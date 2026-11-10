"""Offline tests for the normal Santali ONNX router; inference is never loaded."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.tribal_languages.santali_onnx_router import router


class SantaliOnnxRouterTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    def test_status_is_enabled_by_default_without_environment_override(self):
        with patch.dict(os.environ):
            os.environ.pop("TRIBAL_SANTALI_ONNX_STT_ENABLED", None)
            response = self.client.get("/api/v1/tribal-languages/santali-onnx/status")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["enabled"])
        self.assertFalse(response.json()["model_loaded"])

    def test_explicit_admin_disable_does_not_load_model(self):
        with patch.dict(os.environ, {"TRIBAL_SANTALI_ONNX_STT_ENABLED": "false"}):
            response = self.client.post(
                "/api/v1/tribal-languages/santali-onnx/stt",
                files={"audio": ("empty.wav", b"fake", "audio/wav")},
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn("disabled", response.json()["detail"])

    def test_enabled_route_rejects_empty_audio_before_model_load(self):
        with patch.dict(os.environ, {"TRIBAL_SANTALI_ONNX_STT_ENABLED": "true"}):
            response = self.client.post(
                "/api/v1/tribal-languages/santali-onnx/stt",
                files={"audio": ("empty.wav", b"", "audio/wav")},
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_status_does_not_expose_hf_token(self):
        with patch.dict(
            os.environ,
            {
                "HF_TOKEN": "sensitive-test-token",
                "TRIBAL_SANTALI_ONNX_STT_ENABLED": "false",
            },
        ):
            response = self.client.get("/api/v1/tribal-languages/santali-onnx/status")
        self.assertNotIn("sensitive-test-token", response.text)


if __name__ == "__main__":
    unittest.main()
