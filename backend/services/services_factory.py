from backend.services.chat_service import ChatService
from backend.services.speech_service import SpeechService
from backend.services.translation_service import TranslationService
from backend.services.tts_service import TTSService
from backend.services.health_service import HealthService

class ServiceFactory:
    chat=ChatService()
    speech=SpeechService()
    translation=TranslationService()
    tts=TTSService()
    health=HealthService()