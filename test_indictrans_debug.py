import logging
from backend.translation.indictrans_service import indictrans_service

logging.basicConfig(level=logging.INFO)

indictrans_service.clear_cache()

tests = [
    ("Hello, how are you?", "english", "manipuri"),
    ("नमस्ते, आप कैसे हैं?", "hindi", "manipuri")
]

for text, source, target in tests:
    print("\n" + "=" * 60)
    print(f"{source} -> {target}")
    print("=" * 60)

    result = indictrans_service.translate(
        text=text,
        source_language=source,
        target_language=target
    )

    print("Final output:", result)
