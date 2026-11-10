
from backend.translation.meitei_script_converter import meitei_script_converter
from backend.translation.nllb_service import nllb_service

samples = [
    "ꯃꯤꯇꯩꯂꯣꯟ",
    "ꯃꯩꯇꯩ",
    "ꯃꯤꯇꯩꯂꯣꯟ ꯑꯁꯤ",
]

for original in samples:
    print("\n" + "=" * 60)
    print("Original Meitei Mayek:", original)
    try:
        bengali = meitei_script_converter.convert_meitei_to_bengali(original)
        print("Converted Bengali:", repr(bengali))
        print("NLLB source code:", nllb_service._get_language_code("manipuri"))
        print("NLLB target code:", nllb_service._get_language_code("english"))
        translated = nllb_service.translate(
            bengali, "manipuri", "english"
        )
        print("English translation:", repr(translated))
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}")
