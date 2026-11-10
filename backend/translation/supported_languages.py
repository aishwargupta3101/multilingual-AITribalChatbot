
"""
Central language metadata for the Tribal AI Chatbot.

Important:
- A translation code is a model-specific identifier, not a guarantee
  that the installed model supports that language.
- Keep existing keys stable for backward compatibility.
"""

SUPPORTED_LANGUAGES = {
    "english": {
        "name": "English",
        "code": "eng_Latn",
        "locale": "en",
    },
    "hindi": {
        "name": "Hindi",
        "code": "hin_Deva",
        "locale": "hi",
    },
    "manipuri": {
        "name": "Manipuri (Bengali Script)",
        "code": "mni_Beng",
        "locale": "mni",
    },
    "manipuri_mtei": {
        "name": "Manipuri (Meitei Mayek)",
        "code": None,
        "translation_code": "mni_Beng",
        "locale": "mni",
        "script": "Mtei",
    },
    "monpa": {"name": "Monpa", "code": None, "locale": "mon"},
    "tai_khamti": {"name": "Tai Khamti", "code": None, "locale": "tkt"},
    "naga": {"name": "Naga", "code": None, "locale": "nag"},
    "mishmi": {"name": "Mishmi", "code": None, "locale": "msh"},

    # Other scheduled Indian languages.
    "assamese": {
        "name": "Assamese",
        "code": "asm_Beng",
        "locale": "as",
    },
    "bengali": {
        "name": "Bengali",
        "code": "ben_Beng",
        "locale": "bn",
    },
    "bodo": {
        "name": "Bodo",
        "code": "brx_Deva",
        "locale": "brx",
    },
    "dogri": {
        "name": "Dogri",
        "code": "doi_Deva",
        "locale": "doi",
    },
    "gujarati": {
        "name": "Gujarati",
        "code": "guj_Gujr",
        "locale": "gu",
    },
    "kannada": {
        "name": "Kannada",
        "code": "kan_Knda",
        "locale": "kn",
    },
    "kashmiri": {
        "name": "Kashmiri",
        "code": "kas_Arab",
        "locale": "ks",
    },
    "konkani": {
        "name": "Konkani",
        "code": "kok_Deva",
        "locale": "gom",
    },
    "maithili": {
        "name": "Maithili",
        "code": "mai_Deva",
        "locale": "mai",
    },
    "malayalam": {
        "name": "Malayalam",
        "code": "mal_Mlym",
        "locale": "ml",
    },
    "marathi": {
        "name": "Marathi",
        "code": "mar_Deva",
        "locale": "mr",
    },
    "nepali": {
        "name": "Nepali",
        "code": "npi_Deva",
        "locale": "ne",
    },
    "odia": {
        "name": "Odia",
        "code": "ory_Orya",
        "locale": "or",
    },
    "punjabi": {
        "name": "Punjabi",
        "code": "pan_Guru",
        "locale": "pa",
    },
    "sanskrit": {
        "name": "Sanskrit",
        "code": "san_Deva",
        "locale": "sa",
    },
    "sindhi": {
        "name": "Sindhi",
        "code": "snd_Arab",
        "locale": "sd",
    },
    "tamil": {
        "name": "Tamil",
        "code": "tam_Taml",
        "locale": "ta",
    },
    "telugu": {
        "name": "Telugu",
        "code": "tel_Telu",
        "locale": "te",
    },
    "urdu": {
        "name": "Urdu",
        "code": "urd_Arab",
        "locale": "ur",
    },
    "santali": {
        "name": "Santali",
        "code": None,
        "locale": "sat",
        "script": "Ol Chiki",
    },
    "gondi": {
        "name": "Gondi",
        "code": None,
        "locale": "gon",
    },
}
