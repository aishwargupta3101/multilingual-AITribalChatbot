import ctranslate2
from transformers import AutoTokenizer

MODEL_DIR = "models/translation/nllb-200-distilled-600M-int8"
TOKENIZER_MODEL = "facebook/nllb-200-distilled-600M"

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    TOKENIZER_MODEL,
    cache_dir="models/translation/tokenizer"
)

print("Loading CTranslate2 INT8 model...")

translator = ctranslate2.Translator(
    MODEL_DIR,
    device="cpu",
    compute_type="int8",
    inter_threads=1,
    intra_threads=4,
)

text = "How are you today?"

source_language = "eng_Latn"
target_language = "mni_Beng"

tokenizer.src_lang = source_language

encoded = tokenizer(
    text,
    return_tensors=None,
    truncation=True,
    max_length=256,
)

source_tokens = tokenizer.convert_ids_to_tokens(
    encoded["input_ids"]
)

print("Translating...")

results = translator.translate_batch(
    [source_tokens],
    target_prefix=[[target_language]],
    beam_size=1,
    max_batch_size=1,
    max_decoding_length=128,
)

output_tokens = results[0].hypotheses[0]

if output_tokens and output_tokens[0] == target_language:
    output_tokens = output_tokens[1:]

translated = tokenizer.convert_tokens_to_string(
    output_tokens
).strip()

print()
print("====================================")
print("Source     :", text)
print("Translation:", translated)
print("====================================")