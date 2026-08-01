from backend.translation.nllb_service import nllb_service
text = nllb_service.translate(
    text="Hello, how are you?",
    source_language="english",
    target_language="manipuri"
)
print(text)