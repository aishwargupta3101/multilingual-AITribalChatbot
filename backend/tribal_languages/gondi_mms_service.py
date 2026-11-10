"""Experimental Meta MMS ASR and Adilabad Gondi TTS services.

Model loading is lazy to avoid downloading multi-gigabyte checkpoints during
normal backend startup. The official wsg MMS TTS tokenizer uses Telugu script;
AdiBhasha's translation data uses Devanagari, so TTS input is transliterated
with a conservative character map and checked against the model vocabulary.
"""
from __future__ import annotations

import importlib
import io
import logging
import os
import re
import threading
import unicodedata
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _require_module(module_name: str, purpose: str) -> Any:
    """Import a heavyweight runtime dependency only when its feature is used."""
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f"{purpose} requires the '{module_name}' package in the active environment."
        ) from exc

ASR_MODEL_ID = os.getenv("GONDI_MMS_ASR_MODEL_ID", "facebook/mms-1b-all").strip()
TTS_MODEL_ID = os.getenv("GONDI_MMS_TTS_MODEL_ID", "facebook/mms-tts-wsg").strip()
GONDI_MMS_CODE = "wsg"  # Adilabad Gondi in the Meta MMS language tables

# Approximate character-level conversion: the ASR/TTS wsg checkpoints use the
# Telugu-script character inventory, while AdiBhasha Gondi text is Devanagari.
# Several aspirated/rare characters collapse to the nearest token supported by
# the specific TTS vocabulary. This is a prototype transliteration, not a
# linguistically validated script conversion.
DEVANAGARI_TO_TELUGU = {
    "अ": "అ", "आ": "ఆ", "इ": "ఇ", "ई": "ఈ", "उ": "ఉ", "ऊ": "ఊ",
    "ऋ": "ఉ", "ॠ": "ఉ", "ऌ": "ఇ", "ए": "ఎ", "ऐ": "ఎ", "ओ": "ఒ", "औ": "ఒ",
    "क": "క", "ख": "క", "ग": "గ", "घ": "గ", "ङ": "న",
    "च": "చ", "छ": "చ", "ज": "జ", "झ": "జ", "ञ": "న",
    "ट": "ట", "ठ": "ట", "ड": "డ", "ढ": "డ", "ण": "న",
    "त": "త", "थ": "త", "द": "ద", "ध": "ద", "न": "న",
    "प": "ప", "फ": "ప", "ब": "బ", "भ": "బ", "म": "మ",
    "य": "య", "र": "ర", "ल": "ల", "ळ": "ల", "व": "వ",
    "श": "స", "ष": "స", "स": "స", "ह": "హ",
    "ा": "ా", "ि": "ి", "ी": "ీ", "ु": "ు", "ू": "ూ", "ृ": "ు",
    "े": "ే", "ै": "ే", "ो": "ో", "ौ": "ో", "ं": "ం", "ँ": "ం",
    "ः": "", "्": "్", "़": "", "ऽ": "", "ॐ": "ఓం",
}
TELUGU_TO_DEVANAGARI = {
    "అ": "अ", "ఆ": "आ", "ఇ": "इ", "ఈ": "ई", "ఉ": "उ", "ఊ": "ऊ",
    "ఋ": "ऋ", "ఎ": "ए", "ఏ": "ए", "ఐ": "ऐ", "ఒ": "ओ", "ఓ": "ओ", "ఔ": "औ",
    "క": "क", "ఖ": "ख", "గ": "ग", "ఘ": "घ", "ఙ": "ङ", "చ": "च", "ఛ": "छ",
    "జ": "ज", "ఝ": "झ", "ఞ": "ञ", "ట": "ट", "ఠ": "ठ", "డ": "ड", "ఢ": "ढ",
    "ణ": "ण", "త": "त", "థ": "थ", "ద": "द", "ధ": "ध", "న": "न", "ప": "प",
    "ఫ": "फ", "బ": "ब", "భ": "भ", "మ": "म", "య": "य", "ర": "र", "ల": "ल",
    "ళ": "ळ", "వ": "व", "శ": "श", "ష": "ष", "స": "स", "హ": "ह",
    "ా": "ा", "ి": "ि", "ీ": "ी", "ు": "ु", "ూ": "ू", "ృ": "ृ", "ె": "े",
    "ే": "े", "ై": "ै", "ొ": "ो", "ో": "ो", "ౌ": "ौ", "ం": "ं", "ఁ": "ँ",
    "ః": "ः", "్": "्",
}


