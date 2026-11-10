import unittest

from backend.tribal_languages.translation_service import (
    TribalTranslationService, TranslationNotReadyError, TranslationExecutionError,
)


class TribalTranslationServiceTests(unittest.TestCase):
    def test_pairs_disabled_by_default(self):
        service = TribalTranslationService()
        with self.assertRaises(TranslationNotReadyError):
            service.translate("hello", "santali", "english")

    def test_verified_pair_uses_backend(self):
        service = TribalTranslationService(
            translator=lambda text, src, dst: "translated: " + text,
            verified_pairs=[("santali", "english")],
            backend_name="test",
        )
        result = service.translate("namaste", "sat", "en")
        self.assertEqual(result.text, "translated: namaste")
        self.assertEqual(result.source_language, "santali")
        self.assertEqual(result.target_language, "english")

    def test_monpa_blocked_until_variety_selected(self):
        service = TribalTranslationService(
            translator=lambda text, src, dst: text,
            verified_pairs=[("monpa", "english")],
        )
        with self.assertRaises(TranslationNotReadyError):
            service.translate("sample", "monpa", "english")

    def test_empty_backend_output_rejected(self):
        service = TribalTranslationService(
            translator=lambda text, src, dst: "  ",
            verified_pairs=[("gondi", "english")],
        )
        with self.assertRaises(TranslationExecutionError):
            service.translate("sample", "gondi", "english")

    def test_same_language_returns_original(self):
        service = TribalTranslationService()
        result = service.translate(" hello ", "english", "en")
        self.assertEqual(result.text, "hello")


if __name__ == "__main__":
    unittest.main()
