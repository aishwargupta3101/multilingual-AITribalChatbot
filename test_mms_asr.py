from pathlib import Path
from backend.services.mms_asr_service import mms_asr_service

audio_path = Path("test_audio.wav")

if not audio_path.exists():
    raise FileNotFoundError(
        "Place a Manipuri recording named test_audio.wav in the project root."
    )

audio_bytes = audio_path.read_bytes()

print("Starting Manipuri transcription...")

text = mms_asr_service.transcribe(audio_bytes)

print("\nTranscription:")
print(text)