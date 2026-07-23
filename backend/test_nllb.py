from backend.translation.nllb_service import nllb_service

print("Testing NLLB Translation...")

result = nllb_service.translate(
    text="नमस्ते",
    source_language="hindi",
    target_language="english"
)

print("Result:", result)