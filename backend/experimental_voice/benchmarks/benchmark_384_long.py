import gc
import os
import time
from pathlib import Path
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

MODEL_ID="ai4bharat/indic-parler-tts"
OUTPUT_DIR=Path(__file__).resolve().parents[2]/"outputs"/"benchmarks"
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)
TEXT="ꯑꯩ ꯃꯤꯇꯩ ꯂꯣꯟꯗꯥ ꯋꯥꯍꯪ ꯑꯃꯥ ꯍꯥꯏꯖꯕꯥ ꯑꯃꯥ ꯍꯥꯏꯖꯒꯅꯤ꯫ ꯑꯩ ꯁꯤꯖꯤꯟꯅꯗꯨꯅꯥ ꯌꯥꯝ ꯐꯖꯅꯥ ꯋꯥꯍꯪ ꯉꯥꯡꯖꯒꯅꯤ ꯫"
DESCRIPTION=("Ranjit's voice speaks in Manipuri. The speech is clear, natural, "
              "and moderately paced. The recording is very clear with minimal background noise.")

torch.set_num_threads(min(8,os.cpu_count() or 4))
torch.set_num_interop_threads(1)

def main():
    print("="*60)
    print("384 vs 512 LONG-SENTENCE TEST")
    print("="*60)
    start=time.perf_counter()
    model=ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID).to("cpu")
    model.eval()
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID)
    description_tokenizer=AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
    print(f"Model load: {time.perf_counter()-start:.2f}s")

    description_inputs=description_tokenizer(DESCRIPTION,return_tensors="pt")
    prompt_inputs=tokenizer(TEXT,return_tensors="pt")

    results=[]
    for tokens in [512,384]:
        print(f"\nTEST: {tokens} tokens")
        start=time.perf_counter()
        with torch.inference_mode():
            generation=model.generate(
                input_ids=description_inputs.input_ids,
                attention_mask=description_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask,
                max_new_tokens=tokens
            )
        generation_time=time.perf_counter()-start
        audio=generation.float().cpu().numpy().squeeze()
        sr=model.config.sampling_rate
        duration=len(audio)/sr
        rtf=generation_time/duration
        path=OUTPUT_DIR/f"long_{tokens}.wav"
        sf.write(str(path),audio,sr)
        print(f"Generation: {generation_time:.2f}s")
        print(f"Audio:      {duration:.2f}s")
        print(f"RTF:        {rtf:.2f}x")
        print(f"Output:     {path}")
        results.append((tokens,generation_time,duration,rtf))

    print("\n"+"="*60)
    print("FINAL")
    print("="*60)
    for tokens,generation,duration,rtf in results:
        print(f"{tokens} tokens | {generation:.2f}s | {duration:.2f}s audio | {rtf:.2f}x")

    del model
    gc.collect()

if __name__=="__main__":
    main()