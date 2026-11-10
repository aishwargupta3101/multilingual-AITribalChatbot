import unittest

from backend.tribal_languages.tts_service import (
    TribalTTSConfigurationError,
    TribalTTSGenerationError,
    TribalTTSService,
    TribalTTSUnavailableError,
)


class TribalTTSServiceTests(unittest.TestCase):
    def test_languages_disabled_by_default(self):
        service = TribalTTSService()
        with self.assertRaises(TribalTTSUnavailableError):
            service.synthesize("Hello", "gondi")

    def test_empty_text_rejected(self):
        service = TribalTTSService(
            backend=lambda **kwargs: b"audio",
            enabled_languages={"gondi"},
        )
        with self.assertRaises(TribalTTSConfigurationError):
            service.synthesize("  ", "gondi")

    def test_unknown_language_rejected(self):
        service = TribalTTSService(
            backend=lambda **kwargs: b"audio",
            enabled_languages={"english"},
        )
        with self.assertRaises(TribalTTSConfigurationError):
            service.synthesize("Hello", "english")

    def test_verified_backend_returns_audio(self):
        calls = []

        def fake_backend(*, text, language):
            calls.append((text, language))
            return b"fake-audio"

        service = TribalTTSService(
            backend=fake_backend,
            enabled_languages={"gondi"},
        )
        result = service.synthesize("  sample text  ", "GONDI")

        self.assertEqual(result.language, "gondi")
        self.assertEqual(result.audio, b"fake-audio")
        self.assertEqual(result.content_type, "audio/wav")
        self.assertEqual(calls, [("sample text", "gondi")])

    def test_empty_backend_output_rejected(self):
        service = TribalTTSService(
            backend=lambda **kwargs: b"",
            enabled_languages={"gondi"},
        )
        with self.assertRaises(TribalTTSGenerationError):
            service.synthesize("sample", "gondi")

    def test_backend_exception_wrapped(self):
        def broken_backend(**kwargs):
            raise RuntimeError("internal error")

        service = TribalTTSService(
            backend=broken_backend,
            enabled_languages={"santali"},
        )
        with self.assertRaises(TribalTTSGenerationError):
            service.synthesize("sample", "santali")


if __name__ == "__main__":
    unittest.main()
