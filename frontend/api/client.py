
import logging
import requests
from api.endpoints import BASE_URL
import json
logger = logging.getLogger(__name__)

class APIClient:

    @staticmethod
    def upload_audio(endpoint, audio_path, language="english"):
        """Upload audio for speech recognition."""
        try:
            url = f"{BASE_URL}{endpoint}"
            with open(audio_path, "rb") as audio_file:
                language = language.lower().strip()
                if language == "manipuri_mtei":
                    language = "manipuri"
                response = requests.post(
                    url,
                    files={
                        "audio": (
                            "user_audio.wav",
                            audio_file,
                            "audio/wav",
                        )
                    },
                    data={"language": language},
                    timeout=300,
                )
            logger.info("Speech API Status: %s", response.status_code)
            logger.info("Speech API Response: %s", response.text[:2000])
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_detail = e.response.text if e.response is not None else str(e)
            logger.exception("Audio upload HTTP error: %s", error_detail)
            return {
                "success": False,
                "error": error_detail,
            }
        except (requests.RequestException, OSError, ValueError) as e:
            logger.exception("Audio upload failed.")
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def translate_audio(
        audio_path,
        input_language="english",
        response_language="hindi",
    ):
        """Upload audio, transcribe it, and translate the transcription."""
        try:
            url = f"{BASE_URL}/api/v1/speech/translate"
            stt_language = input_language.lower().strip()
            if stt_language == "manipuri_mtei":
                stt_language = "manipuri"
            with open(audio_path, "rb") as audio_file:
                response = requests.post(
                    url,
                    files={
                        "audio": (
                            "user_audio.wav",
                            audio_file,
                            "audio/wav",
                        )
                    },
                    data={
                        "input_language": stt_language,
                        "response_language": response_language,
                    },
                    timeout=300,
                )
            logger.info("Audio translation status: %s", response.status_code)
            logger.info("Audio translation response: %s", response.text[:2000])
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_detail = e.response.text if e.response is not None else str(e)
            logger.exception("Audio translation HTTP error: %s", error_detail)
            return {
                "success": False,
                "error": error_detail,
            }
        except (requests.RequestException, OSError, ValueError) as e:
            logger.exception("Audio translation failed.")
            return {
                "success": False,
                "error": str(e),
            }
    @staticmethod
    def text_to_speech(text: str, language: str = "english"):
        """Generate speech and return playable MP3 bytes."""
        try:
            if not text or not text.strip():
                logger.error("TTS skipped: empty text.")
                return None

            # No trailing slash to avoid a 307 redirect.
            url = f"{BASE_URL}/api/v1/tts"

            logger.info("Sending TTS request to: %s", url)

            response = requests.post(
                url,
                json={
                    "text": text.strip(),
                    "language": language,
                },
                timeout=300,
            )

            logger.info("TTS HTTP Status: %s", response.status_code)
            logger.info(
                "TTS Content-Type: %s",
                response.headers.get("Content-Type"),
            )

            response.raise_for_status()

            # The backend returns raw MP3 bytes, not JSON.
            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "audio/mpeg" not in content_type and "audio/mp3" not in content_type:
                logger.error(
                    "TTS did not return audio. Content-Type: %s | Response: %s",
                    content_type,
                    response.text[:1000],
                )
                return None

            audio_bytes = response.content

            if not audio_bytes:
                logger.error("TTS returned an empty audio file.")
                return None

            logger.info(
                "Audio retrieved successfully: %s bytes",
                len(audio_bytes),
            )

            return audio_bytes

        except requests.HTTPError as e:
            logger.exception(
                "TTS HTTP error: %s | Response: %s",
                e,
                e.response.text[:1000]
                if e.response is not None
                else "No response",
            )
            return None

        except requests.RequestException as e:
            logger.exception("TTS request failed: %s", e)
            return None
    @staticmethod
    def manipuri_text_to_speech(
        text: str,
        script: str = "bengali",
        speaker: str = "female"
    ):
        """Generate Manipuri speech using AI4Bharat."""
        try:
            if not text or not text.strip():
                logger.error("Manipuri TTS skipped: empty text.")
                return None
            response = requests.post(
                f"{BASE_URL}/api/v1/manipuri-tts",
                json={
                    "text": text.strip(),
                    "script": script,
                    "speaker": speaker
                },
                timeout=300
            )
            logger.info(
                "Manipuri TTS HTTP Status: %s",
                response.status_code
            )
            logger.info(
                "Manipuri TTS Content-Type: %s",
                response.headers.get("Content-Type")
            )
            response.raise_for_status()
            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()
            if "audio/wav" not in content_type:
                logger.error(
                    "Manipuri TTS did not return WAV. "
                    "Content-Type: %s",
                    content_type
                )
                return None
            audio_bytes = response.content
            if not audio_bytes:
                logger.error(
                    "Manipuri TTS returned empty audio."
                )
                return None
            logger.info(
                "Manipuri TTS audio retrieved: %s bytes",
                len(audio_bytes)
            )
            return audio_bytes
        except requests.HTTPError as e:
            logger.exception(
                "Manipuri TTS HTTP error: %s | Response: %s",
                e,
                e.response.text[:2000]
                if e.response is not None
                else "No response"
            )
            return None
        except requests.RequestException as e:
            logger.exception(
                "Manipuri TTS request failed: %s",
                e
            )
            return None

    @staticmethod
    def chat(
        question: str,
        session_id: str,
        language: str = "english",
    ):
        """Send a question to the Tribal AI chatbot."""
        try:
            url = f"{BASE_URL}/api/v1/chat/"

            logger.info("Sending chat request to: %s", url)
            logger.info("Chat question: %s", question)
            logger.info("Chat language: %s", language)
            logger.info("Chat session ID: %s", session_id)

            response = requests.post(
                url,
                json={
                    "question": question,
                    "session_id": session_id,
                    "language": language,
                },
                timeout=300,
            )

            logger.info(
                "Chat HTTP Status: %s",
                response.status_code,
            )

            response.raise_for_status()

            result = response.json()

            logger.info(
                "CHAT API RESPONSE: %s",
                result,
            )

            return result

        except requests.HTTPError as e:
            logger.exception(
                "Chat HTTP error: %s | Response: %s",
                e,
                e.response.text[:2000]
                if e.response is not None
                else "No response",
            )
            return {
                "success": False,
                "error": f"Chat API error: {str(e)}",
            }

        except (requests.RequestException, ValueError) as e:
            logger.exception("Chat API request failed.")
            return {
                "success": False,
                "error": f"Chat API error: {str(e)}",
            }

    @staticmethod
    def chat_stream(
        question: str,
        session_id: str,
        language: str = "english",
    ):
        """Stream chatbot response tokens from the backend."""
        url = f"{BASE_URL}/api/v1/chat/stream"

        try:
            with requests.post(
                url,
                json={
                    "question": question,
                    "session_id": session_id,
                    "language": language,
                },
                stream=True,
                timeout=(10, 600),
            ) as response:

                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data: "):
                        continue

                    event = json.loads(line[6:])
                    yield event

        except requests.RequestException:
            logger.exception("Chat streaming request failed.")
            raise
        except (ValueError, KeyError):
            logger.exception("Invalid streaming response.")
            raise
    @staticmethod
    def translate_text(
        text: str,
        source_language: str,
        target_language: str,
    ):
        """Translate text between supported languages."""
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/translation/translate",
                json={
                    "text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                },
                timeout=300,
            )

            response.raise_for_status()
            data = response.json()

            return (
                data.get("translated_text")
                or data.get("translation")
                or data.get("text")
                or ""
            )

        except (requests.RequestException, ValueError) as e:
            logger.exception("Text translation failed.")
            return ""


    @staticmethod
    def speech_to_text(audio_bytes, language="english"):
        """Transcribe recorded audio using the speech API."""
        try:
            url = f"{BASE_URL}/api/v1/speech/upload"
            language = language.lower().strip()
            if language == "manipuri_mtei":
                language = "manipuri"
            response = requests.post(
                url,
                files={
                    "audio": (
                        "recording.wav",
                        audio_bytes,
                        "audio/wav",
                    )
                },
                data={"language": language},
                timeout=300,
            )
            logger.info("Speech API Status: %s", response.status_code)
            logger.info("Speech API Response: %s", response.text[:2000])
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_detail = e.response.text if e.response is not None else str(e)
            logger.exception("Speech recognition HTTP error: %s", error_detail)
            return {
                "success": False,
                "error": error_detail,
            }
        except (requests.RequestException, OSError, ValueError) as e:
            logger.exception("Speech recognition failed.")
            return {
                "success": False,
                "error": str(e),
            }