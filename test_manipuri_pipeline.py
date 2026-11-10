from backend.translation.meitei_script_converter import meitei_script_converter
from backend.translation.nllb_service import nllb_service
TEST_CASES = ["ꯃꯤꯇꯩꯂꯣꯟ", "ꯃꯩꯇꯩ", "ꯃꯤꯇꯩꯂꯣꯟ ꯑꯁꯤ"]
for text in TEST_CASES:
    print("\n" + "=" * 60)
    print(f"Original Meitei Mayek: {text}")
    try:
        bengali_text = meitei_script_converter.convert_meitei_to_bengali(text)
        print(f"Converted Bengali: {bengali_text}")
        english_text = nllb_service.translate(bengali_text, "manipuri", "english")
        print(f"Translated English: {english_text}")
    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")