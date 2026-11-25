import logging
import requests

from api.endpoints import BASE_URL

logger = logging.getLogger(__name__)

GENERATE_LESSON_ENDPOINT = (
    f"{BASE_URL.rstrip('/')}/api/v1/chapter-study/generate-lesson"
)


def generate_chapter_lesson(
    topic,
    exam="JEE Main",
    subject="Physics",
    chapter="Laws of Motion",
    language="English",
    difficulty="Beginner",
):
    payload = {
        "exam": exam,
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
        "language": language,
        "difficulty": difficulty,
    }

    try:
        response = requests.post(
            GENERATE_LESSON_ENDPOINT,
            json=payload,
            timeout=(15, 360),
        )
        response.raise_for_status()
        return response.json()

    except requests.HTTPError as exc:
        detail = (
            exc.response.text
            if exc.response is not None
            else str(exc)
        )
        logger.exception("Chapter lesson API returned an HTTP error.")
        return {"success": False, "error": detail}

    except requests.RequestException as exc:
        logger.exception("Could not connect to Chapter Learning API.")
        return {"success": False, "error": str(exc)}
