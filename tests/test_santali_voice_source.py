"""Offline tests for the shared English/Santali voice source-language branch."""
from __future__ import annotations
import os
import sys
import types
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

# These unit tests exercise only the audio-to-text helper, not the Streamlit UI.
# Install tiny import stubs when the test runner intentionally omits UI dependencies.
try:
    import streamlit  # noqa: F401
except ImportError:
    sys.modules["streamlit"] = types.ModuleType("streamlit")
try:
    import streamlit_mic_recorder  # noqa: F401
except ImportError:
    mic_module = types.ModuleType("streamlit_mic_recorder")
    mic_module.mic_recorder = lambda *args, **kwargs: None
    sys.modules["streamlit_mic_recorder"] = mic_module

# The extracted integration payload does not include the host project's endpoint config.
# Only constants are needed to import the helper; the HTTP client is mocked in tests.
try:
    import api.endpoints  # noqa: F401
except ImportError:
    endpoints_module = types.ModuleType("api.endpoints")
    endpoints_module.BASE_URL = "http://127.0.0.1:8000"
    endpoints_module.SPEECH_UPLOAD_ENDPOINT = "/api/v1/speech/upload"
    sys.modules["api.endpoints"] = endpoints_module

try:
    import api.client  # noqa: F401
except ImportError:
    client_module = types.ModuleType("api.client")
    class _UnusedAPIClient:
        @staticmethod
        def upload_audio(*args, **kwargs):
            raise AssertionError("APIClient.upload_audio should be mocked in these tests.")
    client_module.APIClient = _UnusedAPIClient
    sys.modules["api.client"] = client_module

from views.santali_voice import _extract_transcript, _transcribe_english


class SantaliVoiceSourceTests(unittest.TestCase):
    def test_extracts_plain_english_transcript(self):
        self.assertEqual(
            _extract_transcript({"success": True, "transcription": "What is the weather?"}),
            "What is the weather?",
        )

    def test_extracts_nested_transcript(self):
        self.assertEqual(
            _extract_transcript({"success": True, "data": {"text": "Hello Tribal AI"}}),
            "Hello Tribal AI",
        )

    def test_rejects_empty_transcript(self):
        with self.assertRaisesRegex(RuntimeError, "no transcript"):
            _extract_transcript({"success": True, "data": {}})

    def test_english_audio_uses_existing_english_speech_endpoint(self):
        seen = {}
        def fake_upload(endpoint, path, language):
            seen["endpoint"] = endpoint
            seen["path"] = path
            seen["language"] = language
            self.assertTrue(os.path.isfile(path))
            with open(path, "rb") as audio_file:
                self.assertEqual(audio_file.read(), b"mock wav bytes")
            return {"success": True, "text": "Tell me a story."}

        with patch("views.santali_voice.APIClient.upload_audio", side_effect=fake_upload) as mock_upload:
            result = _transcribe_english(b"mock wav bytes", "recording.wav")
        self.assertTrue(result["success"])
        self.assertEqual(result["text"], "Tell me a story.")
        self.assertEqual(seen["language"], "english")
        mock_upload.assert_called_once()
        # The temporary file is cleaned up immediately after upload returns.
        self.assertFalse(os.path.exists(seen["path"]))

    @patch("views.santali_voice.APIClient.upload_audio", return_value={"success": False, "error": "ASR offline"})
    def test_english_asr_error_is_reported(self, mock_upload):
        with self.assertRaisesRegex(RuntimeError, "ASR offline"):
            _transcribe_english(b"mock bytes", "recording.wav")


if __name__ == "__main__":
    unittest.main()
