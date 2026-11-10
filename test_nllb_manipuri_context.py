from backend.translation.nllb_service import nllb_service
TEST_CASES = [
    "মীতৈলোন্",
    "মীতৈলোন্ অসী",
    "ꯃꯤꯇꯩꯂꯣꯟ",
    "ꯃꯤꯇꯩꯂꯣꯟ ꯑꯁꯤ"
]
for text in TEST_CASES:
    print("\n" + "=" * 60)
    print(f"Input: {text}")
    try:
        output = nllb_service.translate(text, "manipuri", "english")
        print(f"Output: {output}")
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")