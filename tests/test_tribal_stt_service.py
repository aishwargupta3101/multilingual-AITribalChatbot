import unittest

from backend.tribal_languages.stt_service import (
    STTConfigurationError,
    TribalMMSSTTService,
)


class TribalMMSSTTServiceTests(unittest.TestCase):
    def test_missing_adapter_fails_before_model_loading(self):
        service = TribalMMSSTTService()
        with self.assertRaises(STTConfigurationError):
            service.transcribe("monpa", b"not audio")

    def test_empty_audio_rejected_when_adapter_is_configured(self):
        service = TribalMMSSTTService(adapter_codes={"santali": "verified-test-code"})
        with self.assertRaises(ValueError):
            service.transcribe("santali", b"")

    def test_language_key_normalization(self):
        self.assertEqual(TribalMMSSTTService._language_key(" Santali "), "santali")
        self.assertEqual(TribalMMSSTTService._language_key("Tawang Monpa"), "tawang_monpa")


if __name__ == "__main__":
    unittest.main()
