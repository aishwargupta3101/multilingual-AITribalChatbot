
import csv
import re
import time
from pathlib import Path
import torch
from backend.experimental_voice.meitei_mayek.stt import ExperimentalMeiteiSTT, LANGUAGE_CODE, TARGET_SAMPLE_RATE
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_DIR = PROJECT_ROOT / "experimental_outputs" / "manipuri_dataset"
CSV_PATH = DATASET_DIR / "samples.csv"
RESULTS_PATH = DATASET_DIR / "decoder_comparison.csv"
def normalize_text(text):
    text = str(text or "").strip().lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())
def edit_distance(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for i, ref_char in enumerate(reference, 1):
        current = [i]
        for j, hyp_char in enumerate(hypothesis, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ref_char != hyp_char)))
        previous = current
    return previous[-1]
def calculate_wer(reference, hypothesis):
    ref = normalize_text(reference).split()
    hyp = normalize_text(hypothesis).split()
    if not ref:
        return 0.0 if not hyp else 100.0
    return edit_distance(ref, hyp) / len(ref) * 100
def calculate_cer(reference, hypothesis):
    ref = normalize_text(reference).replace(" ", "")
    hyp = normalize_text(hypothesis).replace(" ", "")
    if not ref:
        return 0.0 if not hyp else 100.0
    return edit_distance(ref, hyp) / len(ref) * 100
def load_dataset():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames:
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        required = {"audio_path", "reference_text"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain {required}. Found: {reader.fieldnames}")
        return list(reader)
def main():
    samples = load_dataset()
    if not samples:
        print("No samples found.")
        return
    print(f"Samples found: {len(samples)}")
    stt = ExperimentalMeiteiSTT()
    stt.load_model()
    results = []
    for index, row in enumerate(samples, 1):
        audio_name = (row.get("audio_path") or "").strip()
        reference = (row.get("reference_text") or "").strip()
        audio_path = Path(audio_name)
        if not audio_path.is_absolute():
            audio_path = DATASET_DIR / audio_path
        print(f"\n[{index}/{len(samples)}] {audio_path.name}")
        if not audio_path.exists():
            print("Audio file missing. Skipping.")
            continue
        waveform = stt.load_audio(audio_path)
        duration = waveform.shape[-1] / TARGET_SAMPLE_RATE
        for decoder in ("ctc", "rnnt"):
            try:
                start = time.perf_counter()
                with torch.inference_mode():
                    output = stt.model(waveform, LANGUAGE_CODE, decoder)
                elapsed = time.perf_counter() - start
                recognized = str(output).strip()
                wer = calculate_wer(reference, recognized)
                cer = calculate_cer(reference, recognized)
                rtf = elapsed / duration if duration else 0.0
                results.append({"audio_path": audio_name, "decoder": decoder, "reference_text": reference, "recognized_text": recognized, "wer": round(wer, 2), "cer": round(cer, 2), "inference_time": round(elapsed, 2), "audio_duration": round(duration, 2), "rtf": round(rtf, 3), "status": "success"})
                print(f"{decoder.upper()}: WER={wer:.2f}% | CER={cer:.2f}% | Time={elapsed:.2f}s | RTF={rtf:.3f}")
                print(f"Text: {recognized}")
            except Exception as error:
                print(f"{decoder.upper()} failed: {error}")
                results.append({"audio_path": audio_name, "decoder": decoder, "reference_text": reference, "recognized_text": "", "wer": "", "cer": "", "inference_time": "", "audio_duration": round(duration, 2), "rtf": "", "status": f"error: {error}"})
    successful = [item for item in results if item["status"] == "success"]
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8-sig", newline="") as file:
        fields = ["audio_path", "decoder", "reference_text", "recognized_text", "wer", "cer", "inference_time", "audio_duration", "rtf", "status"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print("\n========== DECODER COMPARISON ==========")
    for decoder in ("ctc", "rnnt"):
        rows = [item for item in successful if item["decoder"] == decoder]
        if not rows:
            print(f"{decoder.upper()}: No successful results.")
            continue
        avg_wer = sum(float(item["wer"]) for item in rows) / len(rows)
        avg_cer = sum(float(item["cer"]) for item in rows) / len(rows)
        avg_time = sum(float(item["inference_time"]) for item in rows) / len(rows)
        avg_rtf = sum(float(item["rtf"]) for item in rows) / len(rows)
        print(f"\n{decoder.upper()}:")
        print(f"Samples: {len(rows)}")
        print(f"Average WER: {avg_wer:.2f}%")
        print(f"Average CER: {avg_cer:.2f}%")
        print(f"Average inference: {avg_time:.2f}s")
        print(f"Average RTF: {avg_rtf:.3f}")
    print(f"\nResults saved to: {RESULTS_PATH}")
if __name__ == "__main__":
    main()