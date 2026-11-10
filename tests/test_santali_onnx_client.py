"""Offline tests for the optional Santali ONNX frontend client."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
if str(FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(FRONTEND_ROOT))

# The standalone package contains only the new client, so stub the existing
# project's endpoint constant for this offline-only test suite.
import types
endpoint_stub = types.ModuleType("api.endpoints")
endpoint_stub.BASE_URL = "http://testserver"
sys.modules.setdefault("api.endpoints", endpoint_stub)

from api.santali_onnx_client import SantaliOnnxClient, SANTALI_ONNX_STT_ENDPOINT


class SantaliOnnxClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.audio_path = Path(self.temp.name) / "sample.wav"
        self.audio_path.write_bytes(b"fake-wav-data")

    def tearDown(self):
        self.temp.cleanup()

    @patch("api.santali_onnx_client.requests.post")
    def test_successful_response_uses_audio_field_and_experimental_route(self, post):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "success": True,
            "language": "santali",
            "text": "ᱟᱡ",
            "status": "experimental_output_requires_broader_evaluation",
        }
        post.return_value = response

        result = SantaliOnnxClient.transcribe_file(self.audio_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["text"], "ᱟᱡ")
        args, kwargs = post.call_args
        self.assertTrue(args[0].endswith(SANTALI_ONNX_STT_ENDPOINT))
        self.assertIn("audio", kwargs["files"])

    @patch("api.santali_onnx_client.requests.post")
    def test_disabled_backend_returns_actionable_http_error(self, post):
        response = Mock()
        response.ok = False
        response.status_code = 503
        response.json.return_value = {"detail": "Santali ONNX STT is disabled."}
        response.text = ""
        post.return_value = response

        result = SantaliOnnxClient.transcribe_file(self.audio_path)

        self.assertFalse(result["success"])
        self.assertIn("HTTP 503", result["error"])
        self.assertIn("disabled", result["error"])

    def test_missing_file_fails_without_http_request(self):
        result = SantaliOnnxClient.transcribe_file(self.audio_path.parent / "missing.wav")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    @patch("api.santali_onnx_client.requests.post")
    def test_uploaded_bytes_use_filename_and_audio_field(self, post):
        response = Mock()
        response.ok = True
        response.json.return_value = {"success": True, "language": "santali", "text": "ᱟᱡ"}
        post.return_value = response

        result = SantaliOnnxClient.transcribe_bytes(b"fake-mp3-data", "common_voice_sat_test.mp3")

        self.assertTrue(result["success"])
        self.assertEqual(result["text"], "ᱟᱡ")
        args, kwargs = post.call_args
        self.assertTrue(args[0].endswith(SANTALI_ONNX_STT_ENDPOINT))
        uploaded = kwargs["files"]["audio"]
        self.assertEqual(uploaded[0], "common_voice_sat_test.mp3")
        self.assertEqual(uploaded[1], b"fake-mp3-data")

    def test_empty_uploaded_bytes_fail_without_http_request(self):
        with patch("api.santali_onnx_client.requests.post") as post:
            result = SantaliOnnxClient.transcribe_bytes(b"", "empty.mp3")
        self.assertFalse(result["success"])
        self.assertIn("empty", result["error"].lower())
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
