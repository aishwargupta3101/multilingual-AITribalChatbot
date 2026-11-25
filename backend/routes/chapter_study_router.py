"""AI study tools for Chapter Learning: quizzes, doubt solving and flashcards."""
import json
import re
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.llm.education_gemini_client import EducationGeminiClient
from backend.config.logger import logger

router = APIRouter(prefix="/api/v1/chapter-study", tags=["Chapter Study Tools"])
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = EducationGeminiClient()
    return _llm

class StudyContext(BaseModel):
    exam: Literal["JEE Main", "NEET UG"]
    subject: str = Field(..., min_length=2, max_length=40)
    chapter: str = Field(..., min_length=2, max_length=160)
    topic: str = Field(..., min_length=2, max_length=200)
    language: str = Field(default="English", min_length=2, max_length=50)
    difficulty: str = Field(default="Intermediate", max_length=30)

class QuizRequest(StudyContext):
    question_count: int = Field(default=10, ge=5, le=20)
    quiz_difficulty: str = Field(default="Mixed", max_length=20)

class DoubtRequest(StudyContext):
    question: str = Field(..., min_length=5, max_length=5000)

class FlashcardRequest(StudyContext):
    card_count: int = Field(default=10, ge=5, le=20)
    focus: str = Field(default="Mixed revision", max_length=50)


class LessonGenerationRequest(StudyContext):
    """Context required to generate a personalised Chapter Learning lesson."""
    pass

def _repair_invalid_json_escapes(text: str) -> str:
    """Escape invalid backslashes inside JSON strings, preserving valid JSON escapes."""
    out = []
    in_string = False
    i = 0
    valid_simple = {'"', "\\", "/", "b", "f", "n", "r", "t"}

    while i < len(text):
        ch = text[i]
        if not in_string:
            out.append(ch)
            if ch == '"':
                in_string = True
            i += 1
            continue

        if ch == '"':
            out.append(ch)
            in_string = False
            i += 1
            continue

        if ch != "\\":
            out.append(ch)
            i += 1
            continue

        if i + 1 >= len(text):
            out.append("\\\\")
            i += 1
            continue

        nxt = text[i + 1]
        if nxt == "u" and i + 5 < len(text) and all(
            c in "0123456789abcdefABCDEF" for c in text[i + 2:i + 6]
        ):
            out.append(text[i:i + 6])
            i += 6
            continue

        if nxt in valid_simple:
            # Formula commands such as \\theta, \\times, \\neq and \\frac
            # are literal text, not JSON tab/newline/form-feed escapes.
            if nxt in {"b", "f", "n", "r", "t"} and i + 2 < len(text) and text[i + 2].isalpha():
                out.append("\\\\\\\\")
                i += 1
                continue
            out.append(text[i:i + 2])
            i += 2
            continue

        out.append("\\\\\\\\")
        i += 1

    return "".join(out)


