
import os
BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).strip().rstrip("/")

HEALTH_ENDPOINT = "/api/v1/health"
CHAT_ENDPOINT = "/api/v1/chat/"
SPEECH_ENDPOINT = "/api/v1/speech"
TRANSLATION_ENDPOINT = "/api/v1/translation"
TTS_ENDPOINT = "/api/v1/tts"
UPLOAD_ENDPOINT = "/api/v1/upload/"
SPEECH_UPLOAD_ENDPOINT = "/api/v1/speech/upload"

VIDEO_LEARNING_ENDPOINT = "/api/v1/video-learning/lesson"
EDUCATION_UPLOAD_ENDPOINT = "/api/v1/education/upload"
EDUCATION_LESSON_ENDPOINT = "/api/v1/education/generate-lesson"
EDUCATION_ASSESSMENT_ENDPOINT = "/api/v1/education/generate-quiz-worksheet"
