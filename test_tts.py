from backend.tts.manipuri_tts import manipuri_tts
text = "হ্যালো, আপনি কেমন আছেন?"
audio = manipuri_tts.text_to_speech(text)
print(audio)