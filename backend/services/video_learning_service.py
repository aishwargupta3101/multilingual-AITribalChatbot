"""Video-to-learning service. Kept separate from the existing chat pipeline."""
import asyncio
import re
from urllib.parse import urlparse, parse_qs

from backend.config.logger import logger
from backend.llm.llama_service import llama_service
from backend.services.translation_service import translation_service
from backend.database.connection import mongodb


class VideoLearningError(ValueError):
    pass


class VideoLearningRateLimitError(VideoLearningError):
    """The AI provider quota/rate limit prevents lesson generation right now."""
    pass


# Limits concurrent lesson jobs within one backend process. For multiple workers/instances,
# replace this with a Redis-backed distributed queue/rate limiter before production rollout.
_VIDEO_LESSON_SEMAPHORE = asyncio.Semaphore(1)
_VIDEO_LESSON_CACHE_COLLECTION = "video_lessons"
_VIDEO_LESSON_CACHE_VERSION = 1


async def _get_cached_lesson(video_id: str, level: str, language: str):
    """Return a previously completed lesson, if MongoDB is available."""
    database = mongodb.database
    if database is None:
        return None
    try:
        document = await database[_VIDEO_LESSON_CACHE_COLLECTION].find_one({
            "video_id": video_id,
            "level": level,
            "language": language,
            "cache_version": _VIDEO_LESSON_CACHE_VERSION,
        }, {"_id": 0, "result": 1})
        if document and isinstance(document.get("result"), dict):
            logger.info("Video lesson cache hit | video_id=%s | level=%s | language=%s",
                        video_id, level, language)
            return document["result"]
    except Exception:
        # Caching must never break lesson generation if MongoDB cache access fails.
        logger.exception("Video lesson cache lookup failed | video_id=%s", video_id)
    return None


async def _save_cached_lesson(video_id: str, level: str, language: str, result: dict):
    """Persist a completed lesson; failures are logged but don't fail the user request."""
    database = mongodb.database
    if database is None:
        return
    try:
        await database[_VIDEO_LESSON_CACHE_COLLECTION].update_one(
            {
                "video_id": video_id,
                "level": level,
                "language": language,
                "cache_version": _VIDEO_LESSON_CACHE_VERSION,
            },
            {"$set": {
                "video_id": video_id,
                "level": level,
                "language": language,
                "cache_version": _VIDEO_LESSON_CACHE_VERSION,
                "result": result,
            }},
            upsert=True,
        )
        logger.info("Video lesson cached | video_id=%s | level=%s | language=%s",
                    video_id, level, language)
    except Exception:
        # Do not discard a successfully generated lesson because cache persistence failed.
        logger.exception("Video lesson cache save failed | video_id=%s", video_id)


def extract_youtube_video_id(url: str) -> str:
    """Validate common YouTube URL forms and return the 11-character video ID."""
    value = (url or "").strip()
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    video_id = ""
    if host in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/embed/", "/shorts/", "/live/")):
            pieces = parsed.path.strip("/").split("/")
            video_id = pieces[1] if len(pieces) > 1 else ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise VideoLearningError("Enter a valid public YouTube video URL.")
    return video_id


