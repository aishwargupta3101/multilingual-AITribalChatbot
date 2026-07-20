"""
Test Translation Service
"""
from backend.services.translation_service import translation_service
def main():

    text = "Hello, how are you?"
    result = translation_service.translate(
        text=text,
        source_language="english",
        target_language="hindi"
    )
    print("\nOriginal Text:")
    print(text)
    print("\nTranslated Text:")
    print(result)
if __name__ == "__main__":
    main()