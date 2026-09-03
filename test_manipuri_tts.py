from backend.tts.manipuri_tts import manipuri_tts

print("Starting Manipuri TTS test...")

audio_file = manipuri_tts.text_to_speech(
    "ꯅꯪꯒꯤ ꯃꯤꯡ ꯀꯔꯤꯅꯣ?"
)

print("SUCCESS")
print("Audio:", audio_file)