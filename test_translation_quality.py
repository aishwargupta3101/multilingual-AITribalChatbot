
import time
from backend.translation.translation_service import translation_service

tests = [
    {
        "name": "Hindi to English",
        "text": "मुझे शिक्षा प्राप्त करने के लिए छात्रवृत्ति की जानकारी चाहिए।",
        "source": "hindi",
        "target": "english"
    },
    {
        "name": "English to Hindi",
        "text": "Students can apply for scholarships to support their higher education.",
        "source": "english",
        "target": "hindi"
    },
    {
        "name": "English to Manipuri",
        "text": "Education is important for every student.",
        "source": "english",
        "target": "manipuri"
    },
    {
        "name": "Manipuri to English",
        "text": "ꯃꯤꯇꯩꯂꯣꯟ",
        "source": "manipuri_mtei",
        "target": "english"
    }
]

for test in tests:
    print("\n" + "=" * 60)
    print("Test:", test["name"])
    print("Input:", test["text"])

    start = time.perf_counter()

    try:
        result = translation_service.translate(
            text=test["text"],
            source_language=test["source"],
            target_language=test["target"]
        )

        elapsed = time.perf_counter() - start

        print("Output:", result)
        print(f"Time: {elapsed:.2f} seconds")
        print("Status: SUCCESS")

    except Exception as e:
        elapsed = time.perf_counter() - start

        print("Error:", str(e))
        print(f"Time: {elapsed:.2f} seconds")
        print("Status: FAILED")