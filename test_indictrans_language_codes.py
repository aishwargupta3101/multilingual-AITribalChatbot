
from backend.translation.indictrans_service import indictrans_service

print("=" * 65)
print("INDICTRANS2 LANGUAGE CODE DIAGNOSTIC")
print("=" * 65)

model_name = indictrans_service._get_model_name("english", "manipuri")

print("\nModel:", model_name)

indictrans_service._load_model(model_name)

tokenizer = indictrans_service._tokenizer

for language in ["mni_Beng", "mni_Mtei", "hin_Deva"]:
    print("\nLanguage:", language)

    try:
        token_id = tokenizer.convert_tokens_to_ids(language)
        token = tokenizer.convert_ids_to_tokens(token_id)

        print("Token ID:", token_id)
        print("Resolved token:", token)

        if token_id == tokenizer.unk_token_id:
            print("Status: UNKNOWN TOKEN")
        else:
            print("Status: Token recognized")

    except Exception as e:
        print("Error:", e)

print("\n" + "=" * 65)
print("DIAGNOSTIC COMPLETED")
print("=" * 65)
