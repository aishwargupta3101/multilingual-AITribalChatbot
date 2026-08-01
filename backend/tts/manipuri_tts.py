"""
Manipuri TTS Service
Uses AI4Bharat Indic Parler-TTS
"""

import logging
import os
import uuid

import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
logger = logging.getLogger(__name__)

class ManipuriTTS:

    def __init__(self):
        logger.info("Loading Indic Parler TTS...")

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        self.model = (
            ParlerTTSForConditionalGeneration
            .from_pretrained(
                "ai4bharat/indic-parler-tts"
            )
            .to(self.device)
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "ai4bharat/indic-parler-tts"
        )
        self.description_tokenizer = AutoTokenizer.from_pretrained(
            self.model.config.text_encoder._name_or_path
        )
        os.makedirs(
            "generated_audio",
            exist_ok=True
        )
        logger.info("Indic Parler TTS Loaded Successfully.")

    def text_to_speech(
        self,
        text: str
    ) -> str:
        description = (
            "Laishram speaks in Manipuri with a clear, "
            "natural, pleasant female voice at a normal speed."
        )
        description_inputs = self.description_tokenizer(
            description,
            return_tensors="pt"
        ).to(self.device)
        prompt_inputs = self.tokenizer(
            text,
            return_tensors="pt"
        ).to(self.device)
        with torch.no_grad():
            generation = self.model.generate(
                input_ids=description_inputs.input_ids,
                attention_mask=description_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask,
            )
        audio = generation.cpu().numpy().squeeze()
        filename = f"{uuid.uuid4()}.wav"

        filepath = os.path.join(
            "generated_audio",
            filename
        )
        sf.write(
            filepath,
            audio,
            self.model.config.sampling_rate
        )
        return filepath
manipuri_tts = ManipuriTTS()