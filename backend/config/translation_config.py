"""
Translation Configuration
"""
from pathlib import Path
import torch

class TranslationConfig:
    """
    Configuration for translation module.
    """
    MODEL_NAME = "facebook/nllb-200-distilled-600M"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    MODEL_CACHE_DIR = Path("models/translation")
    MAX_INPUT_LENGTH = 256
    MAX_OUTPUT_LENGTH = 128
    MAX_NEW_TOKEN = 128
    BATCH_SIZE = 4
    TEMPERATURE = 0.2
    ENABLE_LOGGING = True
    LOG_TRANSLATIONS = False
    SUPPORTED_FORMATS = [
        "text"
    ]