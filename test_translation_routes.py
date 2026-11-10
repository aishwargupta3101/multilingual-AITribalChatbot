
from backend.services.translation_service import translation_service

test_cases = [
    ("Hello, how are you?", "english", "hindi"),
    ("Hello, how are you?", "english", "manipuri"),
    ("Hello, how are you?", "english", "manipuri_mtei"),
    ("What is artificial intelligence?", "english", "manipuri"),
    ("What is artificial intelligence?", "english", "manipuri_mtei"),
    ("नमस्ते, आप कैसे हैं?", "hindi", "manipuri"),
    ("नमस्ते, आप कैसे हैं?", "hindi", "manipuri_mtei")
]

for text, source, target in test_cases:
    print("\n" + "=" * 70)
    print(f"{source.upper()} -> {target.upper()}")
    print("Input:", text)

    try:
        output = translation_service.translate(
            text=text,
            source_language=source,
            target_language=target
        )
        print("Output:", output)
    except Exception as e:
        print("ERROR:", e)