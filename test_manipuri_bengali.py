
from backend.translation.nllb_service import nllb_service

samples = [
    "Artificial intelligence is a branch of computer science.",
    "Machine learning helps computers learn patterns from data.",
    "Students can use this assistant to learn about education and government scholarships."
]

for text in samples:
    print("\nENGLISH:", text)
    try:
        translated = nllb_service.translate(
            text=text,
            source_language="english",
            target_language="manipuri"
        )
        print("MANIPURI BENGALI:", translated)
    except Exception as exc:
        print("ERROR:", repr(exc))
