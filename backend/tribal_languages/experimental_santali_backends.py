"""Optional lazy-loaded Santali model adapters.

These adapters are not mounted on any API route and are not enabled by default.
They load large gated models only when explicitly instantiated after repository
access has been approved. No heavy ML dependencies are imported at module import.
"""
from __future__ import annotations

import io
import os
import threading
from typing import Any

from .model_candidates import resolve_indictrans2_route


class ModelAccessNotAcceptedError(RuntimeError):
    """The model repository's gated-access conditions have not been acknowledged."""


def _token_kwargs() -> dict[str, str]:
    token = os.getenv("HF_TOKEN", "").strip()
    return {"token": token} if token else {}


class SantaliIndicConformerSTT:
    """Lazy Santali ASR adapter using AI4Bharat IndicConformer (MIT model card).

    The Hugging Face repository is gated. The caller must explicitly pass
    ``hf_access_accepted=True`` after accepting its access conditions.
    ``transcribe`` returns plain text. Audio input should be WAV/FLAC/OGG that
    soundfile can decode; it is converted to mono/16 kHz before inference.
    """
    MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"
    LANGUAGE_CODE = "sat"

    def __init__(self, *, hf_access_accepted: bool = False) -> None:
        if not hf_access_accepted:
            raise ModelAccessNotAcceptedError(
                "Accept access conditions for the IndicConformer Hugging Face model first."
            )
        self._model: Any = None
        self._device: Any = None
        self._lock = threading.RLock()

    def _load(self):
        with self._lock:
            if self._model is not None:
                return self._model, self._device
            try:
                import torch
                from transformers import AutoModel
            except ImportError as exc:
                raise RuntimeError(
                    "Santali ASR dependencies missing. Install torch and transformers "
                    "in the backend environment after checking model requirements."
                ) from exc
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            kwargs = {"trust_remote_code": True, **_token_kwargs()}
            model = AutoModel.from_pretrained(self.MODEL_ID, **kwargs)
            model.to(device)
            model.eval()
            self._model, self._device = model, device
            return model, device

    @staticmethod
    def _audio(audio_bytes: bytes):
        if not audio_bytes:
            raise ValueError("The uploaded audio is empty.")
        try:
            import numpy as np
            import soundfile as sf
            from scipy.signal import resample_poly
        except ImportError as exc:
            raise RuntimeError("Install soundfile, scipy, and numpy for audio decoding.") from exc
        try:
            data, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32")
        except Exception as exc:
            raise ValueError("Could not decode audio; use WAV, FLAC, or another soundfile-supported format.") from exc
        if data.size == 0:
            raise ValueError("The uploaded audio has no samples.")
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        if sample_rate != 16_000:
            from math import gcd
            g = gcd(int(sample_rate), 16_000)
            data = resample_poly(data, 16_000 // g, int(sample_rate) // g).astype(np.float32)
        return data

    def transcribe(self, audio_bytes: bytes, language: str = "santali") -> str:
        if str(language).strip().lower() not in {"santali", "sat", "sat_olck"}:
            raise ValueError("This backend only accepts Santali audio.")
        import torch
        import numpy as np
        audio = self._audio(audio_bytes)
        model, device = self._load()
        waveform = torch.from_numpy(np.asarray(audio, dtype=np.float32)).unsqueeze(0).to(device)
        with torch.inference_mode():
            result = model(waveform, self.LANGUAGE_CODE, "ctc")
        if isinstance(result, (list, tuple)):
            result = result[0] if result else ""
        text = str(result).strip()
        if not text:
            raise RuntimeError("IndicConformer returned an empty Santali transcription.")
        return text


class SantaliIndicTrans2Translator:
    """Lazy IndicTrans2 translator callable for Santali/English/Hindi pairs.

    Implements ``translator(text, source, target) -> str`` for the existing
    TribalTranslationService injection point. It does not configure verified
    pairs or activate an API endpoint by itself.
    """
    def __init__(self, *, hf_access_accepted: bool = False, max_new_tokens: int = 256) -> None:
        if not hf_access_accepted:
            raise ModelAccessNotAcceptedError(
                "Accept access conditions for the selected IndicTrans2 repositories first."
            )
        self.max_new_tokens = int(max_new_tokens)
        self._cache: dict[str, tuple[Any, Any, Any, Any]] = {}
        self._lock = threading.RLock()

    def _load(self, model_id: str):
        with self._lock:
            if model_id in self._cache:
                return self._cache[model_id]
            try:
                import torch
                from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
                from IndicTransToolkit.processor import IndicProcessor
            except ImportError as exc:
                raise RuntimeError(
                    "Install torch, transformers, sentencepiece, and IndicTransToolkit "
                    "in the backend environment before enabling IndicTrans2."
                ) from exc
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            token_args = _token_kwargs()
            tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, **token_args)
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_id, trust_remote_code=True, **token_args
            ).to(device)
            model.eval()
            processor = IndicProcessor(inference=True)
            loaded = (torch, tokenizer, model, processor, device)
            self._cache[model_id] = loaded
            return loaded

    def __call__(self, text: str, source: str, target: str) -> str:
        text = str(text).strip()
        if not text:
            return ""
        model_id, source_code, target_code = resolve_indictrans2_route(source, target)
        torch, tokenizer, model, processor, device = self._load(model_id)
        batch = processor.preprocess_batch([text], src_lang=source_code, tgt_lang=target_code)
        inputs = tokenizer(
            batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(device)
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                use_cache=True,
                min_length=0,
                max_length=self.max_new_tokens,
                num_beams=5,
                num_return_sequences=1,
            )
        decoded = tokenizer.batch_decode(
            generated, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        output = processor.postprocess_batch(decoded, lang=target_code)
        if not output or not str(output[0]).strip():
            raise RuntimeError(f"IndicTrans2 returned empty output for {source} -> {target}.")
        return str(output[0]).strip()


class SantaliParlerTTS:
    """Lazy Indic Parler-TTS backend for Santali; returns WAV bytes.

    The repository is gated and the checkpoint is large. A successful model load
    does not guarantee good Ol Chiki pronunciation: evaluate with native speakers.
    """
    MODEL_ID = "ai4bharat/indic-parler-tts"

    def __init__(self, *, hf_access_accepted: bool = False,
                 description: str = "A speaker reads Santali clearly at a moderate pace with very clear audio.") -> None:
        if not hf_access_accepted:
            raise ModelAccessNotAcceptedError(
                "Accept access conditions for ai4bharat/indic-parler-tts first."
            )
        self.description = description
        self._model = None
        self._tokenizer = None
        self._description_tokenizer = None
        self._device = None
        self._lock = threading.RLock()

    def _load(self):
        with self._lock:
            if self._model is not None:
                return
            try:
                import torch
                from parler_tts import ParlerTTSForConditionalGeneration
                from transformers import AutoTokenizer
            except ImportError as exc:
                raise RuntimeError(
                    "Install torch, transformers, and parler-tts before enabling Santali TTS."
                ) from exc
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            token_args = _token_kwargs()
            model = ParlerTTSForConditionalGeneration.from_pretrained(self.MODEL_ID, **token_args).to(device)
            tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID, **token_args)
            description_tokenizer = AutoTokenizer.from_pretrained(
                model.config.text_encoder._name_or_path, **token_args
            )
            model.eval()
            self._model, self._tokenizer = model, tokenizer
            self._description_tokenizer, self._device = description_tokenizer, device

    def __call__(self, text: str, language: str = "santali") -> bytes:
        if str(language).strip().lower() not in {"santali", "sat", "sat_olck"}:
            raise ValueError("This TTS backend only accepts Santali text.")
        text = str(text).strip()
        if not text:
            raise ValueError("Text must not be empty.")
        self._load()
        import soundfile as sf
        import torch
        description_inputs = self._description_tokenizer(
            self.description, return_tensors="pt"
        ).to(self._device)
        prompt_inputs = self._tokenizer(text, return_tensors="pt").to(self._device)
        with torch.inference_mode():
            waveform = self._model.generate(
                input_ids=description_inputs.input_ids,
                attention_mask=description_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask,
            )
        audio = waveform.detach().cpu().numpy().squeeze()
        if getattr(audio, "size", 0) == 0:
            raise RuntimeError("Indic Parler-TTS returned empty audio.")
        buffer = io.BytesIO()
        sf.write(buffer, audio, int(self._model.config.sampling_rate), format="WAV", subtype="PCM_16")
        return buffer.getvalue()
