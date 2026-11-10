
from backend.translation.indictrans_service import indictrans_service

tests = [
    {
        "name": "English to Manipuri Bengali",
        "text": "Hello, how are you?",
        "source": "english",
        "target": "manipuri",
        "expected_script": "bengali"
    },
    {
        "name": "English to Manipuri Mayek",
        "text": "Hello, how are you?",
        "source": "english",
        "target": "manipuri_mtei",
        "expected_script": "mayek"
    },
    {
        "name": "Hindi to Manipuri Bengali",
        "text": "नमस्ते, आप कैसे हैं?",
        "source": "hindi",
        "target": "manipuri",
        "expected_script": "bengali"
    },
    {
        "name": "Hindi to Manipuri Mayek",
        "text": "नमस्ते, आप कैसे हैं?",
        "source": "hindi",
        "target": "manipuri_mtei",
        "expected_script": "mayek"
    },
    {
        "name": "Manipuri Mayek to English",
        "text": "ꯍꯦꯂꯣ, ꯅꯍꯥꯛꯅ ꯀꯔꯝ ꯇꯧꯒꯦ?",
        "source": "manipuri_mtei",
        "target": "english",
        "expected_script": "latin"
    }
]

def detect_script(text):
    counts = {
        "bengali": 0,
        "mayek": 0,
        "devanagari": 0,
        "latin": 0
    }

    for char in text:
        code = ord(char)

        if 0x0980 <= code <= 0x09FF:
            counts["bengali"] += 1
        elif 0xABC0 <= code <= 0xABFF:
            counts["mayek"] += 1
        elif 0x0900 <= code <= 0x097F:
            counts["devanagari"] += 1
        elif ("A" <= char <= "Z") or ("a" <= char <= "z"):
            counts["latin"] += 1

    return max(counts, key=counts.get) if any(counts.values()) else "unknown"

passed = 0
failed = 0

for test in tests:
    print("\n" + "=" * 60)
    print(test["name"])
    print("=" * 60)

    try:
        result = indictrans_service.translate(
            text=test["text"],
            source_language=test["source"],
            target_language=test["target"]
        )

        result = str(result).strip()
        actual_script = detect_script(result)
        expected_script = test["expected_script"]

        print("Input :", test["text"])
        print("Output:", result)
        print("Expected script:", expected_script)
        print("Detected script:", actual_script)

        if not result:
            print("STATUS: FAILED - Empty translation")
            failed += 1
        elif actual_script == expected_script:
            print("STATUS: PASSED")
            passed += 1
        else:
            print("STATUS: FAILED - Script mismatch")
            failed += 1

    except Exception as error:
        print("ERROR:", error)
        failed += 1

print("\n" + "=" * 60)
print("FINAL TEST SUMMARY")
print("=" * 60)
print("Passed:", passed)
print("Failed:", failed)
print("Total :", passed + failed)