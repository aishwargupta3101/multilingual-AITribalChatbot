import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Load the standalone adapter directly so tests stay independent from the
# backend.services package initializer (which imports unrelated chat/MCP services).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "frontend"))
_SERVICE_PATH = PROJECT_ROOT / "gondi_payload" / "backend" / "services" / "gondi_translation_service.py"
if not _SERVICE_PATH.exists():
    _SERVICE_PATH = PROJECT_ROOT / "backend" / "services" / "gondi_translation_service.py"
_spec = importlib.util.spec_from_file_location("gondi_translation_service_test_module", _SERVICE_PATH)
_service_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_service_module)
GondiTranslationService = _service_module.GondiTranslationService

from frontend.api.gondi_chat_bridge import _strip_markdown_for_translation


class GondiIntegrationUnitTests(unittest.TestCase):
    def test_markdown_cleanup_removes_headings_and_bullets(self):
        value = _strip_markdown_for_translation(
            "## Definition\n\n- **Gondi** is a language.\n- It is used by Gondi communities."
        )
        self.assertNotIn("##", value)
        self.assertNotIn("**", value)
        self.assertNotIn("- ", value)
        self.assertIn("Gondi is a language.", value)
        self.assertIn("It is used by Gondi communities.", value)

    def test_service_id_matches_requested_pair(self):
        payload = {
            "pipelineResponseConfig": [
                {"taskType": "translation", "config": {
                    "language": {"sourceLanguage": "hi", "targetLanguage": "en"},
                    "serviceId": "wrong-pair",
                }},
                {"taskType": "translation", "config": {
                    "language": {"sourceLanguage": "en", "targetLanguage": "gon"},
                    "serviceId": "right-pair",
                }},
            ]
        }
        self.assertEqual(
            GondiTranslationService._find_service_id(payload, "en", "gon"),
            "right-pair",
        )

    def test_unconfigured_service_fails_clearly(self):
        with patch.dict(os.environ, {
            "BHASHINI_USER_ID": "",
            "BHASHINI_ULCA_API_KEY": "",
            "BHASHINI_PIPELINE_ID": "",
        }, clear=False):
            with self.assertRaisesRegex(RuntimeError, "Gondi text translation is not configured"):
                GondiTranslationService().translate("hello", "english", "gondi")

    def test_same_language_returns_text_without_credentials(self):
        self.assertEqual(
            GondiTranslationService().translate("  example  ", "gondi", "gondi"),
            "example",
        )

    def test_translation_config_and_compute_calls(self):
        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        responses = [
            FakeResponse({
                "pipelineInferenceAPIEndPoint": {
                    "callbackURL": "https://bhashini.example/compute",
                    "inferenceApiKey": {"name": "Authorization", "value": "test-token"},
                },
                "pipelineResponseConfig": [{
                    "taskType": "translation",
                    "config": {
                        "language": {"sourceLanguage": "en", "targetLanguage": "gon"},
                        "serviceId": "test-gondi-service",
                    },
                }],
            }),
            FakeResponse({"pipelineResponse": [{"output": [{"target": "Gondi text"}]}]}),
        ]
        with patch.dict(os.environ, {
            "BHASHINI_USER_ID": "test-user",
            "BHASHINI_ULCA_API_KEY": "test-ulca-key",
            "BHASHINI_PIPELINE_ID": "test-pipeline",
        }, clear=False), patch.object(
            _service_module.requests, "post", side_effect=responses
        ) as post:
            GondiTranslationService._pipeline_settings.cache_clear()
            result = GondiTranslationService().translate(
                "Hello world", "english", "gondi"
            )
        self.assertEqual(result, "Gondi text")
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args_list[1].kwargs["json"]["pipelineTasks"][0]["config"]["serviceId"], "test-gondi-service")



if __name__ == "__main__":
    unittest.main()
