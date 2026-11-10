
from backend.translation.manipuri_bengali_service import manipuri_bengali_service

test_sentences = [
    "नमस्ते, आप कैसे हैं?",
    "कृत्रिम बुद्धिमत्ता क्या है?",
    "मेरा नाम अजय है।",
    "भारत एक विविधताओं वाला देश है।",
    "कंप्यूटर एक इलेक्ट्रॉनिक उपकरण है।",
    "आज मौसम बहुत अच्छा है।",
    "शिक्षा हर व्यक्ति के लिए महत्वपूर्ण है।"
]

for text in test_sentences:
    print("\n" + "=" * 70)
    print("HINDI INPUT:", text)

    try:
        output = manipuri_bengali_service.translate_hindi(text)
        print("MANIPURI BENGALI:", output)

    except Exception as e:
        print("TRANSLATION ERROR:", str(e))