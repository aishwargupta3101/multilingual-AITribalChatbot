
import csv
import re
import time
import unicodedata
from pathlib import Path
import torch
import torchaudio
from jiwer import wer,cer
from backend.experimental_voice.meitei_mayek.stt import ExperimentalMeiteiSTT,TARGET_SAMPLE_RATE
ROOT=Path(__file__).resolve().parents[3]
DATASET_DIR=ROOT/"experimental_outputs"/"manipuri_dataset"
CSV_PATH=DATASET_DIR/"samples.csv"
OUTPUT_PATH=DATASET_DIR/"audio_optimization_results.csv"
TEMP_DIR=DATASET_DIR/"optimization_temp"
def normalize_text(text):
    text=unicodedata.normalize("NFC",str(text or ""))
    text=text.replace("\u200c","").replace("\u200d","")
    text=re.sub(r"[^\w\s]"," ",text,flags=re.UNICODE)
    return re.sub(r"\s+"," ",text).strip().casefold()
def load_audio(path):
    waveform,sr=torchaudio.load(str(path))
    if waveform.shape[0]>1:
        waveform=waveform.mean(dim=0,keepdim=True)
    if sr!=TARGET_SAMPLE_RATE:
        waveform=torchaudio.functional.resample(waveform,sr,TARGET_SAMPLE_RATE)
    return waveform.float()
def normalize_audio(waveform):
    peak=waveform.abs().max()
    if peak>0:
        waveform=waveform*(0.95/peak)
    return waveform.clamp(-1.0,1.0)
def trim_silence(waveform,threshold_db=-40):
    if waveform.numel()==0:
        return waveform
    mask=waveform.abs().squeeze(0)>10**(threshold_db/20)
    if not mask.any():
        return waveform
    indices=torch.where(mask)[0]
    start=max(0,int(indices[0])-int(0.15*TARGET_SAMPLE_RATE))
    end=min(waveform.shape[-1],int(indices[-1])+int(0.15*TARGET_SAMPLE_RATE))
    return waveform[:,start:end]
def save_temp(waveform,name):
    path=TEMP_DIR/f"{name}.wav"
    torchaudio.save(str(path),waveform.cpu(),TARGET_SAMPLE_RATE)
    return path
def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing dataset CSV: {CSV_PATH}")
    TEMP_DIR.mkdir(parents=True,exist_ok=True)
    with open(CSV_PATH,"r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("samples.csv has no header")
        reader.fieldnames=[x.strip().lower() for x in reader.fieldnames]
        samples=list(reader)
    if not samples:
        raise ValueError("No samples found in samples.csv")
    stt=ExperimentalMeiteiSTT()
    print("Loading IndicConformer...")
    stt.load_model()
    variants=["original","normalized","trimmed","normalized_trimmed"]
    results=[]
    for i,row in enumerate(samples,1):
        audio_value=(row.get("audio_path") or "").strip()
        reference=(row.get("reference_text") or "").strip()
        if not audio_value or not reference:
            print(f"Skipping row {i}: missing audio or reference")
            continue

        audio_path = Path(audio_value)
        if not audio_path.is_absolute():
            audio_path = ROOT / audio_path
        if not audio_path.exists():
            candidates = [
                DATASET_DIR / "audio" / audio_path.name,
                ROOT / "experimental_outputs" / "manipuri_tts" / audio_path.name,
                DATASET_DIR / audio_path.name
            ]
            audio_path = next((p for p in candidates if p.exists()), audio_path)
        if not audio_path.exists():
            print(f"Skipping missing file: {audio_path}")
            continue
        original=load_audio(audio_path)
        normalized=normalize_audio(original.clone())
        trimmed=trim_silence(original.clone())
        normalized_trimmed=trim_silence(normalized.clone())
        audio_variants={"original":original,"normalized":normalized,"trimmed":trimmed,"normalized_trimmed":normalized_trimmed}
        print(f"\n[{i}/{len(samples)}] {audio_path.name}")
        for variant,waveform in audio_variants.items():
            temp_path=save_temp(waveform,f"sample_{i}_{variant}")
            try:
                start=time.perf_counter()
                output=stt.transcribe(str(temp_path))
                elapsed=time.perf_counter()-start
                prediction=output.get("text","")
                ref=normalize_text(reference)
                hyp=normalize_text(prediction)
                sample_wer=wer(ref,hyp) if ref else 0.0
                sample_cer=cer(ref,hyp) if ref else 0.0
                duration=waveform.shape[-1]/TARGET_SAMPLE_RATE
                results.append({"audio_file":audio_path.name,"variant":variant,"reference":reference,"prediction":prediction,"wer":round(sample_wer*100,2),"cer":round(sample_cer*100,2),"inference_seconds":round(elapsed,3),"audio_duration_seconds":round(duration,3),"rtf":round(elapsed/duration,3) if duration else 0})
                print(f"{variant}: WER={sample_wer*100:.2f}% CER={sample_cer*100:.2f}% Time={elapsed:.2f}s")
            except Exception as exc:
                print(f"{variant} failed: {exc}")
    if not results:
        raise RuntimeError("No results generated. Check audio paths and references.")
    with open(OUTPUT_PATH,"w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print("\n========== OPTIMIZATION SUMMARY ==========")
    for variant in variants:
        rows=[r for r in results if r["variant"]==variant]
        if rows:
            print(f"{variant}: WER={sum(r['wer'] for r in rows)/len(rows):.2f}% CER={sum(r['cer'] for r in rows)/len(rows):.2f}% Time={sum(r['inference_seconds'] for r in rows)/len(rows):.2f}s")
    print(f"\nSaved: {OUTPUT_PATH}")
if __name__=="__main__":
    main()