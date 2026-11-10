
import os
from pathlib import Path
import requests
class ExperimentalGPUTTS:
    def __init__(self,api_url=None,api_key=None,timeout=600):
        self.api_url=(api_url or os.getenv("GPU_TTS_URL","")).rstrip("/")
        self.api_key=api_key or os.getenv("GPU_TTS_API_KEY","")
        self.timeout=timeout
        self.output_dir=Path("experimental_outputs/manipuri_tts")
        self.output_dir.mkdir(parents=True,exist_ok=True)
    def generate(self,text,script="bengali",output_name="manipuri_gpu.wav"):
        if not self.api_url:
            raise ValueError("GPU_TTS_URL environment variable is not set.")
        if not self.api_key:
            raise ValueError("GPU_TTS_API_KEY environment variable is not set.")
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        model_input=text
        if script.lower() in ("meitei_mayek","manipuri_mtei"):
            from backend.translation.meitei_script_converter import convert_meitei_to_bengali
            model_input=convert_meitei_to_bengali(text)
        response=requests.post(self.api_url+"/generate",json={"text":model_input,"language":"manipuri"},headers={"Authorization":f"Bearer {self.api_key}","Accept":"audio/wav"},timeout=self.timeout)
        if response.status_code!=200:
            raise RuntimeError(f"GPU TTS API failed ({response.status_code}): {response.text[:1000]}")
        if "audio" not in response.headers.get("Content-Type","").lower():
            raise RuntimeError(f"Unexpected response type: {response.headers.get('Content-Type')}")
        output_path=self.output_dir/output_name
        output_path.write_bytes(response.content)
        return {"success":True,"input_script":script,"model_input":model_input,"audio_path":str(output_path.resolve()),"sample_rate":44100,"device":"remote_cuda","file_size_bytes":len(response.content)}