def _fetch_transcript(video_id: str):
    """Fetch captions, preferring English but falling back to Hindi and other languages."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise VideoLearningError(
            "YouTube transcript support is not installed yet. Add youtube-transcript-api "
            "to your backend requirements, then redeploy/restart the backend."
        ) from exc

    # Try a broad set of transcript language codes. These are SOURCE caption
    # languages; the lesson output language is selected separately in the UI.
    # YouTube only exposes languages that the individual video actually provides.
    preferred_languages = [
        "en", "hi", "mni", "as", "bn", "brx", "doi", "gu", "kn", "ks",
        "gom", "mai", "ml", "mr", "ne", "or", "pa", "sa", "sat", "sd",
        "ta", "te", "ur",
    ]
    snippets = None
    try:
        api = YouTubeTranscriptApi()
        if hasattr(api, "list"):
            transcript_list = api.list(video_id)
            selected = transcript_list.find_transcript(preferred_languages)
            fetched = selected.fetch()
            snippets = [
                {"text": getattr(item, "text", ""),
                 "start": getattr(item, "start", 0),
                 "duration": getattr(item, "duration", 0)}
                for item in fetched
            ]
        elif hasattr(YouTubeTranscriptApi, "get_transcript"):
            # Compatibility with older versions; pass fallback languages in priority order.
            snippets = YouTubeTranscriptApi.get_transcript(
                video_id, languages=preferred_languages
            )
        else:
            fetched = api.fetch(video_id, languages=preferred_languages)
            snippets = [
                {"text": getattr(item, "text", ""),
                 "start": getattr(item, "start", 0),
                 "duration": getattr(item, "duration", 0)}
                for item in fetched
            ]
    except Exception as exc:
        logger.exception("YouTube transcript retrieval failed | video_id=%s", video_id)
        raise VideoLearningError(
            "I couldn't retrieve captions in the preferred languages. Caption availability "
            "depends on the individual YouTube video; try a public video with captions enabled. "
            "This feature currently builds lessons from captions/transcripts, not visual-only "
            "content such as diagrams or demonstrations that are not described in speech."
        ) from exc

    cleaned = []
    for item in snippets or []:
        # New API returns snippet objects; old API returns dictionaries.
        if isinstance(item, dict):
            raw_text = item.get("text", "")
            raw_start = item.get("start", 0)
        else:
            raw_text = getattr(item, "text", "")
            raw_start = getattr(item, "start", 0)
        text = str(raw_text).replace("\n", " ").strip()
        if not text:
            continue
        start = max(0, int(float(raw_start)))
        timestamp = f"{start // 60:02d}:{start % 60:02d}"
        cleaned.append({"start": start, "timestamp": timestamp, "text": text})
    if not cleaned:
        raise VideoLearningError("The video transcript was empty.")
    # Keep substantially more of the source so long videos are not silently reduced
    # to only their opening portion. Per-section generation below keeps each model
    # request bounded even when the overall transcript is long.
    transcript_text = "\n".join(f"[{x['timestamp']}] {x['text']}" for x in cleaned)
    max_transcript_chars = 45000
    if len(transcript_text) > max_transcript_chars:
        logger.warning(
            "Video transcript exceeds safety cap | video_id=%s | chars=%s | cap=%s",
            video_id, len(transcript_text), max_transcript_chars
        )
        transcript_text = transcript_text[:max_transcript_chars]
        transcript_text += "\n[WARNING: Transcript exceeded the current processing limit; later captions were omitted.]"
    return cleaned, transcript_text


def _split_transcript(transcript_text: str, max_chars: int = 4500):
    """Split timestamped captions into small, chronological chunks for API limits."""
    lines = transcript_text.splitlines()
    chunks = []
    current = []
    current_size = 0
    for line in lines:
        # Keep each caption line intact where possible so timestamps remain attached.
        if current and current_size + len(line) + 1 > max_chars:
            chunks.append("\n".join(current))
            current = []
            current_size = 0
        if len(line) > max_chars:
            # Defensive handling for an unusually long single caption line.
            for offset in range(0, len(line), max_chars):
                piece = line[offset:offset + max_chars]
                if current:
                    chunks.append("\n".join(current))
                    current = []
                    current_size = 0
                chunks.append(piece)
            continue
        current.append(line)
        current_size += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


def _retry_delay_seconds(headers, attempt: int) -> float:
    """Choose a bounded wait using Groq's retry/reset headers when available."""
    headers = headers or {}
    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after:
        # Retry-After is usually seconds; accept common values such as "2s".
        value = str(retry_after).strip().lower()
        if value.endswith("s"):
            value = value[:-1].strip()
        try:
            return min(60.0, max(1.0, float(value)))
        except (TypeError, ValueError):
            pass

    # Groq reset headers can be durations such as "1.5s" or "2m".
    reset_values = [
        headers.get("x-ratelimit-reset-requests"),
        headers.get("x-ratelimit-reset-tokens"),
    ]
    parsed_resets = []
    for raw in reset_values:
        if not raw:
            continue
        value = str(raw).strip().lower()
        try:
            if value.endswith("ms"):
                seconds = float(value[:-2]) / 1000.0
            elif value.endswith("s"):
                seconds = float(value[:-1])
            elif value.endswith("m"):
                seconds = float(value[:-1]) * 60.0
            else:
                seconds = float(value)
            if seconds >= 0:
                parsed_resets.append(seconds)
        except (TypeError, ValueError):
            continue
    if parsed_resets:
        return min(60.0, max(1.0, max(parsed_resets)))

    return min(30.0, 5.0 * (2 ** attempt))


