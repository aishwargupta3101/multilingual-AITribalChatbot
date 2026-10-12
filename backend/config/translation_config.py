
"""
Translation Configuration
"""
from pathlib import Path
import torch

class TranslationConfig:
    """Central configuration for multilingual translation."""
    MODEL_NAME = "facebook/nllb-200-distilled-600M"
    INDICTRANS_INDIC_INDIC_MODEL = "ai4bharat/indictrans2-indic-indic-1B"
    INDICTRANS_EN_INDIC_MODEL = "ai4bharat/indictrans2-en-indic-1B"
    INDICTRANS_INDIC_EN_MODEL = "ai4bharat/indictrans2-indic-en-1B"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    USE_FP16 = torch.cuda.is_available()
    MODEL_CACHE_DIR = Path("models/translation")
    INDICTRANS_CACHE_DIR = Path("models/indictrans2")
    MAX_INPUT_LENGTH = 256
    MAX_OUTPUT_LENGTH = 128
    MAX_NEW_TOKEN = 128
    BATCH_SIZE = 1
    TEMPERATURE = 0.2
    USE_INFERENCE_MODE = True
    ENABLE_LOGGING = True
    LOG_TRANSLATIONS = False
    SUPPORTED_FORMATS = ["text"]
    INDICTRANS_NUM_BEAMS = 1
    INDICTRANS_DO_SAMPLE = False