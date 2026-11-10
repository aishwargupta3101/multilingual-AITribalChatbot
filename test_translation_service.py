
from backend.services.translation_service import translation_service

def test_translation(text, source, target):
    print(f"\n{source} -> {target}")
    print(f"Input: {text}")
    try:
        result = translation_service.translate(text, source, target)
        print(f"Output: {result}")
        print(f"Status: {'SUCCESS' if result else 'EMPTY OUTPUT'}")
    except ValueError as e:
        print(f"UNSUPPORTED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("TRANSLATION SERVICE TEST")
    print("=" * 60)
    test_translation("Hello, how are you?", "english", "manipuri_mtei")
    test_translation("नमस्ते, आप कैसे हैं?", "hindi", "manipuri_mtei")
    test_translation("Hello, how are you?", "english", "manipuri")
    test_translation("I need your help.", "english", "hindi")
    test_translation("Hello, how are you?", "english", "tai_khamti")