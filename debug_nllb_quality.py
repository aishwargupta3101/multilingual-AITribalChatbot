
from backend.translation.nllb_service import nllb_service

tests = [
    ("মীতৈলোন্", "manipuri", "english"),
    ("মীতৈলোন্ অসী", "manipuri", "english"),
    ("Hello, how are you?", "english", "manipuri"),
    ("What is artificial intelligence?", "english", "manipuri"),
]

for text, source, target in tests:
    print("\n" + "=" * 55)
    print(f"{source} -> {target}")
    print("Input:", text)
    try:
        print("Output:", repr(nllb_service.translate(text, source, target)))
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
