"""Offline safety tests for the opt-in Santali router; no models are downloaded."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.tribal_languages.santali_router import router


class SantaliRouterTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
        self.base_env = {
            "TRIBAL_SANTALI_STT_ENABLED": "false",
            "TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED": "false",
            "TRIBAL_SANTALI_TRANSLATION_ENABLED": "false",
            "TRIBAL_SANTALI_TRANSLATION_HF_ACCESS_ACCEPTED": "false",
            "TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS": "",
            "TRIBAL_SANTALI_TTS_ENABLED": "false",
            "TRIBAL_SANTALI_TTS_HF_ACCESS_ACCEPTED": "false",
        }
        self.patch = patch.dict(os.environ, self.base_env, clear=False)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_status_says_all_capabilities_disabled_by_default(self):
        response = self.client.get("/api/v1/tribal-languages/santali/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "experimental")
        for capability in ("stt", "translation", "tts"):
            self.assertFalse(payload["capabilities"][capability]["enabled"])
            self.assertFalse(payload["capabilities"][capability]["model_loaded"])

    def test_stt_is_unavailable_when_disabled(self):
        response = self.client.post(
            "/api/v1/tribal-languages/santali/stt",
            files={"audio": ("sample.wav", b"fake-audio", "audio/wav")},
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("disabled", response.json()["detail"])

    def test_translation_is_unavailable_when_disabled(self):
        response = self.client.post(
            "/api/v1/tribal-languages/santali/translate",
            json={"text": "Hello", "source_language": "english", "target_language": "santali"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("disabled", response.json()["detail"])

    def test_tts_is_unavailable_when_disabled(self):
        response = self.client.post(
            "/api/v1/tribal-languages/santali/tts", data={"text": "ᱥᱟᱱᱛᱟᱲᱤ"}
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("disabled", response.json()["detail"])

    def test_access_must_be_accepted_before_enabled_stt_runs(self):
        os.environ["TRIBAL_SANTALI_STT_ENABLED"] = "true"
        os.environ["TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED"] = "false"
        response = self.client.post(
            "/api/v1/tribal-languages/santali/stt",
            files={"audio": ("sample.wav", b"fake-audio", "audio/wav")},
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("access conditions", response.json()["detail"])

    def test_translation_direction_must_be_reviewed_and_explicitly_enabled(self):
        os.environ["TRIBAL_SANTALI_TRANSLATION_ENABLED"] = "true"
        os.environ["TRIBAL_SANTALI_TRANSLATION_HF_ACCESS_ACCEPTED"] = "true"
        os.environ["TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS"] = ""
        response = self.client.post(
            "/api/v1/tribal-languages/santali/translate",
            json={"text": "Hello", "source_language": "english", "target_language": "santali"},
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("not enabled", response.json()["detail"])

    def test_translation_route_rejects_unrelated_pair(self):
        os.environ["TRIBAL_SANTALI_TRANSLATION_ENABLED"] = "true"
        os.environ["TRIBAL_SANTALI_TRANSLATION_HF_ACCESS_ACCEPTED"] = "true"
        response = self.client.post(
            "/api/v1/tribal-languages/santali/translate",
            json={"text": "Hello", "source_language": "english", "target_language": "hindi"},
        )
        self.assertEqual(response.status_code, 400)

    def test_status_never_exposes_hf_token(self):
        with patch.dict(os.environ, {"HF_TOKEN": "test-secret-must-not-be-returned"}, clear=False):
            response = self.client.get("/api/v1/tribal-languages/santali/status")
        self.assertNotIn("test-secret-must-not-be-returned", response.text)


if __name__ == "__main__":
    unittest.main()
