from backend.translation.indictrans_service import indictrans_service

test_sentences = [
    "Hello, how are you?",
    "What is artificial intelligence?",
    "Artificial intelligence is a technology that enables computers to think and learn."
]

for text in test_sentences:
    print("\n" + "=" * 70)
    print("ENGLISH:", text)

    try:
        result = indictrans_service.translate(
            text=text,
            source_language="english",
            target_language="manipuri_mtei"
        )
        print("MEITEI MAYEK:", result)

    except Exception as e:
        print("ERROR:", str(e))