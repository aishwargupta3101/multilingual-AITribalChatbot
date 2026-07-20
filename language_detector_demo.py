from backend.translation import LanguageDetector
samples = [

    "Hello, how are you?",

    "नमस्ते आप कैसे हैं?",

    "Good Morning",

    "भारत मेरा देश है"

]
for text in samples:

    language = LanguageDetector.detect_language(text)
    print(f"\nInput : {text}")
    print(f"Detected : {language}")