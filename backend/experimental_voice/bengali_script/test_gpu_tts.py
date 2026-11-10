
from backend.experimental_voice.bengali_script.gpu_tts import ExperimentalGPUTTS
tts=ExperimentalGPUTTS()
text="আর্টিফিসিএল ইন্তেলিজেন্সকী অপীকপা ৱাহন্থোক্না AI হায়বসি মীওইবগী ইন্তেলিজেন্স মথৌ তাবা থবকশিং।"
result=tts.generate(text,script="bengali",output_name="manipuri_gpu_integrated_test.wav")
print("Success:",result["success"])
print("Device:",result["device"])
print("Audio:",result["audio_path"])
print("File size:",result["file_size_bytes"],"bytes")