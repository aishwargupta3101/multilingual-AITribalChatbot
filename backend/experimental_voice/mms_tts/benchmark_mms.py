import time
from pathlib import Path
import soundfile as sf
import torch
from transformers import VitsModel, AutoTokenizer

MODEL_ID = "facebook/mms-tts-mni"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "mms_tts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEXT = "ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯋꯥꯍꯪ ꯑꯃꯥ ꯍꯥꯏꯖꯕꯥ ꯑꯃꯥ ꯍꯥꯏꯖꯒꯅꯤ꯫"

def main():
    print("=" * 60)
    print("MMS MANIPURI TTS BENCHMARK")
    print("=" * 60)
    print(f"Model: {MODEL_ID}")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    print("\nLoading tokenizer...")
    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer_time = time.perf_counter() - start
    print(f"Tokenizer loaded: {tokenizer_time:.2f}s")

    print("\nLoading VITS model...")
    start = time.perf_counter()
    model = VitsModel.from_pretrained(MODEL_ID)
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    model_load_time = time.perf_counter() - start
    print(f"Model loaded: {model_load_time:.2f}s")

    device = next(model.parameters()).device

    print("\nTokenizing...")
    inputs = tokenizer(TEXT, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    print("\nGenerating speech...")
    start = time.perf_counter()

    with torch.inference_mode():
        output = model(**inputs).waveform

    if device.type == "cuda":
        torch.cuda.synchronize()

    generation_time = time.perf_counter() - start

    audio = output.squeeze().cpu().numpy()
    sample_rate = model.config.sampling_rate
    duration = len(audio) / sample_rate
    rtf = generation_time / duration if duration > 0 else 0

    output_path = OUTPUT_DIR / "mms_manipuri_test.wav"
    sf.write(str(output_path), audio, sample_rate)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Model load      : {model_load_time:.2f}s")
    print(f"Generation      : {generation_time:.2f}s")
    print(f"Audio duration  : {duration:.2f}s")
    print(f"RTF             : {rtf:.2f}x")
    print(f"Audio speed     : {duration / generation_time:.4f}x realtime")
    print(f"Sample rate     : {sample_rate}")
    print(f"Output          : {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()