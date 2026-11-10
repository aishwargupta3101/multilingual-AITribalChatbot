"""Low-memory Santali Ol Chiki text-to-speech using the Santali Piper VITS ONNX export.

Only the ONNX model, its small config, and its paired phonemizer are fetched from HF.
The model is Apache-2.0; review its source Rasa dataset terms separately before redistribution.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import threading
from pathlib import Path
from typing import Any

MODEL_REPO = "kaushalkrishnax/santali-piper-vits"
_MODEL_FILENAME = "model/santali_piper_vits.onnx"
_CONFIG_FILENAME = "model/santali_piper_vits.onnx.json"
_PHONEMIZER_FILENAME = "santali_phonemizer.py"
_LOCK = threading.RLock()
_SESSION: Any = None
_CONFIG: dict[str, Any] | None = None
_PHONEMIZER: Any = None


def _load_resources():
    global _SESSION, _CONFIG, _PHONEMIZER
    with _LOCK:
        if _SESSION is not None and _CONFIG is not None and _PHONEMIZER is not None:
            return _SESSION, _CONFIG, _PHONEMIZER
        try:
            import onnxruntime as ort
            from huggingface_hub import hf_hub_download
        except ImportError as exc:
            raise RuntimeError(
                "Santali speech generation requires onnxruntime and huggingface_hub. "
                "Install the missing packages into the project's existing .venv and update requirements.txt."
            ) from exc

        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        kwargs = {"repo_id": MODEL_REPO}
        if token:
            kwargs["token"] = token
        try:
            model_path = hf_hub_download(filename=_MODEL_FILENAME, **kwargs)
            config_path = hf_hub_download(filename=_CONFIG_FILENAME, **kwargs)
            phonemizer_path = hf_hub_download(filename=_PHONEMIZER_FILENAME, **kwargs)
        except Exception as exc:
            raise RuntimeError(
                f"Could not download the Santali TTS assets from {MODEL_REPO}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
        module_spec = importlib.util.spec_from_file_location("santali_piper_phonemizer", phonemizer_path)
        if module_spec is None or module_spec.loader is None:
            raise RuntimeError("Could not load the Santali phonemizer module.")
        phonemizer = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(phonemizer)
        options = ort.SessionOptions()
        options.intra_op_num_threads = max(1, min(4, os.cpu_count() or 1))
        options.inter_op_num_threads = 1
        session = ort.InferenceSession(
            model_path,
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        _SESSION, _CONFIG, _PHONEMIZER = session, config, phonemizer
        return _SESSION, _CONFIG, _PHONEMIZER


def _prepare_santali_tts_input(text: str) -> str:
    """Prepare audio-only text for the Ol Chiki Santali phonemizer.

    The displayed chatbot answer is not modified. Markdown delimiters and
    characters from unsupported writing systems are removed only from the
    text sent to this Santali-only TTS model.
    """
    import re
    import unicodedata

    source = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    # Remove structural Markdown before phonemization.
    source = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", source)
    source = re.sub(r"(?m)^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", source)
    source = re.sub(r"\*\*|__|[*`~]", "", source)

    # The voice model is trained for Ol Chiki. Keep Ol Chiki, ASCII words
    # (e.g. AI), whitespace, and basic punctuation. Replace other scripts
    # (for example Bengali, Odia, or Arabic fragments) with spaces so their
    # unsupported marks cannot crash phonemization.
    allowed_ascii_punctuation = set(".,!?;:'\"()[]{}-/%&+")
    output = []
    removed = 0
    for char in source:
        codepoint = ord(char)
        is_olchiki = 0x1C50 <= codepoint <= 0x1C7F
        is_ascii_text = char.isascii() and (
            char.isalnum() or char.isspace() or char in allowed_ascii_punctuation
        )
        if is_olchiki or is_ascii_text:
            output.append(char)
        elif char.isspace():
            output.append(" ")
        else:
            output.append(" ")
            removed += 1

    prepared = re.sub(r"\s+", " ", "".join(output)).strip()
    if removed:
        import logging
        logging.getLogger(__name__).warning(
            "Santali TTS omitted %d unsupported-script/formatting character(s) from audio input; displayed answer is unchanged.",
            removed,
        )

    has_olchiki_letter = any(
        0x1C50 <= ord(char) <= 0x1C7F
        and unicodedata.category(char).startswith("L")
        for char in prepared
    )
    if not prepared or not has_olchiki_letter:
        raise ValueError(
            "Santali speech needs Ol Chiki text. No supported Ol Chiki text remained after removing unsupported characters."
        )
    return prepared


def synthesize_santali_wav(text: str) -> bytes:
    """Synthesize Ol Chiki text and return a WAV byte string."""
    clean = str(text or "").strip()
    if not clean:
        raise ValueError("Santali TTS input is empty.")
    if len(clean) > 1200:
        raise ValueError("Santali TTS input is too long (limit 1,200 characters).")
    try:
        import numpy as np
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError("Santali speech output requires numpy and soundfile.") from exc

    session, config, phonemizer = _load_resources()
    id_map = config.get("phoneme_id_map", {})
    tts_text = _prepare_santali_tts_input(clean)
    tokens = phonemizer.santali_to_phonemes(tts_text)
    ids = list(id_map.get("^", []))
    if not ids:
        raise RuntimeError("Santali TTS configuration has no start token.")
    for token in tokens:
        if token not in id_map:
            raise ValueError(
                f"Santali TTS does not recognize phoneme token {token!r}; "
                "the text may contain an unsupported character."
            )
        ids.extend(id_map[token])
        ids.extend(id_map["_"])
    ids.extend(id_map.get("$", []))
    if len(ids) > 8000:
        raise ValueError("Santali text is too long to synthesize safely.")

    inf = config.get("inference", {})
    # ONNX exports do not all expose the optional Piper speaker-id input.
    # This particular model export rejects "sid", so construct the feed from
    # the actual graph inputs rather than passing unsupported optional inputs.
    candidate_feed = {
        "input": np.asarray([ids], dtype=np.int64),
        "input_lengths": np.asarray([len(ids)], dtype=np.int64),
        "scales": np.asarray(
            [inf.get("noise_scale", 0.667), inf.get("length_scale", 1.0), inf.get("noise_w", 0.8)],
            dtype=np.float32,
        ),
        "sid": np.asarray([0], dtype=np.int64),
    }
    actual_input_names = [item.name for item in session.get_inputs()]
    required_unhandled = [name for name in actual_input_names if name not in candidate_feed]
    if required_unhandled:
        raise RuntimeError(
            "Unsupported required input(s) in Santali TTS ONNX model: "
            + ", ".join(required_unhandled)
            + ". Inspect session.get_inputs() and update the input mapping."
        )
    input_feed = {name: candidate_feed[name] for name in actual_input_names}
    audio = session.run(None, input_feed)[0].squeeze()

    output = io.BytesIO()
    sf.write(output, audio, int(config.get("audio", {}).get("sample_rate", 22050)), format="WAV")
    return output.getvalue()


def tts_model_loaded() -> bool:
    """Return whether the ONNX voice is loaded in this backend process."""
    return _SESSION is not None
