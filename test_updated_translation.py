
from backend.services.translation_service import translation_service

test_cases = [
    ("Hello, how are you?", "english", "manipuri"),
    ("What is artificial intelligence?", "english", "manipuri"),
    ("नमस्ते, आप कैसे हैं?", "hindi", "manipuri"),
    ("कृत्रिम बुद्धिमत्ता क्या है?", "hindi", "manipuri"),
    ("Hello, how are you?", "english", "manipuri_mtei"),
    ("Hello, how are you?", "english", "hindi")
]

for text, source, target in test_cases:
    print("\n" + "=" * 65)
    print(f"INPUT ({source}): {text}")
    print(f"TARGET: {target}")

    try:
        result = translation_service.translate(text, source, target)
        print("OUTPUT:", result)
    except Exception as e:
        print("ERROR:", e)