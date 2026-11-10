
from backend.services.translation_service import translation_service

tests = [
    ("Hello, how are you?", "english", "manipuri"),
    ("My name is Rahul.", "english", "manipuri"),
    ("Thank you.", "english", "manipuri"),
    ("नमस्कार, आप कैसे हैं?", "hindi", "manipuri"),
    ("आपका नाम क्या है?", "hindi", "manipuri"),
    ("Hello, how are you?", "english", "manipuri_mtei"),
    ("ꯍꯦꯂꯣ", "manipuri_mtei", "english"),
]

for text, source, target in tests:
    print("\n" + "=" * 60)
    print(f"Source: {source}")
    print(f"Target: {target}")
    print(f"Input: {text}")

    try:
        result = translation_service.translate(
            text,
            source,
            target
        )
        print(f"Output: {result}")
    except Exception as e:
        print(f"ERROR: {e}")