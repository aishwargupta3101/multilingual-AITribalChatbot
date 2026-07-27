import soundfile as sf
from transformers import AutoProcessor, SeamlessM4Tv2Model

processor = AutoProcessor.from_pretrained(
    "facebook/seamless-m4t-v2-large"
)

model = SeamlessM4Tv2Model.from_pretrained(
    "facebook/seamless-m4t-v2-large"
)

inputs = processor(
    text="Hello, how are you?",
    src_lang="eng",
    return_tensors="pt"
)

output = model.generate(
    **inputs,
    tgt_lang="mni",
    generate_speech=True
)

print(type(output))

audio = output[0]

audio = audio.cpu().numpy().squeeze()

sf.write("manipuri.wav", audio, 16000)

print("Done")