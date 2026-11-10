
import time
from pathlib import Path

import torch
import torchaudio
from transformers import AutoModel


MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"
TARGET_SAMPLE_RATE = 16000
LANGUAGE_CODE = "mni"

def load_audio(audio_path):
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )
    waveform, sample_rate = torchaudio.load(str(audio_path))
    if waveform.shape[0] > 1:
        waveform = torch.mean(
            waveform,
            dim=0,
            keepdim=True
        )
    if sample_rate != TARGET_SAMPLE_RATE:
        resampler = torchaudio.transforms.Resample(
            orig_freq=sample_rate,
            new_freq=TARGET_SAMPLE_RATE
        )
        waveform = resampler(waveform)
    return waveform

def main():
    total_start = time.perf_counter()
    print("=" * 60)
    print("INDICCONFORMER MANIPURI STT PERFORMANCE TEST")
    print("=" * 60)
    audio_path = input(
        "Enter full audio file path: "
    ).strip().strip('"')
    print("\nLoading audio...")
    audio_start = time.perf_counter()
    waveform = load_audio(audio_path)
    audio_load_time = time.perf_counter() - audio_start
    audio_duration = (
        waveform.shape[-1] / TARGET_SAMPLE_RATE
    )
    print("Audio loaded successfully.")
    print("Waveform shape:", waveform.shape)
    print(f"Audio duration: {audio_duration:.2f} seconds")
    print(f"Audio loading time: {audio_load_time:.2f} seconds")
    print("\nLoading IndicConformer model...")
    print("The first download may take several minutes.")
    model_start = time.perf_counter()
    model = AutoModel.from_pretrained(
        MODEL_ID,
        trust_remote_code=True
    )
    model.eval()
    model_load_time = time.perf_counter() - model_start
    print("\nModel loaded successfully.")
    print(f"Model loading time: {model_load_time:.2f} seconds")
    results = {}
    timings = {}
    for decoding_method in ["ctc", "rnnt"]:
        print(f"\nRunning {decoding_method.upper()} decoding...")
        inference_start = time.perf_counter()
        try:
            with torch.inference_mode():
                transcription = model(
                    waveform,
                    LANGUAGE_CODE,
                    decoding_method
                )
            inference_time = (
                time.perf_counter() - inference_start
            )
            results[decoding_method] = str(transcription)
            timings[decoding_method] = inference_time
            rtf = inference_time / audio_duration
            print(f"\n{decoding_method.upper()} result:")
            print(transcription)
            print(
                f"{decoding_method.upper()} inference time: "
                f"{inference_time:.2f} seconds"
            )
            print(
                f"{decoding_method.upper()} RTF: "
                f"{rtf:.3f}"
            )
        except Exception as error:
            timings[decoding_method] = None
            results[decoding_method] = (
                f"ERROR: {error}"
            )
            print(
                f"{decoding_method.upper()} failed: "
                f"{error}"
            )
    total_time = time.perf_counter() - total_start
    print("\n" + "=" * 60)
    print("FINAL COMPARISON")
    print("=" * 60)
    print("\nCTC:")
    print(results.get("ctc", "Not available"))
    print("\nRNNT:")
    print(results.get("rnnt", "Not available"))
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Audio duration: {audio_duration:.2f} seconds")
    print(f"Audio loading: {audio_load_time:.2f} seconds")
    print(f"Model loading: {model_load_time:.2f} seconds")
    for method in ["ctc", "rnnt"]:
        inference_time = timings.get(method)
        if inference_time is not None:
            rtf = inference_time / audio_duration
            print(
                f"{method.upper()} inference: "
                f"{inference_time:.2f} seconds"
            )
            print(
                f"{method.upper()} RTF: {rtf:.3f}"
            )
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    print("\nExperiment completed.")
if __name__ == "__main__":
    main()