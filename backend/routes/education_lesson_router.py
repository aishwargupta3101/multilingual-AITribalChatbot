from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import asyncio
from backend.services.pdf_extraction_service import extract_text_from_pdf
from backend.llm.education_gemini_client import EducationGeminiClient
from backend.services.translation_service import translation_service
from backend.config.logger import logger

router = APIRouter(prefix="/api/v1/education", tags=["Education Assistant"])
_education_llm = None

# Keep each prompt manageable while covering the complete extracted chapter.
LESSON_CHUNK_CHARS = 7000
ASSESSMENT_CHUNK_CHARS = 9000
MAX_SOURCE_CHARS = 60000


class LessonRequest(BaseModel):
    extracted_text: str = Field(..., min_length=1)
    grade: str = "6"
    subject: str = "English"
    language: str = "English"
    learning_objectives: str = ""


def get_education_llm():
    global _education_llm
    if _education_llm is None:
        _education_llm = EducationGeminiClient()
    return _education_llm


def _split_text(text: str, chunk_size: int):
    """Split on paragraph/sentence boundaries where possible, without dropping text."""
    text = text.strip()
    chunks = []
    while text:
        if len(text) <= chunk_size:
            chunks.append(text)
            break
        cut = text.rfind("\\n", 0, chunk_size)
        if cut < chunk_size // 2:
            cut = text.rfind(". ", 0, chunk_size)
        if cut < chunk_size // 2:
            cut = chunk_size
        else:
            cut += 1
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    return chunks


async def _generate_complete_lesson(llm, text, grade, subject, objectives):
    chunks = _split_text(text[:MAX_SOURCE_CHARS], LESSON_CHUNK_CHARS)
    section_results = []
    for index, chunk in enumerate(chunks, start=1):
        prompt = f"""
You are preparing a comprehensive chapter lesson for Grade {grade}, subject {subject}.
This is source part {index} of {len(chunks)}. Extract and explain ALL important
ideas, events, concepts, examples, vocabulary, and facts in this part. Do not
pretend this part is the whole chapter. Use only the supplied source.
Learning objectives: {objectives or "Derive suitable objectives from the full chapter."}
Write in English, in clear age-appropriate language. Return concise structured notes
with a part heading and the source-specific details.

SOURCE PART:
{chunk}
"""
        part = await llm.ainvoke(prompt)
        if not isinstance(part, str) or not part.strip():
            raise RuntimeError(f"Gemini returned an empty lesson segment ({index}).")
        section_results.append(part.strip())

    merge_prompt = f"""
Combine the following notes from all parts of one textbook chapter into ONE
complete, coherent, age-appropriate lesson for Grade {grade}, subject {subject}.
Do not omit important content from any part. Remove only duplicate explanations.
Use ONLY the notes below. Include:
1. Chapter title
2. Learning objectives
3. Complete explanation organized by topic/sequence
4. Key terms and meanings
5. Important examples/details from the chapter
6. Quick recap
7. Five student questions
Learning objectives requested: {objectives or "Derive from the chapter."}

CHAPTER PART NOTES:
{chr(10).join(section_results)}
"""
    lesson = await llm.ainvoke(merge_prompt)
    if not isinstance(lesson, str) or not lesson.strip():
        raise RuntimeError("Gemini returned an empty merged lesson.")
    return lesson.strip()


@router.post("/generate-lesson")
async def generate_lesson(request: LessonRequest):
    textbook_text = request.extracted_text.strip()
    if not textbook_text:
        raise HTTPException(status_code=400, detail="No textbook text was provided.")
    if len(textbook_text) > MAX_SOURCE_CHARS:
        logger.warning("Education source text capped from %s to %s chars", len(textbook_text), MAX_SOURCE_CHARS)
        textbook_text = textbook_text[:MAX_SOURCE_CHARS]

    try:
        llm = get_education_llm()
        lesson_english = await _generate_complete_lesson(
            llm, textbook_text, request.grade, request.subject, request.learning_objectives
        )
        target_language = request.language.strip().lower()
        if target_language in ("english", "en"):
            lesson, output_language = lesson_english, "English"
        else:
            lesson = await asyncio.to_thread(
                translation_service.translate,
                text=lesson_english,
                source_language="english",
                target_language=target_language,
            )
            output_language = request.language
        return {
            "status": "success", "grade": request.grade, "subject": request.subject,
            "language": output_language, "lesson": lesson, "lesson_english": lesson_english,
            "source_characters_used": len(textbook_text),
        }
    except Exception as exc:
        if getattr(getattr(exc, "response", None), "status_code", None) == 429:
            raise HTTPException(status_code=429, detail="Education AI is temporarily rate-limited. Please wait and try again.") from exc
        logger.exception("Lesson generation or translation failed.")
        raise HTTPException(status_code=500, detail="Could not generate or translate the lesson. Check backend logs.") from exc


