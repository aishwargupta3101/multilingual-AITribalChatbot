from pydantic import BaseModel, Field


class ChapterLessonRequest(BaseModel):
    exam: str = "JEE Main"
    subject: str = "Physics"
    chapter: str = "Laws of Motion"
    topic: str = Field(min_length=2, max_length=200)
    language: str = "English"
    difficulty: str = "Beginner"


class ChapterLessonResponse(BaseModel):
    success: bool
    exam: str
    subject: str
    chapter: str
    topic: str
    language: str
    lesson: str
    message: str
