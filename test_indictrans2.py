
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

MODEL_NAME = "ai4bharat/indictrans2-indic-indic-1B"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Device: {DEVICE}")
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)
print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float32
).to(DEVICE)
model.eval()
ip = IndicProcessor(inference=True)

sentences = [
    "नमस्ते, आप कैसे हैं?",
    "मेरा नाम राहुल है।",
    "आज मौसम बहुत अच्छा है।",
    "आपका दिन शुभ हो।",
    "मुझे आपकी मदद चाहिए।"
]

for target_lang in ["mni_Beng", "mni_Mtei"]:
    print(f"\n{'=' * 50}")
    print(f"Testing target language: {target_lang}")
    print("=" * 50)

    batch = ip.preprocess_batch(
        sentences,
        src_lang="hin_Deva",
        tgt_lang=target_lang
    )

    inputs = tokenizer(
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
        return_attention_mask=True
    ).to(DEVICE)

    with torch.inference_mode():
        generated_tokens = model.generate(
            **inputs,
            max_length=128,
            num_beams=5,
            num_return_sequences=1
        )

    decoded = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )

    translations = ip.postprocess_batch(
        decoded,
        lang=target_lang
    )

    for source, translated in zip(sentences, translations):
        print(f"\nHindi: {source}")
        print(f"Translation: {translated}")