def _is_daily_quota_error(exc: Exception) -> bool:
    """Inspect the provider response body without logging secrets."""
    response = getattr(exc, "response", None)
    body = ""
    if response is not None:
        try:
            body = response.text[:3000].lower()
        except Exception:
            body = ""
    combined = f"{exc} {body}".lower()
    return any(term in combined for term in (
        "tokens per day", "token per day", "daily limit", "daily quota",
        "tokens_per_day", "rate_limit_exceeded", "quota exceeded",
    ))


async def _generate_with_rate_limit_retry(messages, *, max_attempts: int = 2):
    """Retry short-lived 429s only; never waste retries on an exhausted daily quota."""
    for attempt in range(max_attempts):
        try:
            return await llama_service.generate_response(messages)
        except Exception as exc:
            response = getattr(exc, "response", None)
            status_code = getattr(response, "status_code", None)
            if status_code != 429 or _is_daily_quota_error(exc) or attempt == max_attempts - 1:
                raise

            headers = getattr(response, "headers", {}) or {}
            delay = _retry_delay_seconds(headers, attempt)
            logger.warning(
                f"Temporary Groq rate limit during video lesson; retrying in {delay:.1f} "
                f"seconds (attempt {attempt + 1}/{max_attempts})."
            )
            await asyncio.sleep(delay)


