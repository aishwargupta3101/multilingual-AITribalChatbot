from backend.services.chat_service import ChatService
from backend.services.speech_service import SpeechService
from backend.services.translation_service import TranslationService
from backend.services.tts_service import TTSService
from backend.services.health_service import HealthService
from backend.database.mongodb import MongoDB

def get_chat_service()-> ChatService:
    return ChatService()

def get_speech_service() -> SpeechService:
    return SpeechService()

def get_translation_service() -> TranslationService:
    return TranslationService()

def get_tts_service() -> TTSService:
    return TTSService()

def get_health_service() -> HealthService:
    return HealthService()
def get_database():
    return MongoDB()