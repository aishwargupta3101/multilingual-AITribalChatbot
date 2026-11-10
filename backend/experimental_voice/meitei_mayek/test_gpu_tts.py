from backend.experimental_voice.bengali_script.gpu_tts import ExperimentalGPUTTS
tts=ExperimentalGPUTTS()
text="ꯑꯥꯏ ꯑꯁꯤ ꯃꯤꯑꯣꯏꯕꯒꯤ ꯃꯊꯧ ꯇꯥꯕꯥ ꯊꯕꯛ ꯑꯃꯅꯤ।"
result=tts.generate(text,script="meitei_mayek",output_name="manipuri_meitei_gpu_test.wav")
print("Success:",result["success"])
print("Device:",result["device"])
print("Audio:",result["audio_path"])