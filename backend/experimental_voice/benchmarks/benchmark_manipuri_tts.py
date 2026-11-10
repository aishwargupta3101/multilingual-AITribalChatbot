import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.experimental_voice.bengali_script.tts import ExperimentalManipuriTTS

TEST_TEXT = "ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯋꯥꯍꯪ ꯑꯃꯥ ꯍꯥꯏꯖꯕꯥ ꯑꯃꯥ ꯍꯥꯏꯖꯒꯅꯤ꯫"
SCRIPT = "meitei_mayek"
OUTPUT_NAME = "benchmark_manipuri_tts.wav"

def main():
    print("=" * 60)
    print("MANIPURI TTS PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"Python PID: {os.getpid()}")
    print(f"CPU threads: {__import__('torch').get_num_threads()}")
    print(f"Test script: {SCRIPT}")
    print(f"Text length: {len(TEST_TEXT)} characters")
    print()
    print("Creating TTS instance...")
    start = time.perf_counter()
    tts = ExperimentalManipuriTTS()
    model_load_time = time.perf_counter() - start
    print(f"Initial model setup: {model_load_time:.2f} seconds")
    print()
    print("Starting TTS generation...")
    start = time.perf_counter()
    result = tts.generate(
        text=TEST_TEXT,
        script=SCRIPT,
        output_name=OUTPUT_NAME
    )
    total_time = time.perf_counter() - start
    print()
    if not result.get("success"):
        print("TTS FAILED")
        print(result.get("error"))
        return
    audio_path = result.get("audio_path")
    audio_duration = result.get("duration_seconds") or result.get("audio_duration")
    generation_time = result.get("generation_time_seconds") or result.get("generation_time")
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Audio path: {audio_path}")
    print(f"Device: {result.get('device')}")
    print(f"Generation time: {generation_time}")
    print(f"Total measured time: {total_time:.2f} seconds")
    print(f"Audio duration: {audio_duration}")
    if audio_duration:
        print(f"Real-Time Factor: {total_time / audio_duration:.2f}")
    print("=" * 60)

if __name__ == "__main__":
    main()