@router.post("/upload-and-generate-lesson")
async def upload_and_generate_lesson(
    file: UploadFile = File(...), grade: str = "6", subject: str = "English",
    language: str = "English", learning_objectives: str = "",
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF textbook.")
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")
    try:
        extraction = await asyncio.to_thread(extract_text_from_pdf, pdf_bytes)
        if isinstance(extraction, dict):
            extracted_text = extraction.get("extracted_text") or extraction.get("text") or ""
            page_count = extraction.get("page_count", 0)
        elif isinstance(extraction, (tuple, list)):
            extracted_text = extraction[0] if extraction else ""
            page_count = extraction[1] if len(extraction) > 1 else 0
        else:
            extracted_text, page_count = str(extraction), 0
        if not isinstance(extracted_text, str):
            extracted_text = str(extracted_text)
        if len(extracted_text.strip()) < 50:
            raise HTTPException(status_code=422, detail="Not enough text could be extracted from this PDF. It may be scanned or image-based.")
        lesson_result = await generate_lesson(LessonRequest(
            extracted_text=extracted_text, grade=grade, subject=subject,
            language=language, learning_objectives=learning_objectives,
        ))
        return {**lesson_result, "filename": file.filename, "page_count": page_count,
                "extracted_characters": len(extracted_text)}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("PDF-to-lesson workflow failed.")
        raise HTTPException(status_code=500, detail="Could not extract the PDF or generate the lesson.") from exc
    finally:
        await file.close()


class QuizWorksheetRequest(BaseModel):
    extracted_text: str = Field(..., min_length=50)
    grade: str = "6"
    subject: str = "English"
    language: str = "English"
    question_count: int = Field(default=8, ge=1, le=20)


@router.post("/generate-quiz-worksheet")
async def generate_quiz_worksheet(request: QuizWorksheetRequest):
    source = request.extracted_text.strip()[:MAX_SOURCE_CHARS]
    chunks = _split_text(source, ASSESSMENT_CHUNK_CHARS)
    try:
        llm = get_education_llm()
        source_notes = []
        for index, chunk in enumerate(chunks, start=1):
            prompt = f"""
For Grade {request.grade} {request.subject}, extract the key facts, concepts,
vocabulary, events, and examples from source part {index}/{len(chunks)}.
Use only this source part. Be thorough but concise. Output language: English.

SOURCE:
{chunk}
"""
            notes = await llm.ainvoke(prompt)
            if not isinstance(notes, str) or not notes.strip():
                raise RuntimeError(f"Gemini returned empty assessment source notes ({index}).")
            source_notes.append(notes.strip())

        prompt = f"""
Create complete assessment materials for Grade {request.grade}, subject {request.subject},
based on ALL chapter notes below. Output language: {request.language}.
Create exactly {request.question_count} distinct numbered quiz questions, mixing
multiple choice, true/false, and short answer. Include an answer key with one answer
for every question. Then create a worksheet with vocabulary, comprehension, and at
least one creative/application activity, followed by brief teacher notes.
Ensure the worksheet covers the chapter broadly, not just its opening section.
Do not add unsupported facts. Keep the answer key separate from student questions.

CHAPTER NOTES:
{chr(10).join(source_notes)}
"""
        result = await llm.ainvoke(prompt)
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("Education Gemini returned an empty assessment.")
        return {"status": "success", "grade": request.grade, "subject": request.subject,
                "language": request.language, "assessment": result.strip(),
                "source_characters_used": len(source)}
    except Exception as exc:
        if getattr(getattr(exc, "response", None), "status_code", None) == 429:
            raise HTTPException(status_code=429, detail="Education AI is temporarily rate-limited. Please wait and try again.") from exc
        logger.exception("Quiz and worksheet generation failed.")
        raise HTTPException(status_code=500, detail="Could not generate the quiz and worksheet.") from exc