def _extract_json(raw: str) -> Any:
    """Parse JSON directly or inside a Markdown fence; repair formula backslashes."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("The AI response was empty.")

    text = raw.strip()
    text = re.sub(r"^```(?:json)?\\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\\s*```$", "", text)

    candidates = [text]
    first, last = text.find("{"), text.rfind("}")
    if first >= 0 and last > first and text[first:last + 1] != text:
        candidates.append(text[first:last + 1])

    errors = []
    for candidate in candidates:
        for attempt in (candidate, _repair_invalid_json_escapes(candidate)):
            try:
                return json.loads(attempt)
            except json.JSONDecodeError as exc:
                errors.append(f"{exc.msg} at line {exc.lineno}, column {exc.colno}")

    detail = errors[-1] if errors else "No JSON object was found."
    raise ValueError(f"The AI response was not valid JSON: {detail}")

async def _invoke(prompt: str) -> str:
    try:
        result = await get_llm().ainvoke(prompt)
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("The AI provider returned an empty response.")
        return result.strip()
    except Exception as exc:
        logger.exception("Chapter Study Tools AI request failed.")
        if "429" in str(exc):
            raise HTTPException(status_code=429, detail="Education AI is rate-limited. Wait briefly and try again.") from exc
        raise HTTPException(status_code=502, detail="The AI provider is temporarily unavailable. Check backend logs and retry.") from exc

def _context_text(request: StudyContext) -> str:
    return (
        f"Exam: {request.exam}\nSubject: {request.subject}\nChapter: {request.chapter}\n"
        f"Topic: {request.topic}\nStudent language: {request.language}\n"
        f"Level: {request.difficulty}"
    )

def _clean_quiz_questions(data: Any, expected_count: int) -> list[dict]:
    """Validate the quiz structure and reject unfinished or contradictory drafts."""
    questions = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(questions, list) or not questions:
        raise ValueError("Missing questions array.")

    cleaned = []
    draft_markers = (
        "wait,",
        "let's re-evaluate",
        "let's recalculate",
        "let's check",
        "let's make sure",
        "we need to",
        "as an ai",
        "option should be",
        "answer should be",
    )

    for i, item in enumerate(questions[:expected_count], 1):
        if not isinstance(item, dict):
            continue

        options = item.get("options")
        if isinstance(options, list):
            options = {chr(65 + j): value for j, value in enumerate(options[:4])}
        if not isinstance(options, dict):
            continue

        normalized_options = {
            key: str(options.get(key, "")).strip()
            for key in ("A", "B", "C", "D")
        }
        if not all(normalized_options.values()):
            continue

        answer = str(item.get("answer", "")).strip().upper()
        question = str(item.get("question", "")).strip()
        explanation = str(item.get("explanation", "")).strip()

        combined = " ".join([question, *normalized_options.values(), explanation]).lower()
        if any(marker in combined for marker in draft_markers):
            continue
        if answer not in {"A", "B", "C", "D"} or not question or not explanation:
            continue

        cleaned.append({
            "id": str(item.get("id", i)),
            "question": question,
            "options": normalized_options,
            "answer": answer,
            "explanation": explanation,
            "difficulty": str(item.get("difficulty", "Medium")).strip() or "Medium",
        })

    if not cleaned:
        raise ValueError("No valid, complete MCQs were returned.")
    return cleaned


async def _generate_additional_questions(
    request: QuizRequest, existing_questions: list[dict], missing_count: int
) -> list[dict]:
    """Generate only the missing MCQs, avoiding questions already in the quiz."""
    if missing_count <= 0:
        return []

    prompt = f"""
You are an expert {request.exam} question setter. Create exactly {missing_count} NEW
original MCQs for the selected topic. These are AI-created practice questions, NOT PYQs.
Use {request.language}; difficulty: {request.quiz_difficulty}.

