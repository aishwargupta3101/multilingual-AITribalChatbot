import soundfile as sf
import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model

MODEL_NAME = "facebook/seamless-m4t-v2-large"

processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = SeamlessM4Tv2Model.from_pretrained(MODEL_NAME)
model.eval()

inputs = processor(
    text="Hello, how are you?",
    src_lang="eng",
    return_tensors="pt",
)

with torch.inference_mode():
    output = model.generate(
        **inputs,
        tgt_lang="hin",
        generate_speech=True,
    )

audio = output[0].cpu().numpy().squeeze()
sf.write("hindi_test.wav", audio, 16000)

print("Saved hindi_test.wav")