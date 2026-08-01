from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "facebook/nllb-200-distilled-600M"
)

print("mni_Beng ID :", tokenizer.convert_tokens_to_ids("mni_Beng"))
print("eng_Latn ID :", tokenizer.convert_tokens_to_ids("eng_Latn"))
print("hin_Deva ID :", tokenizer.convert_tokens_to_ids("hin_Deva"))