Return exactly {missing_count} questions, each with four options A/B/C/D, exactly one
correct answer, and a complete checked explanation. Solve numerical questions fully.
Do not repeat, paraphrase, or reuse any question in the existing quiz below. Do not
include drafting or self-correction language. Return ONLY valid JSON in this schema:
{{"questions":[{{"id":"1","question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"answer":"A","explanation":"...","difficulty":"Medium"}}]}}

Context:
{_context_text(request)}

Existing questions to avoid:
{json.dumps([q["question"] for q in existing_questions], ensure_ascii=False)}
"""
    raw = await _invoke(prompt)
    data = _extract_json(raw)
    additions = _clean_quiz_questions(data, missing_count)

    existing_texts = {" ".join(q["question"].lower().split()) for q in existing_questions}
    unique = []
    for question in additions:
        key = " ".join(question["question"].lower().split())
        if key not in existing_texts:
            existing_texts.add(key)
            unique.append(question)
    if len(unique) != missing_count:
        raise ValueError(
            f"AI supplied {len(unique)} unique additional questions; expected {missing_count}."
        )
    return unique


@router.post("/quiz")
async def generate_quiz(request: QuizRequest):
    generation_prompt = f"""
You are an expert {request.exam} question setter.
Create exactly {request.question_count} original MCQs for this topic. These are AI-created
practice questions, NOT previous-year questions. Use {request.language}.
Requested difficulty: {request.quiz_difficulty}.

Requirements:
- Exactly four options A, B, C and D, with one unambiguously correct answer.
- Questions must test the stated topic and suit the exam.
- For numerical questions, solve the problem fully before selecting the answer.
- Ensure the answer key matches one of the options.
- Explanations must contain only the finished solution. Never include internal drafting,
  self-correction, "wait", "let me recalculate", or discussion of changing the answer.
- Avoid ambiguous wording, missing data, malformed units and duplicate options.
- Do not claim a question appeared in a real exam.

Return ONLY valid JSON:
{{
 "questions":[
  {{"id":"1","question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"answer":"A","explanation":"Complete checked solution","difficulty":"Medium"}}
 ]
}}

Context:
{_context_text(request)}
"""
    raw = await _invoke(generation_prompt)

    try:
        generated_data = _extract_json(raw)
        generated_questions = _clean_quiz_questions(generated_data, request.question_count)
    except Exception as exc:
        logger.exception(
            "Initial quiz generation failed validation. Raw response length: %s characters.",
            len(raw),
        )
        raise HTTPException(
            status_code=502,
            detail="The generated quiz was incomplete or malformed. Please regenerate.",
        ) from exc

    # Top up an undersized first response before independent verification.
    if len(generated_questions) < request.question_count:
        try:
            missing = request.question_count - len(generated_questions)
            generated_questions.extend(
                await _generate_additional_questions(request, generated_questions, missing)
            )
        except Exception as exc:
            logger.exception("Could not generate the missing quiz questions.")
            raise HTTPException(
                status_code=502,
                detail=(
                    f"The AI generated only {len(generated_questions)} of "
                    f"{request.question_count} questions and could not safely generate the missing ones. "
                    "Please regenerate."
                ),
            ) from exc

    # Independent second pass: recompute answers and repair the question set.
    verification_prompt = f"""
You are an independent examiner and solution verifier for {request.exam}.
Audit every MCQ below independently. Do NOT trust its supplied answer key or explanation.
For each question:
1. Solve it from the question statement, independently and step by step.
2. Check whether all four options are valid and exactly one is correct.
3. For numerical questions, recompute all arithmetic and units.
4. Compare your independently obtained result with the options.
5. Set "answer" to the option that is actually correct.
6. Rewrite the explanation as a concise, complete derivation that supports that answer.
7. If a question is ambiguous, underspecified, has no correct option, has multiple correct
   options, or cannot be reliably solved, REPLACE it with a new unambiguous question on
   the same topic and difficulty, then solve and verify the replacement.
8. Remove unfinished reasoning, contradictory statements, answer-key deliberation and
   phrases such as "wait", "let's recalculate" or "check options".
9. Keep the same number of questions and four options labelled A/B/C/D.

Return ONLY valid JSON in exactly this schema:
{{
 "questions":[
  {{"id":"1","question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"answer":"A","explanation":"Independently checked complete solution","difficulty":"Medium"}}
 ]
}}

Context:
{_context_text(request)}

MCQs to audit:
{json.dumps({"questions": generated_questions}, ensure_ascii=False)}
"""
    verification_raw = await _invoke(verification_prompt)

    try:
        verified_data = _extract_json(verification_raw)
        verified_questions = _clean_quiz_questions(verified_data, request.question_count)
        if len(verified_questions) < request.question_count:
            missing = request.question_count - len(verified_questions)
            supplemental = await _generate_additional_questions(
                request, verified_questions, missing
            )
            supplemental_prompt = f"""
You are an independent {request.exam} examiner. Independently solve and verify every
MCQ below. Check that exactly one option is correct, recompute all calculations and
units, and rewrite the explanation as a complete solution. Replace any ambiguous or
incorrect question with a clear one on the same topic. Return exactly {missing}
verified questions in JSON using the same schema. Return ONLY JSON.
Context:
{_context_text(request)}
Questions:
{json.dumps({"questions": supplemental}, ensure_ascii=False)}
"""
            supplemental_raw = await _invoke(supplemental_prompt)
            supplemental_data = _extract_json(supplemental_raw)
            supplemental_verified = _clean_quiz_questions(supplemental_data, missing)
            if len(supplemental_verified) != missing:
                raise ValueError(
                    f"Supplemental verification returned {len(supplemental_verified)} questions; "
                    f"expected {missing}."
                )
            verified_questions.extend(supplemental_verified)

        if len(verified_questions) != request.question_count:
            raise ValueError(
                f"Final quiz contains {len(verified_questions)} questions; "
                f"expected exactly {request.question_count}."
            )

        # Normalise IDs and reject duplicate question statements before returning.
        seen_questions = set()
        for index, question in enumerate(verified_questions, start=1):
            question["id"] = str(index)
            normalised_text = " ".join(question["question"].lower().split())
            if normalised_text in seen_questions:
                raise ValueError("The verified quiz contains duplicate questions.")
            seen_questions.add(normalised_text)
    except Exception as exc:
        logger.exception(
            "Independent quiz verification failed. Response length: %s characters.",
            len(verification_raw),
        )
        raise HTTPException(
            status_code=502,
            detail="The quiz was generated, but independent answer verification failed. Please retry.",
        ) from exc

    return {
        "success": True,
        "context": request.model_dump(exclude={"question_count", "quiz_difficulty"}),
        "questions": verified_questions,
        "verification_status": "independently_ai_reviewed",
        "verification_note": (
            "Questions and answer keys received a second AI review. "
            "AI review reduces errors but does not guarantee correctness; "
            "students should cross-check important answers with trusted textbooks or official keys."
        ),
    }

@router.post("/doubt")
async def solve_doubt(request: DoubtRequest):
    prompt = f"""
You are a patient, precise {request.exam} tutor. Answer the student's question in
{request.language}. Focus on the selected topic. Explain the concept first, then solve
step by step, show formulas and units where relevant, and finish with a short final
answer and one useful learning tip. If information is missing or the question is
ambiguous, state the assumption rather than inventing details. Do not claim certainty
when the problem cannot be solved from the supplied information.
{_context_text(request)}

STUDENT QUESTION:
{request.question}
"""
    answer = await _invoke(prompt)
    return {"success": True, "answer": answer}

@router.post("/flashcards")
async def generate_flashcards(request: FlashcardRequest):
    prompt = f"""
Create exactly {request.card_count} accurate study flashcards for the selected topic.
Write in {request.language}. Focus: {request.focus}. Match {request.exam} preparation
level. Each front should ask one clear question; each back should give a concise but
useful answer, definition, formula or fact. Avoid duplicates. Check all formulas and
facts. Return ONLY valid JSON:
{{"cards":[{{"front":"Question","back":"Answer"}}]}}
Context:
{_context_text(request)}
"""
    raw = await _invoke(prompt)
    try:
        data = _extract_json(raw)
        cards = data.get("cards") if isinstance(data, dict) else None
        if not isinstance(cards, list):
            raise ValueError("Missing cards array.")
        cleaned = [
            {"front": str(card.get("front", "")).strip(), "back": str(card.get("back", "")).strip()}
            for card in cards[:request.card_count]
            if isinstance(card, dict) and str(card.get("front", "")).strip() and str(card.get("back", "")).strip()
        ]
        if not cleaned:
            raise ValueError("No usable flashcards were returned.")
        return {"success": True, "cards": cleaned}
    except Exception as exc:
        logger.exception("Could not parse generated flashcards. Raw response length: %s characters.", len(raw))
        raise HTTPException(status_code=502, detail="The AI response could not be converted into flashcards. Please regenerate.") from exc

@router.post("/generate-lesson")
async def generate_chapter_lesson(request: LessonGenerationRequest):
    """Generate a structured lesson for the selected exam, chapter and topic."""
    prompt = f"""
You are an expert, patient tutor preparing a lesson for {request.exam}.

Create a complete, accurate and student-friendly lesson for the following selection:
{_context_text(request)}

Write entirely in {request.language}. Adapt the vocabulary, pace and depth to the
student's {request.difficulty} level. Keep the explanation focused on the selected
topic and suitable for the requested examination.

Use clear Markdown headings and include:
1. Topic overview and why it matters
2. Learning objectives
3. Prerequisite knowledge (briefly)
4. Detailed concept-by-concept explanation
5. Important definitions, laws and principles
6. Relevant formulas, with symbol meanings and SI units
7. At least two worked examples where suitable for the subject
8. Common misconceptions and mistakes
9. Exam-oriented tips (without claiming predictions)
10. Quick revision summary
11. Five practice questions with answers and concise explanations

For Biology and other primarily conceptual topics, use suitable examples instead
of forcing mathematical formulas. Do not invent facts, citations or PYQ claims.
Return the lesson as readable Markdown, not JSON.
"""
    lesson = await _invoke(prompt)
    return {
        "success": True,
        "lesson": lesson,
        "exam": request.exam,
        "subject": request.subject,
        "chapter": request.chapter,
        "topic": request.topic,
        "language": request.language,
        "difficulty": request.difficulty,
    }

