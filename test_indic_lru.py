
import os
import time
import torch

os.environ["TRIBAL_INDIC_MODEL_CACHE_SIZE"] = "2"

from backend.translation.indictrans_service_lru_cache import IndicTransService

service = IndicTransService()

tests = [
    ("Hello, how are you?", "english", "hindi"),
    ("नमस्ते, आप कैसे हैं?", "hindi", "english"),
    ("Hello, how are you?", "english", "hindi"),
    ("नमस्ते, आप कैसे हैं?", "hindi", "bengali"),
    ("Artificial intelligence is useful.", "english", "hindi"),
]

for text, source, target in tests:
    start = time.perf_counter()

    result = service.translate(text, source, target)

    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    print("\nDirection:", source, "->", target)
    print("Translation:", result)
    print("Time:", round(elapsed, 3), "seconds")
    print("Cached models:", list(service._model_cache.keys()))
    print(
        "GPU memory:",
        round(torch.cuda.memory_allocated() / 1024**3, 2),
        "GB"
    )

print("\nLRU CACHE TEST COMPLETED")
print("GPU:", torch.cuda.get_device_name(0))
