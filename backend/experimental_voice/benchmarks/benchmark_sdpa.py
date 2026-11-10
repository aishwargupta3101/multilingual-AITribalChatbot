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
MAX_NEW_TOKENS = 1024
TEXT = "ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯋꯥꯍꯪ ꯑꯃꯥ ꯍꯥꯏꯖꯕꯥ ꯑꯃꯥ ꯍꯥꯏꯖꯒꯅꯤ꯫"
DESCRIPTION = (
    "Ranjit's voice speaks in Manipuri. "
    "The speech is clear, natural, and moderately paced. "
    "The recording is very clear with minimal background noise."
)

CPU_THREADS = min(8, os.cpu_count() or 4)
torch.set_num_threads(CPU_THREADS)
torch.set_num_interop_threads(1)

def load_model(attn_implementation=None):
    start = time.perf_counter()
    kwargs = {}
    if attn_implementation:
        kwargs["attn_implementation"] = attn_implementation
    model = ParlerTTSForConditionalGeneration.from_pretrained(
        MODEL_ID,
        **kwargs
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

def generate_once(model, tokenizer, description_tokenizer):
    description_inputs = description_tokenizer(
        DESCRIPTION,
        return_tensors="pt"
    )
    prompt_inputs = tokenizer(
        TEXT,
        return_tensors="pt"
    )

    start = time.perf_counter()

    with torch.inference_mode():
        generation = model.generate(
            input_ids=description_inputs.input_ids,
            attention_mask=description_inputs.attention_mask,
            prompt_input_ids=prompt_inputs.input_ids,
            prompt_attention_mask=prompt_inputs.attention_mask,
            max_new_tokens=MAX_NEW_TOKENS,
        )

    generation_time = time.perf_counter() - start
    audio = generation.float().cpu().numpy().squeeze()
    sample_rate = model.config.sampling_rate
    duration = len(audio) / sample_rate
    rtf = generation_time / duration if duration > 0 else 0

    return generation_time, duration, rtf, audio, sample_rate

def run_test(name, attn_implementation=None):
    print("\n" + "=" * 60)
    print(f"TEST: {name}")
    print("=" * 60)

    model, tokenizer, description_tokenizer, load_time = load_model(
        attn_implementation
    )

    print(f"Model load time: {load_time:.2f}s")
    print(f"Attention implementation: {attn_implementation or 'default'}")

    print("\nWarm-up generation...")
    warmup_time, warmup_duration, _, _, _ = generate_once(
        model,
        tokenizer,
        description_tokenizer
    )

    print(
        f"Warm-up: {warmup_time:.2f}s "
        f"for {warmup_duration:.2f}s audio"
    )

    print("\nMeasured generation...")
    generation_time, duration, rtf, audio, sample_rate = generate_once(
        model,
        tokenizer,
        description_tokenizer
    )

    output_path = OUTPUT_DIR / f"{name}.wav"
    sf.write(str(output_path), audio, sample_rate)

    print("\nRESULT")
    print(f"Generation time : {generation_time:.2f}s")
    print(f"Audio duration   : {duration:.2f}s")
    print(f"RTF              : {rtf:.2f}x")
    print(f"Audio speed      : {duration / generation_time:.4f}x realtime")
    print(f"Output           : {output_path}")

    del model
    del tokenizer
    del description_tokenizer
    gc.collect()

    return {
        "name": name,
        "load": load_time,
        "generation": generation_time,
        "duration": duration,
        "rtf": rtf,
    }

def main():
    print("Indic Parler-TTS SDPA Benchmark")
    print(f"CPU threads: {torch.get_num_threads()}")
    print(f"CPU inter-op threads: {torch.get_num_interop_threads()}")

    results = []

    results.append(
        run_test(
            "baseline",
            None
        )
    )

    results.append(
        run_test(
            "sdpa",
            "sdpa"
        )
    )

    print("\n" + "=" * 60)
    print("FINAL COMPARISON")
    print("=" * 60)

    for result in results:
        print(
            f"{result['name']:10} | "
            f"generation={result['generation']:.2f}s | "
            f"audio={result['duration']:.2f}s | "
            f"RTF={result['rtf']:.2f}x"
        )

    baseline = results[0]
    sdpa = results[1]

    improvement = (
        (baseline["generation"] - sdpa["generation"])
        / baseline["generation"]
    ) * 100

    print(
        f"\nSDPA generation improvement: "
        f"{improvement:.2f}%"
    )

if __name__ == "__main__":
    main()