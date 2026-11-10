"""Fast, offline checks for the central translation language registry."""
from backend.services.translation_service import TranslationService


def test_every_registered_language_validates():
    for language in TranslationService.SUPPORTED_LANGUAGES:
        normalized = TranslationService.normalize_language(language)
        TranslationService.validate_language(normalized)


def test_common_aliases_normalize_to_supported_languages():
    aliases = {
        "Assamese": "assamese",
        "asm": "assamese",
        "Bengali": "bengali",
        "Gujarati": "gujarati",
        "Hindi": "hindi",
        "Manipuri Bengali": "manipuri",
        "Meitei Mayek": "manipuri_mtei",
        "Santali": "santali",
        "Tamil": "tamil",
        "Telugu": "telugu",
        "Urdu": "urdu",
    }
    for alias, expected in aliases.items():
        actual = TranslationService.normalize_language(alias)
        assert actual == expected, f"{alias!r} normalized to {actual!r}"
        TranslationService.validate_language(actual)


def test_english_identity_translation_does_not_require_model():
    service = TranslationService()
    assert service.translate("Artificial intelligence is useful.", "english", "english") == "Artificial intelligence is useful."