def devanagari_to_telugu(text: str) -> str:
    """Convert Devanagari characters to a conservative Telugu-script form for MMS-TTS."""
    raw = re.sub(r"(?i)\bAI\b", "అయి", str(text or ""))
    result: list[str] = []
    for char in raw:
        if char in DEVANAGARI_TO_TELUGU:
            result.append(DEVANAGARI_TO_TELUGU[char])
        elif char.isascii() and char.isalpha():
            # Preserve no unsupported Roman words as if they were Gondi; callers can report the limitation.
            result.append(char)
        elif char.isdigit():
            # Digits are outside this wsg tokenizer; use a pause rather than an unknown phoneme.
            result.append(" ")
        elif unicodedata.category(char).startswith("P") or char.isspace():
            result.append(" ")
        elif char in "।॥":
            result.append(" ")
        elif "\u0c00" <= char <= "\u0c7f":
            result.append(char)
        else:
            # Do not silently strip other scripts. Keep the character for vocabulary validation.
            result.append(char)
    return re.sub(r"\s+", " ", "".join(result)).strip()


def telugu_to_devanagari(text: str) -> str:
    """Map the Telugu-script wsg ASR output to the Devanagari form used for text MT."""
    return "".join(TELUGU_TO_DEVANAGARI.get(char, char) for char in str(text or "")).strip()


