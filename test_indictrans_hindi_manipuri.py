
from backend.translation.indictrans_service import indictrans_service

test_sentences = [
    "नमस्ते, आप कैसे हैं?",
    "कृत्रिम बुद्धिमत्ता क्या है?",
    "कृत्रिम बुद्धिमत्ता एक ऐसी तकनीक है जो कंप्यूटर को सोचने और सीखने में सक्षम बनाती है।"
]

targets = ["manipuri", "manipuri_mtei"]

for target in targets:
    print("\n" + "=" * 70)
    print("TARGET:", target.upper())

    for text in test_sentences:
        print("\nHINDI INPUT:", text)

        try:
            output = indictrans_service.translate(
                text=text,
                source_language="hindi",
                target_language=target
            )
            print("TRANSLATION:", output)

        except Exception as e:
            print("ERROR:", str(e))