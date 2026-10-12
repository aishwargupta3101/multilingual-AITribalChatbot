import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import wave
from pathlib import Path
import numpy as np
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from TTS.utils.synthesizer import Synthesizer
from backend.translation.meitei_script_converter import convert_meitei_to_bengali

FASTPITCH_MODEL = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\best_model.pth"
FASTPITCH_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\config.json"
SPEAKERS_FILE = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\speakers.pth"
HIFIGAN_MODEL = r"C:\Users\kunda\Downloads\mni\mni\hifigan\best_model.pth"
HIFIGAN_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\hifigan\config.json"

OUTPUT_DIR = PROJECT_ROOT / "experimental_outputs" / "manipuri_tts" / "unified"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate(text: str, script: str, speaker: str, output_path: str):
    if script == "meitei_mayek":
        text = convert_meitei_to_bengali(text)

    text = text.replace("।", "").strip()

    if not text:
        raise ValueError("Text is empty after script conversion.")

    synthesizer = Synthesizer(
        tts_checkpoint=FASTPITCH_MODEL,
        tts_config_path=FASTPITCH_CONFIG,
        tts_speakers_file=SPEAKERS_FILE,
        vocoder_checkpoint=HIFIGAN_MODEL,
        vocoder_config=HIFIGAN_CONFIG,
        use_cuda=False
    )

    wav = synthesizer.tts(
        text=text,
        speaker_name=speaker
    )

    audio = np.asarray(wav)

    if audio.dtype != np.int16:
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767).astype(np.int16)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(output), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(synthesizer.tts_model.ap.sample_rate)
        wf.writeframes(audio.tobytes())

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python indic_tts_worker.py <text> <script> <speaker> <output>")
        sys.exit(1)

    try:
        generate(
            text=sys.argv[1],
            script=sys.argv[2],
            speaker=sys.argv[3],
            output_path=sys.argv[4]
        )
        print("SUCCESS")
    except Exception as error:
        print(f"ERROR:{error}")
        sys.exit(1)