class GondiMMSServices:
    def __init__(self) -> None:
        self._asr_processor: Any = None
        self._asr_model: Any = None
        self._asr_device: str | None = None
        self._tts_tokenizer: Any = None
        self._tts_model: Any = None
        self._tts_device: str | None = None
        self._asr_lock = threading.Lock()
        self._tts_lock = threading.Lock()

    def status(self) -> dict[str, Any]:
        """Return readiness metadata for this service instance."""
        return {
            "language": "gondi",
            "variety": "Adilabad Gondi (wsg)",
            "asr_model": ASR_MODEL_ID,
            "asr_loaded": self._asr_model is not None,
            "asr_loads_on_first_request": True,
            "tts_model": TTS_MODEL_ID,
            "tts_loaded": self._tts_model is not None,
            "tts_loads_on_first_request": True,
            "text_translation_model": "google/mt5-small fine-tuned on Hindi-Gondi data",
            "notes": [
                "Speech models are experimental and load lazily; first use downloads model weights.",
                "ASR/TTS are for the Adilabad Gondi (wsg) variety, not all Gondi varieties.",
                "The wsg TTS tokenizer uses Telugu script; text is transliterated from Devanagari with approximations.",
                "Validate output with Gondi speakers before relying on it.",
            ],
        }

    def _load_asr(self) -> None:
        if self._asr_model is not None:
            return
        with self._asr_lock:
            if self._asr_model is not None:
                return
            torch = _require_module("torch", "Gondi ASR")
            transformers = _require_module("transformers", "Gondi ASR")
            auto_model_for_ctc = getattr(transformers, "AutoModelForCTC", None)
            auto_processor = getattr(transformers, "AutoProcessor", None)
            if auto_model_for_ctc is None or auto_processor is None:
                raise RuntimeError(
                    "The installed transformers package does not expose AutoModelForCTC and AutoProcessor."
                )
            try:
                processor = auto_processor.from_pretrained(ASR_MODEL_ID)
                processor.tokenizer.set_target_lang(GONDI_MMS_CODE)
                model = auto_model_for_ctc.from_pretrained(ASR_MODEL_ID)
                model.load_adapter(GONDI_MMS_CODE)
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model.to(device)
                model.eval()
            except Exception as exc:
                logger.exception("Unable to load MMS Adilabad Gondi ASR model.")
                raise RuntimeError(
                    f"Could not load {ASR_MODEL_ID} adapter '{GONDI_MMS_CODE}' ({type(exc).__name__}). "
                    "Confirm the current Transformers version and model adapter availability."
                ) from exc
            self._asr_processor, self._asr_model, self._asr_device = processor, model, device
            logger.info("Loaded Gondi MMS ASR adapter %s on %s", GONDI_MMS_CODE, device)

    def transcribe_audio_bytes(self, audio_bytes: bytes) -> dict[str, str]:
        if not audio_bytes:
            raise ValueError("Audio upload is empty.")
        sf = _require_module("soundfile", "Gondi ASR")
        torch = _require_module("torch", "Gondi ASR")
        try:
            waveform, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)
        except Exception as exc:
            raise ValueError("Could not read this audio. Upload a WAV or FLAC recording.") from exc
        waveform = np.asarray(waveform, dtype=np.float32)
        if waveform.ndim == 2:
            waveform = waveform.mean(axis=1)
        if waveform.ndim != 1 or waveform.size == 0:
            raise ValueError("Audio must contain a non-empty mono or stereo signal.")
        duration = waveform.size / float(sample_rate)
        if duration > 90:
            raise ValueError("Gondi transcription accepts recordings up to 90 seconds.")
        if sample_rate <= 0:
            raise ValueError("Invalid audio sample rate.")
        if sample_rate != 16000:
            new_size = max(1, int(round(waveform.size * 16000 / sample_rate)))
            waveform = np.interp(
                np.linspace(0, waveform.size - 1, new_size),
                np.arange(waveform.size),
                waveform,
            ).astype(np.float32)
        self._load_asr()
        asr_processor = self._asr_processor
        asr_model = self._asr_model
        if asr_processor is None or asr_model is None or self._asr_device is None:
            raise RuntimeError("Gondi ASR model initialization did not complete.")
        inputs = asr_processor(waveform, sampling_rate=16000, return_tensors="pt")
        inputs = {key: value.to(self._asr_device) for key, value in inputs.items()}
        try:
            with torch.inference_mode():
                logits = asr_model(**inputs).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            raw_text = asr_processor.batch_decode(predicted_ids)[0].strip()
        except Exception as exc:
            logger.exception("MMS Gondi ASR inference failed.")
            raise RuntimeError(f"Gondi ASR inference failed ({type(exc).__name__}).") from exc
        if not raw_text:
            raise RuntimeError("MMS returned an empty Gondi transcription.")
        # MMS wsg may use Telugu-script text. Return a Devanagari-form approximation
        # for the local Hindi-Gondi translation model, retaining the raw hypothesis too.
        devanagari_text = telugu_to_devanagari(raw_text) if any("\u0c00" <= c <= "\u0c7f" for c in raw_text) else raw_text
        return {"text": devanagari_text, "raw_text": raw_text, "raw_script": "Telugu or model-native", "script": "Devanagari approximation"}

    def _load_tts(self) -> None:
        if self._tts_model is not None:
            return
        with self._tts_lock:
            if self._tts_model is not None:
                return
            torch = _require_module("torch", "Gondi TTS")
            transformers = _require_module("transformers", "Gondi TTS")
            auto_tokenizer = getattr(transformers, "AutoTokenizer", None)
            auto_model_for_text_to_waveform = getattr(transformers, "AutoModelForTextToWaveform", None)
            if auto_tokenizer is None or auto_model_for_text_to_waveform is None:
                raise RuntimeError(
                    "The installed transformers package does not expose the MMS-TTS model classes required here."
                )
            try:
                tokenizer = auto_tokenizer.from_pretrained(TTS_MODEL_ID)
                model = auto_model_for_text_to_waveform.from_pretrained(TTS_MODEL_ID)
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model.to(device)
                model.eval()
            except Exception as exc:
                logger.exception("Unable to load MMS Adilabad Gondi TTS model.")
                raise RuntimeError(f"Could not load {TTS_MODEL_ID} ({type(exc).__name__}).") from exc
            self._tts_tokenizer, self._tts_model, self._tts_device = tokenizer, model, device
            logger.info("Loaded Gondi MMS TTS model on %s", device)

    def synthesize_wav(self, text: str) -> tuple[bytes, str]:
        value = str(text or "").strip()
        if not value:
            raise ValueError("Text for Gondi speech is empty.")
        if len(value) > 1200:
            raise ValueError("Gondi speech accepts at most 1200 characters at a time.")
        self._load_tts()
        torch = _require_module("torch", "Gondi TTS")
        tts_tokenizer = self._tts_tokenizer
        tts_model = self._tts_model
        if tts_tokenizer is None or tts_model is None or self._tts_device is None:
            raise RuntimeError("Gondi TTS model initialization did not complete.")
        speech_text = devanagari_to_telugu(value)
        tokens = tts_tokenizer(speech_text, return_tensors="pt")
        # Refuse unsupported script fragments instead of returning misleading noise.
        unk_id = getattr(tts_tokenizer, "unk_token_id", None)
        input_ids = tokens.get("input_ids")
        if unk_id is not None and input_ids is not None and bool((input_ids == unk_id).any().item()):
            vocabulary = tts_tokenizer.get_vocab()
            bad = sorted({c for c in speech_text if c not in vocabulary and not c.isspace()})
            shown = " ".join(repr(c) for c in bad[:12]) or "unknown token"
            raise ValueError(
                "The Adilabad Gondi TTS tokenizer cannot represent part of this answer after script conversion. "
                f"Unsupported characters: {shown}. Try a shorter Gondi-only sentence without English words or numbers."
            )
        tokens = {key: tensor.to(self._tts_device) for key, tensor in tokens.items()}
        try:
            with torch.inference_mode():
                output = tts_model(**tokens).waveform.detach().cpu().squeeze().numpy()
            sf = _require_module("soundfile", "Gondi TTS")
            buffer = io.BytesIO()
            sf.write(buffer, output, int(tts_model.config.sampling_rate), format="WAV", subtype="PCM_16")
            return buffer.getvalue(), speech_text
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("MMS Gondi TTS synthesis failed.")
            raise RuntimeError(f"Gondi speech generation failed ({type(exc).__name__}).") from exc

gondi_mms_services = GondiMMSServices()
