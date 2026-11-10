import sys
import time
import wave
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from TTS.utils.synthesizer import Synthesizer
from backend.translation.meitei_script_converter import convert_meitei_to_bengali

FASTPITCH_MODEL = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\best_model.pth"
FASTPITCH_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\config.json"
SPEAKERS_FILE = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\speakers.pth"
HIFIGAN_MODEL = r"C:\Users\kunda\Downloads\mni\mni\hifigan\best_model.pth"
HIFIGAN_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\hifigan\config.json"

OUTPUT_DIR = Path("experimental_outputs/manipuri_tts/indic_tts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEXTS = [
    "ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯍꯥꯌꯕ ꯃꯇꯝ ꯄꯨꯔꯛꯂꯤ꯫",
    "ꯃꯤꯇꯩ ꯂꯣꯟ ꯑꯁꯤ ꯃꯤꯌꯥꯝꯅ ꯁꯤꯡꯖꯤꯟꯅꯕ ꯂꯣꯟꯅꯤ꯫",
    "ꯑꯩ ꯀ꯭ꯂꯥꯁꯇꯥ ꯄꯔꯤꯡ ꯇꯝꯂꯤ꯫",
    "ꯃꯤꯌꯥꯝꯅ ꯏꯃꯥ ꯂꯣꯟ ꯑꯃꯁꯨꯡ ꯏꯅꯥ ꯂꯣꯟ ꯁꯤꯡꯖꯤꯟꯅꯕ ꯌꯥꯏ꯫",
    "ꯅꯨꯡꯉꯥꯏꯖꯔꯤꯕ ꯅꯨꯃꯤꯠ ꯑꯃꯗꯥ ꯃꯤꯌꯥꯝꯒ ꯂꯣꯏꯅꯅ ꯄꯥꯡꯊꯣꯛꯂꯤ꯫"
]

print("Loading AI4Bharat Manipuri TTS...")

load_start = time.perf_counter()

synthesizer = Synthesizer(
    tts_checkpoint=FASTPITCH_MODEL,
    tts_config_path=FASTPITCH_CONFIG,
    tts_speakers_file=SPEAKERS_FILE,
    vocoder_checkpoint=HIFIGAN_MODEL,
    vocoder_config=HIFIGAN_CONFIG,
    use_cuda=False
)

load_time = time.perf_counter() - load_start

print(f"Model loaded in {load_time:.2f}s")

for index, meitei_text in enumerate(TEXTS, start=1):
    bengali_text = convert_meitei_to_bengali(meitei_text)
    bengali_text = bengali_text.replace("।", "")

    print("\n" + "=" * 60)
    print(f"TEST {index}")
    print("Meitei :", meitei_text)
    print("Bengali:", bengali_text)

    start = time.perf_counter()

    wav = synthesizer.tts(
        text=bengali_text,
        speaker_name="female"
    )

    generation_time = time.perf_counter() - start

    audio = np.asarray(wav)

    if audio.dtype != np.int16:
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767).astype(np.int16)

    output_path = OUTPUT_DIR / f"manipuri_test_{index}.wav"

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(synthesizer.tts_model.ap.sample_rate)
        wf.writeframes(audio.tobytes())

    with wave.open(str(output_path), "rb") as wf:
        duration = wf.getnframes() / wf.getframerate()

    rtf = generation_time / duration if duration else 0

    print(f"Generation: {generation_time:.2f}s")
    print(f"Duration  : {duration:.2f}s")
    print(f"RTF       : {rtf:.2f}x")
    print(f"Output    : {output_path.resolve()}")

print("\n" + "=" * 60)
print("ALL 5 TESTS COMPLETED")
print("=" * 60)