import json
import unittest
from pathlib import Path

from backend.tribal_languages.model_candidates import (
    candidate_is_eligible,
    get_candidate,
    list_model_candidates,
    resolve_indictrans2_route,
)


class CandidateCatalogTests(unittest.TestCase):
    def test_all_candidates_remain_disabled(self):
        candidates = list_model_candidates()
        self.assertGreaterEqual(len(candidates), 10)
        self.assertTrue(all(not row.get("enabled", False) for row in candidates))

    def test_santali_translation_routes(self):
        self.assertEqual(
            resolve_indictrans2_route("english", "santali"),
            ("ai4bharat/indictrans2-en-indic-dist-200M", "eng_Latn", "sat_Olck"),
        )
        self.assertEqual(
            resolve_indictrans2_route("santali", "english"),
            ("ai4bharat/indictrans2-indic-en-dist-200M", "sat_Olck", "eng_Latn"),
        )
        self.assertEqual(
            resolve_indictrans2_route("hindi", "santali"),
            ("ai4bharat/indictrans2-indic-indic-dist-320M", "hin_Deva", "sat_Olck"),
        )

    def test_translation_routing_blocks_unsupported_pairs(self):
        with self.assertRaises(ValueError):
            resolve_indictrans2_route("gondi", "english")
        with self.assertRaises(ValueError):
            resolve_indictrans2_route("english", "english")

    def test_gondi_mms_noncommercial_gate(self):
        candidate = get_candidate("gondi", "tts")
        allowed, reason = candidate_is_eligible(
            candidate, deployment_mode="commercial_product", hf_access_accepted=True
        )
        self.assertFalse(allowed)
        self.assertIn("CC-BY-NC", reason)

    def test_gondi_mms_local_demo_requires_acknowledgement(self):
        candidate = get_candidate("gondi", "tts")
        allowed, reason = candidate_is_eligible(
            candidate, deployment_mode="local_noncommercial_demo", hf_access_accepted=True
        )
        self.assertFalse(allowed)
        self.assertIn("non-commercial", reason)
        allowed, _ = candidate_is_eligible(
            candidate, deployment_mode="local_noncommercial_demo",
            hf_access_accepted=True, noncommercial_acknowledged=True,
        )
        self.assertTrue(allowed)

    def test_gondi_mms_requires_explicit_permission_for_commercial_use(self):
        candidate = get_candidate("gondi", "tts")
        allowed, _ = candidate_is_eligible(
            candidate, deployment_mode="commercial_product",
            hf_access_accepted=True, commercial_license_permission=True,
        )
        self.assertTrue(allowed)

    def test_gated_models_require_access_acceptance(self):
        candidate = get_candidate("santali", "stt")
        allowed, reason = candidate_is_eligible(
            candidate, deployment_mode="hosted_api", hf_access_accepted=False
        )
        self.assertFalse(allowed)
        self.assertIn("access conditions", reason)

    def test_indic_speak_requires_hosted_api_permission(self):
        candidate = get_candidate("santali", "tts_alternative")
        allowed, reason = candidate_is_eligible(
            candidate, deployment_mode="hosted_api", hf_access_accepted=True
        )
        self.assertFalse(allowed)
        self.assertIn("Written permission", reason)

    def test_no_monpa_model_is_claimed_ready(self):
        records = list_model_candidates("monpa")
        self.assertEqual(len(records), 3)
        self.assertTrue(all(record["status"].startswith("blocked_") for record in records))

    def test_manifest_parses_and_keeps_candidates_off_by_default(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "data/tribal_languages/model_candidates.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["default_enabled"])
        self.assertIn("gondi", manifest["languages"])
        self.assertIn("santali", manifest["languages"])
        self.assertIn("monpa", manifest["languages"])
        self.assertNotIn("tbo", manifest["languages"]["monpa"].get("known_codes_to_confirm_with_language_owner", {}).values())


if __name__ == "__main__":
    unittest.main()
