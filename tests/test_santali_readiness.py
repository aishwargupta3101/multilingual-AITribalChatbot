import unittest
from unittest.mock import Mock

from backend.tribal_languages.santali_readiness import (
    configuration_report,
    probe_repo_readme_access,
    probe_required_repositories,
)


class SantaliReadinessTests(unittest.TestCase):
    def test_inference_flags_default_off(self):
        report = configuration_report({})
        for capability in ("stt", "translation", "tts"):
            self.assertFalse(report["capabilities"][capability]["enabled"])
            self.assertFalse(report["capabilities"][capability]["access_acknowledged_in_env"])
            self.assertFalse(report["capabilities"][capability]["safe_to_attempt_only_after_repo_access_probe"])
        self.assertEqual(report["translation_verified_pairs"], [])
        self.assertFalse(report["hf_token_configured"])

    def test_flags_are_detected_without_enabling_anything(self):
        report = configuration_report({
            "TRIBAL_SANTALI_STT_ENABLED": "true",
            "TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED": "true",
            "TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS": "english->santali, santali->english",
            "HF_TOKEN": "dummy-secret-token",
        })
        self.assertTrue(report["capabilities"]["stt"]["enabled"])
        self.assertTrue(report["hf_token_configured"])
        self.assertEqual(report["translation_verified_pairs"], ["english->santali", "santali->english"])
        self.assertNotIn("dummy-secret-token", repr(report))

    def test_no_token_skips_access_probe(self):
        result = probe_repo_readme_access("owner/model", "")
        self.assertEqual(result["status"], "skipped_no_HF_TOKEN")
        self.assertFalse(result["readme_accessible"])

    def test_success_probe_only_requests_readme_with_temp_cache(self):
        fn = Mock(return_value="/tmp/README.md")
        result = probe_repo_readme_access("owner/model", "fake", fn)
        self.assertTrue(result["readme_accessible"])
        self.assertEqual(result["status"], "readme_accessible")
        kwargs = fn.call_args.kwargs
        self.assertEqual(kwargs["filename"], "README.md")
        self.assertIn("cache_dir", kwargs)
        self.assertNotIn("fake", repr(result))

    def test_auth_error_is_sanitized(self):
        class Response:
            status_code = 403
        class GatedRepoError(Exception):
            response = Response()
        def fn(**kwargs):
            raise GatedRepoError("secret fake token should not be exposed")
        result = probe_repo_readme_access("owner/model", "secret fake token", fn)
        self.assertFalse(result["readme_accessible"])
        self.assertEqual(result["http_status"], 403)
        self.assertNotIn("secret fake token", repr(result))

    def test_repository_list_is_deduplicated(self):
        fn = Mock(return_value="/tmp/README.md")
        result = probe_required_repositories("fake", fn)
        repo_ids = [row["repo_id"] for row in result]
        self.assertEqual(len(repo_ids), len(set(repo_ids)))
        self.assertEqual(fn.call_count, len(repo_ids))


if __name__ == "__main__":
    unittest.main()
