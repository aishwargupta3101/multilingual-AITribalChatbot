
import csv
import re
import time
from pathlib import Path
from backend.experimental_voice.meitei_mayek.stt import ExperimentalMeiteiSTT
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_DIR = PROJECT_ROOT / "experimental_outputs" / "manipuri_dataset"
CSV_PATH = DATASET_DIR / "samples.csv"
RESULTS_PATH = DATASET_DIR / "evaluation_results.csv"
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
    ref_words = normalize_text(reference).split()
    hyp_words = normalize_text(hypothesis).split()
    if not ref_words:
        return 0.0 if not hyp_words else 100.0
    return edit_distance(ref_words, hyp_words) / len(ref_words) * 100
def calculate_cer(reference, hypothesis):
    ref_chars = normalize_text(reference).replace(" ", "")
    hyp_chars = normalize_text(hypothesis).replace(" ", "")
    if not ref_chars:
        return 0.0 if not hyp_chars else 100.0
    return edit_distance(ref_chars, hyp_chars) / len(ref_chars) * 100
def load_samples():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset CSV not found: {CSV_PATH}")
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames:
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        required = {"audio_path", "reference_text"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain columns: {required}. Found: {reader.fieldnames}")
        return list(reader)
def main():
    samples = load_samples()
    if not samples:
        print("No samples found in the dataset.")
        return
    print(f"Dataset samples found: {len(samples)}")
    print("Loading IndicConformer once...")
    stt = ExperimentalMeiteiSTT()
    stt.load_model()
    results = []
    total_inference = 0.0
    for index, row in enumerate(samples, 1):
        audio_name = (row.get("audio_path") or "").strip()
        reference = (row.get("reference_text") or "").strip()
        audio_path = Path(audio_name)
        if not audio_path.is_absolute():
            audio_path = DATASET_DIR / audio_path
        print(f"\n[{index}/{len(samples)}] Processing: {audio_path.name}")
        if not audio_path.exists():
            print(f"SKIPPED: Audio file not found: {audio_path}")
            results.append({"audio_path": audio_name, "reference_text": reference, "recognized_text": "", "wer": "", "cer": "", "inference_time": "", "status": "missing_audio"})
            continue
        try:
            output = stt.transcribe(str(audio_path))
            recognized = output.get("text", "")
            inference_time = float(output.get("inference_time", 0))
            wer = calculate_wer(reference, recognized)
            cer = calculate_cer(reference, recognized)
            total_inference += inference_time
            results.append({"audio_path": audio_name, "reference_text": reference, "recognized_text": recognized, "wer": round(wer, 2), "cer": round(cer, 2), "inference_time": round(inference_time, 2), "status": "success"})
            print(f"WER: {wer:.2f}% | CER: {cer:.2f}% | Time: {inference_time:.2f}s")
        except Exception as error:
            print(f"ERROR: {error}")
            results.append({"audio_path": audio_name, "reference_text": reference, "recognized_text": "", "wer": "", "cer": "", "inference_time": "", "status": f"error: {error}"})
    successful = [r for r in results if r["status"] == "success"]
    if successful:
        average_wer = sum(float(r["wer"]) for r in successful) / len(successful)
        average_cer = sum(float(r["cer"]) for r in successful) / len(successful)
        average_time = sum(float(r["inference_time"]) for r in successful) / len(successful)
    else:
        average_wer = average_cer = average_time = 0.0
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["audio_path", "reference_text", "recognized_text", "wer", "cer", "inference_time", "status"])
        writer.writeheader()
        writer.writerows(results)
    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total samples: {len(samples)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed or skipped: {len(samples) - len(successful)}")
    print(f"Average WER: {average_wer:.2f}%")
    print(f"Average CER: {average_cer:.2f}%")
    print(f"Average inference time: {average_time:.2f}s")
    print(f"Total inference time: {total_inference:.2f}s")
    print(f"Results saved to: {RESULTS_PATH}")
if __name__ == "__main__":
    main()