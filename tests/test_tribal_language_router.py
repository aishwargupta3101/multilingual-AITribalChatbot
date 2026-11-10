import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.tribal_languages.router import router


class TribalLanguageRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(router)
        cls.client = TestClient(app)

    def test_health_reports_metadata_only(self):
        response = self.client.get("/api/v1/tribal-languages/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["mode"], "metadata-only")
        self.assertFalse(body["inference_enabled"])

    def test_lists_three_experimental_languages(self):
        response = self.client.get("/api/v1/tribal-languages/languages")
        self.assertEqual(response.status_code, 200)
        codes = {item["code"] for item in response.json()["languages"]}
        self.assertEqual(codes, {"gondi", "santali", "monpa"})

    def test_all_capabilities_disabled_by_default(self):
        body = self.client.get("/api/v1/tribal-languages/languages").json()
        for language in body["languages"]:
            for capability in ("stt", "translation", "tts"):
                self.assertFalse(language[capability]["enabled"])

    def test_language_lookup_is_case_insensitive(self):
        response = self.client.get("/api/v1/tribal-languages/languages/GONDI")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], "gondi")

    def test_unknown_language_returns_404(self):
        response = self.client.get("/api/v1/tribal-languages/languages/unknown")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
