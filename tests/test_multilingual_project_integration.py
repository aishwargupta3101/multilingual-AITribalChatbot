from backend.services.translation_service import TranslationService
from backend.translation.indictrans_service import IndicTransService


def test_all_matrix_languages_are_registered_in_both_services():
    expected = {
        "assamese", "bengali", "bodo", "dogri", "gujarati", "hindi",
        "kannada", "kashmiri", "kashmiri_deva", "konkani", "maithili",
        "malayalam", "manipuri", "manipuri_mtei", "marathi", "nepali",
        "odia", "punjabi", "sanskrit", "santali", "sindhi",
        "sindhi_deva", "tamil", "telugu", "urdu",
    }
    assert expected <= TranslationService.SUPPORTED_LANGUAGES
    assert expected <= set(IndicTransService.LANGUAGE_CODES)


def test_meitei_mayek_registration_is_preserved():
    assert "manipuri_mtei" in TranslationService.SUPPORTED_LANGUAGES
    assert IndicTransService.LANGUAGE_CODES["manipuri_mtei"] == "mni_Mtei"


def test_aliases_normalize():
    assert TranslationService.normalize_language("asm") == "assamese"
    assert TranslationService.normalize_language("kas-Deva") == "kashmiri_deva"
    assert TranslationService.normalize_language("sat_Olck") == "santali"
