
import time
from pathlib import Path

import torch
import torchaudio
from transformers import AutoModel

MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"
TARGET_SAMPLE_RATE = 16000
LANGUAGE_CODE = "mni"


class ExperimentalMeiteiSTT:
    """
    Experimental Manipuri speech-to-text service.

    Uses IndicConformer RNNT decoding to generate
    transcription in Meitei Mayek script.

    This service is isolated from production code.
    """
    def __init__(self):
        self.model = None

    def load_model(self):
        """Load the IndicConformer model."""
        if self.model is not None:
            return
        print("Loading IndicConformer model...")
        start_time = time.perf_counter()
        self.model = AutoModel.from_pretrained(
            MODEL_ID,
            trust_remote_code=True
        )
        self.model.eval()
        elapsed = time.perf_counter() - start_time
        print(
            f"Model loaded in {elapsed:.2f} seconds."
        )
    @staticmethod
    def load_audio(audio_path):
        """Load and preprocess audio."""
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )
        waveform, sample_rate = torchaudio.load(
            str(audio_path)
        )
        if waveform.shape[0] > 1:
            waveform = torch.mean(
                waveform,
                dim=0,
                keepdim=True
            )
        if sample_rate != TARGET_SAMPLE_RATE:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=TARGET_SAMPLE_RATE
            )
            waveform = resampler(waveform)
        return waveform
    def transcribe(self, audio_path):
        """
        Transcribe audio using RNNT decoding.
        Returns:
            dict: Transcription and performance details.
        """
        if self.model is None:
            self.load_model()
        waveform = self.load_audio(audio_path)
        audio_duration = (
            waveform.shape[-1] / TARGET_SAMPLE_RATE
        )
        start_time = time.perf_counter()
        with torch.inference_mode():
            transcription = self.model(
                waveform,
                LANGUAGE_CODE,
                "rnnt"
            )
        inference_time = (
            time.perf_counter() - start_time
        )
        rtf = inference_time / audio_duration
        return {
            "text": str(transcription),
            "language": "manipuri",
            "script": "meitei_mayek",
            "decoder": "rnnt",
            "audio_duration": round(audio_duration, 2),
            "inference_time": round(inference_time, 2),
            "rtf": round(rtf, 3)
        }

if __name__ == "__main__":
    print("=" * 60)
    print("EXPERIMENTAL MEITEI MAYEK STT")
    print("=" * 60)
    audio_path = input(
        "Enter full audio file path: "
    ).strip().strip('"')
    stt = ExperimentalMeiteiSTT()
    try:
        result = stt.transcribe(audio_path)
        print("\nTranscription:")
        print(result["text"])
        print("\nPerformance:")
        print(
            f"Audio duration: "
            f"{result['audio_duration']} seconds"
        )
        print(
            f"Inference time: "
            f"{result['inference_time']} seconds"
        )
        print(
            f"RTF: {result['rtf']}"
        )
        print("\nSTT experiment completed.")
    except Exception as error:
        print(f"\nSTT failed: {error}")