import os
import sys
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else None

if THREADS is None:
    print("=" * 60)
    print("CPU THREAD PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"CPU logical processors: {os.cpu_count()}")
    print("Tests: [4, 6, 8, 10, 12]")
    print()
    print("Each thread count runs in a separate Python process.")
    print("Production TTS code is NOT modified.")
    print()

    results = []

    for threads in [4, 6, 8, 10, 12]:
        print(f"\nStarting {threads}-thread test...")
        completed = subprocess.run(
            [sys.executable, __file__, str(threads)],
            cwd=PROJECT_ROOT,
            text=True
        )

        if completed.returncode != 0:
            print(f"Test with {threads} threads failed.")

    print("\n" + "=" * 60)
    print("ALL THREAD TESTS COMPLETED")
    print("=" * 60)
    print("Review the individual results above.")
    sys.exit(0)

import torch

torch.set_num_threads(THREADS)
torch.set_num_interop_threads(1)

from backend.experimental_voice.bengali_script.tts import ExperimentalManipuriTTS

TEST_TEXT = "ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯋꯥꯍꯪ ꯑꯃꯥ ꯍꯥꯏꯖꯕꯥ ꯑꯃꯥ ꯍꯥꯏꯖꯒꯅꯤ꯫"
SCRIPT = "meitei_mayek"

print("\n" + "=" * 60)
print(f"TESTING CPU THREADS: {THREADS}")
print("=" * 60)
print(f"PyTorch threads: {torch.get_num_threads()}")
print(f"PyTorch inter-op threads: {torch.get_num_interop_threads()}")

tts = ExperimentalManipuriTTS()

start = time.perf_counter()

result = tts.generate(
    text=TEST_TEXT,
    script=SCRIPT,
    output_name=f"benchmark_threads_{THREADS}.wav"
)

total_time = time.perf_counter() - start

if not result.get("success"):
    print("TTS FAILED")
    print(result.get("error"))
    sys.exit(1)

audio_duration = result.get("duration_seconds")
if audio_duration is None:
    audio_duration = result.get("audio_duration")

generation_time = result.get("generation_time_seconds")
if generation_time is None:
    generation_time = result.get("generation_time")

print("\n========== RESULT ==========")
print(f"Threads:          {THREADS}")
print(f"Total time:       {total_time:.2f}s")
print(f"Generation time:  {generation_time}")
print(f"Audio duration:   {audio_duration}")

if audio_duration:
    print(f"RTF:              {total_time / audio_duration:.2f}")

print("============================")