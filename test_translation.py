
from backend.services.translation_service import translation_service

tests = [
    {
        "text": "Hello, how are you?",
        "source": "english",
        "target": "hindi"
    },
    {
        "text": "Hello, how are you?",
        "source": "english",
        "target": "manipuri"
    },
    {
        "text": "What is artificial intelligence?",
        "source": "english",
        "target": "manipuri"
    }
]

for test in tests:
    print("\n" + "=" * 50)
    print(
        f"{test['source']} -> {test['target']}"
    )

    result = translation_service.translate(
        text=test["text"],
        source_language=test["source"],
        target_language=test["target"]
    )

    print("Input:", test["text"])
    print("Output:", result)