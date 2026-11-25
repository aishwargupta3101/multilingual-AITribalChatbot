import logging

from fastapi import APIRouter, HTTPException

from backend.llm.education_gemini_client import EducationGeminiClient
from backend.schemas.chapter_learning import (
    ChapterLessonRequest,
    ChapterLessonResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chapter-learning",
    tags=["Chapter Learning"],
)


@router.post("/generate-lesson", response_model=ChapterLessonResponse)
async def generate_chapter_lesson(request: ChapterLessonRequest):
    try:
        client = EducationGeminiClient()

        prompt = f"""
You are an experienced Physics educator preparing students for
{request.exam}.

Create a detailed lesson using these details:

Exam: {request.exam}
Subject: {request.subject}
Chapter: {request.chapter}
Topic: {request.topic}
Language: {request.language}
Difficulty: {request.difficulty}

Include:
1. Introduction
2. Learning objectives
3. Fundamental concepts
4. Detailed explanations
5. Important definitions
6. Formulas and derivations
7. Solved numerical examples
8. Common mistakes
9. Five practice questions with answers
10. Revision summary

Explain concepts step by step.
Use correct mathematical notation.
Do not invent official previous-year questions or citations.
Clearly distinguish generated practice questions from actual PYQs.
Write the entire lesson in {request.language}.
Use Markdown formatting.
"""

        lesson = await client.ainvoke(prompt)

        if not lesson or not str(lesson).strip():
            raise HTTPException(
                status_code=502,
                detail="AI provider returned an empty lesson.",
            )

        return ChapterLessonResponse(
            success=True,
            exam=request.exam,
            subject=request.subject,
            chapter=request.chapter,
            topic=request.topic,
            language=request.language,
            lesson=str(lesson),
            message="Chapter lesson generated successfully.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Chapter lesson generation failed.")
        raise HTTPException(
            status_code=502,
            detail="Chapter lesson generation failed. Check backend logs.",
        ) from exc
