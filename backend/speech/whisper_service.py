from faster_whisper import WhisperModel

class WhisperService:

    def __init__(self):
        print("=" * 60)
        print("Loading Faster-Whisper Model...")
        print("=" * 60)
        self.model = WhisperModel(
            model_size_or_path="medium",
            device="cpu",
            compute_type="int8"
        )
        print("Whisper Model Loaded Successfully")

    def transcribe(self, audio_path: str):
        print("=" * 60)
        print("🎤 USING FASTER WHISPER")
        print("Audio File:", audio_path)
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True
        )
        text = " ".join(segment.text for segment in segments).strip()
        print("Detected Language:", info.language)
        print("Confidence:", info.language_probability)
        print("Transcribed Text:", text)
        print("=" * 60)
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
whisper_service = WhisperService()