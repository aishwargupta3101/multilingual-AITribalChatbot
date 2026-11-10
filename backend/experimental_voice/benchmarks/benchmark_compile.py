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
    load_time = time.perf_counter() - start
    return model, tokenizer, description_tokenizer, load_time

def prepare_inputs(tokenizer, description_tokenizer):
    description_inputs = description_tokenizer(
        DESCRIPTION,
        return_tensors="pt"
    )
    prompt_inputs = tokenizer(
        TEXT,
        return_tensors="pt"
    )
    return description_inputs, prompt_inputs

def generate(
    model,
    description_inputs,
    prompt_inputs
):
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

def main():
    print("=" * 65)
    print("TORCH.COMPILE BENCHMARK")
    print("=" * 65)
    print(f"PyTorch version: {torch.__version__}")
    print(f"CPU threads: {torch.get_num_threads()}")
    print(f"CPU inter-op threads: {torch.get_num_interop_threads()}")
    print()

    print("Loading model...")
    model, tokenizer, description_tokenizer, load_time = load_model()

    print(f"Model load: {load_time:.2f}s")

    description_inputs, prompt_inputs = prepare_inputs(
        tokenizer,
        description_tokenizer
    )

    print("\nBASELINE")
    print("-" * 65)

    baseline_time, baseline_duration, baseline_rtf, _, _ = generate(
        model,
        description_inputs,
        prompt_inputs
    )

    print(f"Generation : {baseline_time:.2f}s")
    print(f"Audio      : {baseline_duration:.2f}s")
    print(f"RTF        : {baseline_rtf:.2f}x")

    print("\nCreating compiled model...")
    compile_start = time.perf_counter()

    try:
        compiled_model = torch.compile(
            model,
            mode="reduce-overhead"
        )
    except Exception as exc:
        print("\nTORCH.COMPILE FAILED")
        print(type(exc).__name__, str(exc))
        return

    compile_setup_time = time.perf_counter() - compile_start
    print(f"Compile setup: {compile_setup_time:.2f}s")

    print("\nCOMPILED RUN 1")
    print("-" * 65)

    try:
        run1_time, run1_duration, run1_rtf, audio1, sample_rate1 = generate(
            compiled_model,
            description_inputs,
            prompt_inputs
        )

        print(f"Generation : {run1_time:.2f}s")
        print(f"Audio      : {run1_duration:.2f}s")
        print(f"RTF        : {run1_rtf:.2f}x")

    except Exception as exc:
        print("\nCOMPILED RUN 1 FAILED")
        print(type(exc).__name__, str(exc))
        return

    print("\nCOMPILED RUN 2")
    print("-" * 65)

    try:
        run2_time, run2_duration, run2_rtf, audio2, sample_rate2 = generate(
            compiled_model,
            description_inputs,
            prompt_inputs
        )

        print(f"Generation : {run2_time:.2f}s")
        print(f"Audio      : {run2_duration:.2f}s")
        print(f"RTF        : {run2_rtf:.2f}x")

    except Exception as exc:
        print("\nCOMPILED RUN 2 FAILED")
        print(type(exc).__name__, str(exc))
        return

    print("\nCOMPILED RUN 3")
    print("-" * 65)

    try:
        run3_time, run3_duration, run3_rtf, audio3, sample_rate3 = generate(
            compiled_model,
            description_inputs,
            prompt_inputs
        )

        print(f"Generation : {run3_time:.2f}s")
        print(f"Audio      : {run3_duration:.2f}s")
        print(f"RTF        : {run3_rtf:.2f}x")

    except Exception as exc:
        print("\nCOMPILED RUN 3 FAILED")
        print(type(exc).__name__, str(exc))
        return

    output_path = OUTPUT_DIR / "compile_test.wav"
    sf.write(str(output_path), audio3, sample_rate3)

    average_compiled = (
        run2_time + run3_time
    ) / 2

    improvement = (
        (baseline_time - average_compiled)
        / baseline_time
    ) * 100

    print("\n" + "=" * 65)
    print("FINAL RESULT")
    print("=" * 65)
    print(f"Baseline generation : {baseline_time:.2f}s")
    print(f"Compile run 1       : {run1_time:.2f}s")
    print(f"Compile run 2       : {run2_time:.2f}s")
    print(f"Compile run 3       : {run3_time:.2f}s")
    print(f"Average steady state: {average_compiled:.2f}s")
    print(f"Improvement         : {improvement:.2f}%")
    print(f"Output              : {output_path}")
    print("=" * 65)

    del compiled_model
    del model
    gc.collect()

if __name__ == "__main__":
    main()