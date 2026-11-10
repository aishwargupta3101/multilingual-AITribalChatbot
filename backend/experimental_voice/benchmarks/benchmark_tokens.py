import gc
import os
import time
from pathlib import Path
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

MODEL_ID = "ai4bharat/indic-parler-tts"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "benchmarks"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEXT = "ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯋꯥꯍꯪ ꯑꯃꯥ ꯍꯥꯏꯖꯕꯥ ꯑꯃꯥ ꯍꯥꯏꯖꯒꯅꯤ꯫"
DESCRIPTION = (
    "Ranjit's voice speaks in Manipuri. "
    "The speech is clear, natural, and moderately paced. "
    "The recording is very clear with minimal background noise."
)

TOKEN_LIMITS = [1024, 768, 512, 384]

CPU_THREADS = min(8, os.cpu_count() or 4)
torch.set_num_threads(CPU_THREADS)
torch.set_num_interop_threads(1)

def load_model():
    start = time.perf_counter()
    model = ParlerTTSForConditionalGeneration.from_pretrained(
        MODEL_ID
    ).to("cpu")
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    description_tokenizer = AutoTokenizer.from_pretrained(
        model.config.text_encoder._name_or_path
    )

    return (
        model,
        tokenizer,
        description_tokenizer,
        time.perf_counter() - start
    )

def generate(model, description_inputs, prompt_inputs, max_new_tokens):
    start = time.perf_counter()
    with torch.inference_mode():
        generation = model.generate(
            input_ids=description_inputs.input_ids,
            attention_mask=description_inputs.attention_mask,
            prompt_input_ids=prompt_inputs.input_ids,
            prompt_attention_mask=prompt_inputs.attention_mask,
            max_new_tokens=max_new_tokens,
        )
    generation_time = time.perf_counter() - start
    audio = generation.float().cpu().numpy().squeeze()
    sample_rate = model.config.sampling_rate
    duration = len(audio) / sample_rate
    rtf = generation_time / duration if duration > 0 else 0
    return generation_time, duration, rtf, audio, sample_rate
def main():
    print("=" * 65)
    print("MAX NEW TOKENS BENCHMARK")
    print("=" * 65)
    print(f"CPU threads: {torch.get_num_threads()}")
    print()

    print("Loading model...")
    model, tokenizer, description_tokenizer, load_time = load_model()
    print(f"Model load: {load_time:.2f}s")

    description_inputs = description_tokenizer(
        DESCRIPTION,
        return_tensors="pt"
    )

    prompt_inputs = tokenizer(
        TEXT,
        return_tensors="pt"
    )

    results = []

    for limit in TOKEN_LIMITS:
        print("\n" + "=" * 65)
        print(f"TEST: max_new_tokens = {limit}")
        print("=" * 65)

        try:
            generation_time, duration, rtf, audio, sample_rate = generate(
                model,
                description_inputs,
                prompt_inputs,
                limit
            )

            output_path = OUTPUT_DIR / f"tokens_{limit}.wav"
            sf.write(str(output_path), audio, sample_rate)

            print(f"Generation : {generation_time:.2f}s")
            print(f"Audio      : {duration:.2f}s")
            print(f"RTF        : {rtf:.2f}x")
            print(f"Output     : {output_path}")

            results.append({
                "tokens": limit,
                "generation": generation_time,
                "duration": duration,
                "rtf": rtf,
                "path": str(output_path)
            })

        except Exception as exc:
            print(f"FAILED: {type(exc).__name__}: {exc}")

    print("\n" + "=" * 65)
    print("FINAL COMPARISON")
    print("=" * 65)

    baseline = None

    for result in results:
        if result["tokens"] == 1024:
            baseline = result
            break

    print(
        f"{'TOKENS':>8} | "
        f"{'GENERATION':>12} | "
        f"{'AUDIO':>8} | "
        f"{'RTF':>8}"
    )
    print("-" * 65)

    for result in results:
        print(
            f"{result['tokens']:>8} | "
            f"{result['generation']:>10.2f}s | "
            f"{result['duration']:>6.2f}s | "
            f"{result['rtf']:>6.2f}x"
        )

    if baseline:
        print("\nRelative to 1024 tokens:")

        for result in results:
            if result["tokens"] == 1024:
                continue

            improvement = (
                (baseline["generation"] - result["generation"])
                / baseline["generation"]
            ) * 100

            print(
                f"{result['tokens']} tokens: "
                f"{improvement:+.2f}% generation-time change"
            )

    print("\nListen to the generated WAV files before choosing a limit.")

    del model
    gc.collect()

if __name__ == "__main__":
    main()