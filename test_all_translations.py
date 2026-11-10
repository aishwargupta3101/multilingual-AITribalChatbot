
from backend.services.translation_service import translation_service

TEST_TEXT = "Artificial intelligence is useful."

languages = sorted(translation_service.SUPPORTED_LANGUAGES)

passed = []
failed = []

print("\n===== TRIBAL AI: ALL-LANGUAGE TRANSLATION TEST =====\n")

for language in languages:
    if language == "english":
        continue

    try:
        result = translation_service.translate_response(
            text=TEST_TEXT,
            source_language="english",
            target_language=language,
        )

        if result and result.strip() and result.strip() != TEST_TEXT:
            passed.append(language)
            print(f"[PASS] {language}: {result}")
        else:
            failed.append((language, "Empty or unchanged output"))
            print(f"[FAIL] {language}: Empty or unchanged output")

    except Exception as exc:
        failed.append((language, str(exc)))
        print(f"[FAIL] {language}: {exc}")

print("\n===== SUMMARY =====")
print(f"Passed: {len(passed)}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nLanguages requiring attention:")
    for language, error in failed:
        print(f"- {language}: {error}")
