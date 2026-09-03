"""
Manipuri TTS Service
Uses AI4Bharat Indic Parler-TTS
"""

import logging
import os
import uuid
import numpy as np
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


class ManipuriTTS:
    def __init__(self):
        logger.info("Initializing Manipuri TTS...")

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        self.model = None
        self.tokenizer = None
        self.description_tokenizer = None
        os.makedirs(
            "generated_audio",
            exist_ok=True
        )

    def load_model(self):
        if self.model is not None:
            return
        logger.info(
            "Loading AI4Bharat Indic Parler-TTS..."
        )
        self.model = (
            ParlerTTSForConditionalGeneration
            .from_pretrained(
                "ai4bharat/indic-parler-tts"
            )
            .to(self.device)
        )
        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                "ai4bharat/indic-parler-tts"
            )
        )
        self.description_tokenizer = (
            AutoTokenizer.from_pretrained(
                self.model.config.text_encoder._name_or_path
            )
        )

        logger.info(
            "AI4Bharat Indic Parler-TTS loaded successfully."
        )

    def text_to_speech(self, text: str) -> str:
        self.load_model()
        print("=" * 60)
        print("ENTERED MANIPURI TTS")
        print("Text:", text)
        description = (
            "Laishram speaks in Manipuri with a clear female voice "
            "at a normal speaking pace. The recording is very clear audio."
        )
        description_inputs = (
            self.description_tokenizer(
                description,
                return_tensors="pt"
            ).to(self.device)
        )
        prompt_inputs = (
            self.tokenizer(
                text,
                return_tensors="pt"
            ).to(self.device)
        )
        print("Before generate")

        with torch.no_grad():
            generation = self.model.generate(
                input_ids=description_inputs.input_ids,
                attention_mask=description_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask,
                max_new_tokens=256
            )

        print("After generate")
        audio = (
            generation
            .detach()
            .cpu()
            .numpy()
            .squeeze()
        )
        print("Shape:", audio.shape)
        print("Min:", np.min(audio))
        print("Max:", np.max(audio))
        filename = f"{uuid.uuid4()}.wav"

        filepath = os.path.join(
            "generated_audio",
            filename
        )
        print("Saving Audio...")
        sf.write(
            filepath,
            audio,
            self.model.config.sampling_rate,
            subtype="PCM_16"
        )
        print("Saved:", filepath)
        print("=" * 60)
        return filepath
manipuri_tts = ManipuriTTS()