
"""
Experimental Manipuri TTS with performance measurement.
This module is separate from the production TTS service.
Supports Bengali script and Meitei Mayek (converted to Bengali).
"""
import logging
import time
from pathlib import Path
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)
import os
CPU_THREADS = min(8, os.cpu_count() or 4)
torch.set_num_threads(CPU_THREADS)
torch.set_num_interop_threads(1)
print(f"Configured CPU threads: {CPU_THREADS}")
MODEL_ID = "ai4bharat/indic-parler-tts"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "experimental_outputs" / "manipuri_tts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAX_NEW_TOKENS = 1024

class ExperimentalManipuriTTS:
    _shared_model = None
    _shared_tokenizer = None
    _shared_description_tokenizer = None
    _shared_device = None

    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = ExperimentalManipuriTTS._shared_model
        self.tokenizer = ExperimentalManipuriTTS._shared_tokenizer
        self.description_tokenizer = ExperimentalManipuriTTS._shared_description_tokenizer

    def load_model(self):
        """Load model once and reuse it across instances."""
        if self.model is not None and ExperimentalManipuriTTS._shared_device == self.device:
            return 0.0

        start = time.perf_counter()
        print(f"Loading model: {MODEL_ID}")
        print(f"Device: {self.device}")

        model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID).to(self.device)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
        model.eval()

        print("\n========== MODEL CONFIGURATION ==========")
        print("CPU threads:", torch.get_num_threads())
        print("CPU interop threads:", torch.get_num_interop_threads())
        print("Sampling rate:", model.config.sampling_rate)
        print("Configured max new tokens:", model.generation_config.max_new_tokens)
        print("Configured max length:", model.generation_config.max_length)
        print("Do sample:", model.generation_config.do_sample)
        print("Temperature:", model.generation_config.temperature)
        print("Generation limit used:", MAX_NEW_TOKENS)
        print("=========================================")

        ExperimentalManipuriTTS._shared_model = model
        ExperimentalManipuriTTS._shared_tokenizer = tokenizer
        ExperimentalManipuriTTS._shared_description_tokenizer = description_tokenizer
        ExperimentalManipuriTTS._shared_device = self.device
        self.model = model
        self.tokenizer = tokenizer
        self.description_tokenizer = description_tokenizer

        elapsed = time.perf_counter() - start
        print(f"Model loaded successfully in {elapsed:.2f} seconds.")
        return elapsed

    def generate(self, text: str, script: str, output_name: str) -> dict:
        total_start = time.perf_counter()
        text = (text or "").strip()
        script = (script or "").lower().strip()

        if not text:
            return {"success": False, "error": "Input text is empty."}
        if script not in {"bengali", "meitei_mayek"}:
            return {"success": False, "error": "Script must be bengali or meitei_mayek."}
        if not output_name or Path(output_name).name != output_name or Path(output_name).suffix.lower() != ".wav":
            return {"success": False, "error": "Output name must be a valid WAV filename."}

        try:
            conversion_start = time.perf_counter()
            if script == "meitei_mayek":
                from backend.translation.meitei_script_converter import convert_meitei_to_bengali
                model_text = convert_meitei_to_bengali(text)
                if not model_text:
                    return {"success": False, "error": "Script conversion returned empty text."}
            else:
                model_text = text

            conversion_time = time.perf_counter() - conversion_start
            print("\nInput script:", script)
            print("Text sent to model:", model_text)

            load_time = self.load_model()
            description = (
                "Ranjit's voice speaks in Manipuri. "
                "The speech is clear, natural, and moderately paced. "
                "The recording is very clear with minimal background noise."
            )

            tokenization_start = time.perf_counter()
            description_inputs = self.description_tokenizer(description, return_tensors="pt").to(self.device)
            prompt_inputs = self.tokenizer(model_text, return_tensors="pt").to(self.device)
            tokenization_time = time.perf_counter() - tokenization_start

            generation_start = time.perf_counter()
            with torch.inference_mode():
                generation = self.model.generate(
                    input_ids=description_inputs.input_ids,
                    attention_mask=description_inputs.attention_mask,
                    prompt_input_ids=prompt_inputs.input_ids,
                    prompt_attention_mask=prompt_inputs.attention_mask,
                    max_new_tokens=MAX_NEW_TOKENS,
                )

            if self.device.startswith("cuda"):
                torch.cuda.synchronize()

            generation_time = time.perf_counter() - generation_start
            audio = generation.float().cpu().numpy().squeeze()
            sample_rate = self.model.config.sampling_rate
            audio_duration = len(audio) / sample_rate
            generation_speed = audio_duration / generation_time if generation_time > 0 else 0

            print(f"Generated tensor shape: {tuple(generation.shape)}")
            print(f"Generated audio duration: {audio_duration:.2f}s")
            print(f"Generation speed: {generation_speed:.4f} audio-seconds per processing-second")

            output_path = OUTPUT_DIR / output_name
            save_start = time.perf_counter()
            sf.write(str(output_path), audio, sample_rate)
            save_time = time.perf_counter() - save_start
            total_time = time.perf_counter() - total_start

            print("\n========== TTS PERFORMANCE ==========")
            print(f"Script conversion: {conversion_time:.2f}s")
            print(f"Model loading:     {load_time:.2f}s")
            print(f"Tokenization:      {tokenization_time:.2f}s")
            print(f"Audio generation:  {generation_time:.2f}s")
            print(f"Audio saving:      {save_time:.2f}s")
            print(f"Total:             {total_time:.2f}s")
            print("=====================================")

            return {
                "success": True,
                "input_script": script,
                "model_input": model_text,
                "audio_path": str(output_path),
                "sample_rate": sample_rate,
                "device": self.device,
                "timings": {
                    "conversion_seconds": round(conversion_time, 2),
                    "model_load_seconds": round(load_time, 2),
                    "tokenization_seconds": round(tokenization_time, 2),
                    "generation_seconds": round(generation_time, 2),
                    "save_seconds": round(save_time, 2),
                    "total_seconds": round(total_time, 2),
                },
            }

        except Exception as exc:
            logger.exception("Experimental TTS failed.")
            return {"success": False, "error": str(exc)}

if __name__ == "__main__":
    tts = ExperimentalManipuriTTS()
    print("\nExperimental Manipuri TTS")
    print("1. Bengali script")
    print("2. Meitei Mayek")

    choice = input("Choose input script (1/2): ").strip()
    if choice == "1":
        script = "bengali"
    elif choice == "2":
        script = "meitei_mayek"
    else:
        print("Invalid selection.")
        raise SystemExit(1)

    text = input("\nEnter a Manipuri sentence in the selected script: ").strip()
    result = tts.generate(
        text=text,
        script=script,
        output_name="manipuri_optimized_test.wav",
    )

    print("\n========== RESULT ==========")
    for key, value in result.items():
        print(f"{key}: {value}")
    print("============================")