class VideoLearningService:
    async def create_lesson(self, url: str, level: str = "beginner", output_language: str = "english"):
        # Serialize lesson generation within this process to avoid concurrent bursts to Groq.
        async with _VIDEO_LESSON_SEMAPHORE:
            return await self._create_lesson_locked(url, level, output_language)

    async def _create_lesson_locked(self, url: str, level: str = "beginner", output_language: str = "english"):
        video_id = extract_youtube_video_id(url)
        level = level if level in {"beginner", "college", "advanced"} else "beginner"
        normalized_language = translation_service.normalize_language(output_language or "english")
        logger.info("Video learning started | video_id=%s | level=%s | language=%s",
                    video_id, level, normalized_language)

        # Check cache before retrieving captions or calling the AI provider.
        cached = await _get_cached_lesson(video_id, level, normalized_language)
        if cached is not None:
            return cached

        transcript, transcript_text = _fetch_transcript(video_id)

        # Generate detailed teaching sections per chunk, then assemble locally.
        # This avoids a single huge final request and preserves all sections.
        chunks = _split_transcript(transcript_text, max_chars=4000)
        lesson_sections = []
        try:
            for index, chunk in enumerate(chunks, start=1):
                chunk_prompt = f"""You are Tribal LearnAI, an expert teacher creating comprehensive study notes from a YouTube lesson.

Learner level: {level}
This is transcript section {index} of {len(chunks)}. Explain this section in detail and preserve its place in the video.

Requirements:
- Write a descriptive heading for the concepts covered in this section.
- Explain each concept step by step in plain language appropriate to the learner level.
- Define technical terms when they first appear.
- Include concrete examples, worked examples, analogies, or pseudocode when relevant to the transcript.
- Preserve important facts, procedures, comparisons, caveats, and timestamps in [MM:SS] format.
- Do not invent details that are not supported by the captions.
- Do not just summarize. Teach the material so a student can study without watching the video.
- Do not claim to see slides, figures, or demonstrations that are not described by captions.
- Do not include a transcript or repeat captions verbatim.
- Aim for 500-800 words when the source contains enough distinct material; be shorter only when the source section is genuinely brief.
- Cover every distinct concept in this caption section, including examples, transitions, caveats, and demonstrations described in speech.
- Add a short "Key takeaways" subsection for this section.
- Add practice questions specific to this section, with concise answer keys, when the captions provide enough information.
- Avoid padding or repeating the same idea to reach a word count; detail must come from the captions or be clearly labelled as a simple illustrative example.
- Use Markdown headings, lists, tables, and code blocks when they improve learning.

CAPTIONS FOR THIS SECTION:
{chunk}

Return only the detailed teaching section, not a summary of the entire video."""
                section = await _generate_with_rate_limit_retry([
                    {"role": "user", "content": chunk_prompt}
                ])
                section = str(section or "").strip()
                if not section:
                    raise VideoLearningError(
                        f"The AI model returned an empty explanation for section {index}. Please retry."
                    )
                lesson_sections.append(section)
                if index < len(chunks):
                    await asyncio.sleep(2.0)

            lesson = (
                "# Video Lesson: Comprehensive Study Notes\n\n"
                f"**Level:** {level.title()}  \n"
                f"**Source video:** https://www.youtube.com/watch?v={video_id}\n\n"
                "## Learning overview\n\n"
                f"These notes were built from {len(transcript)} caption segments across {len(chunks)} chronological sections. The notes aim to explain the available caption content in video order; details not stated in captions are not assumed.\n\n"
                + "\n\n---\n\n".join(lesson_sections)
                + "\n\n## Self-check questions\n\n"
                "1. What are the main concepts explained in this lesson?\n"
                "2. Define the key technical terms introduced.\n"
                "3. Explain one process or idea step by step.\n"
                "4. Give an example applying one of the concepts.\n"
                "5. Which details would you revisit in the original video?\n\n"
                "## Answer guidance\n\n"
                "Use the explanations and examples above. For details not covered by the captions, revisit the linked video rather than guessing."
            )
        except VideoLearningError:
            raise
        except Exception as exc:
            logger.exception("Video lesson generation failed | video_id=%s", video_id)
            response = getattr(exc, "response", None)
            status_code = getattr(response, "status_code", None)
            if status_code == 429:
                headers = getattr(response, "headers", {}) or {}
                reset_requests = headers.get("x-ratelimit-reset-requests")
                reset_tokens = headers.get("x-ratelimit-reset-tokens")
                if _is_daily_quota_error(exc):
                    raise VideoLearningRateLimitError(
                        "Video lesson generation is temporarily unavailable because the AI "
                        "provider's daily quota is exhausted. No more retries were attempted. "
                        "Please try after the provider's quota resets, or contact the platform "
                        "administrator."
                    ) from exc
                reset_hint = ", ".join(
                    f"{name}={value}"
                    for name, value in (
                        ("request reset", reset_requests),
                        ("token reset", reset_tokens),
                    ) if value
                )
                raise VideoLearningRateLimitError(
                    "The AI provider is temporarily rate-limiting lesson generation. "
                    "Please wait before trying again."
                    + (f" Provider reset hint: {reset_hint}." if reset_hint else "")
                ) from exc
            elif status_code == 413:
                message = "The AI provider rejected a request that was too large. Try a shorter video."
            else:
                message = "The AI model couldn't generate one of the lesson sections. Please try again."
            raise VideoLearningError(message) from exc

        if not lesson or not str(lesson).strip():
            raise VideoLearningError("The AI model returned an empty lesson. Please try again.")
        lesson = str(lesson).strip()
        if normalized_language != "english":
            try:
                lesson = translation_service.translate_response(
                    text=lesson, target_language=normalized_language, source_language="english"
                )
            except Exception:
                logger.exception("Video lesson translation failed | language=%s", normalized_language)
                raise VideoLearningError(
                    "The lesson was generated, but translation to the selected language failed. Try English or retry later."
                )
        result = {
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "transcript_segments": len(transcript),
            "transcript_characters_used": len(transcript_text),
            "transcript_chunks_processed": len(chunks),
            "transcript_start_timestamp": transcript[0]["timestamp"] if transcript else None,
            "transcript_end_timestamp": transcript[-1]["timestamp"] if transcript else None,
            "transcript_truncated": len(transcript_text) >= 45000,
            "lesson": lesson,
            "language": normalized_language,
        }
        await _save_cached_lesson(video_id, level, normalized_language, result)
        return result

video_learning_service = VideoLearningService()
