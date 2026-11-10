
import json
import tempfile
import unittest
from pathlib import Path

from backend.tribal_languages.dataset_validator import validate_manifest, validate_model_config


class DatasetValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "audio").mkdir()
        (self.root / "audio" / "sample.wav").write_bytes(b"fake-audio-bytes")
        self.manifest = self.root / "manifest.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self, entries):
        self.manifest.write_text(json.dumps({"schema_version": 1, "datasets": entries}), encoding="utf-8")

    def valid_entry(self):
        return {
            "dataset_id": "sample-001",
            "language_code": "sat",
            "audio_path": "audio/sample.wav",
            "transcript": "verified sample transcript",
            "source": "documented source",
            "license": "CC-BY-4.0",
            "consent_status": "permission documented",
        }

    def test_valid_entry_passes(self):
        self.write_manifest([self.valid_entry()])
        report = validate_manifest(self.manifest)
        self.assertTrue(report.ok)
        self.assertEqual(report.valid_entries, 1)

    def test_missing_audio_fails(self):
        entry = self.valid_entry()
        entry["audio_path"] = "audio/missing.wav"
        self.write_manifest([entry])
        report = validate_manifest(self.manifest)
        self.assertFalse(report.ok)
        self.assertIn("audio_file_missing", [i.code for i in report.issues])

    def test_path_traversal_fails(self):
        entry = self.valid_entry()
        entry["audio_path"] = "../outside.wav"
        self.write_manifest([entry])
        report = validate_manifest(self.manifest)
        self.assertFalse(report.ok)
        self.assertIn("unsafe_audio_path", [i.code for i in report.issues])

    def test_empty_transcript_fails(self):
        entry = self.valid_entry()
        entry["transcript"] = "   "
        self.write_manifest([entry])
        report = validate_manifest(self.manifest)
        self.assertFalse(report.ok)
        self.assertIn("missing_transcript", [i.code for i in report.issues])

    def test_unknown_license_fails(self):
        entry = self.valid_entry()
        entry["license"] = "TBD"
        self.write_manifest([entry])
        report = validate_manifest(self.manifest)
        self.assertFalse(report.ok)
        self.assertIn("license_unverified", [i.code for i in report.issues])

    def test_duplicate_ids_fail(self):
        entry = self.valid_entry()
        self.write_manifest([entry, dict(entry)])
        report = validate_manifest(self.manifest)
        self.assertFalse(report.ok)
        self.assertIn("duplicate_dataset_id", [i.code for i in report.issues])

    def test_missing_consent_metadata_warns(self):
        entry = self.valid_entry()
        del entry["consent_status"]
        self.write_manifest([entry])
        report = validate_manifest(self.manifest)
        self.assertTrue(report.ok)
        self.assertIn("consent_status_missing", [i.code for i in report.issues])

    def test_invalid_json_reported(self):
        self.manifest.write_text("{broken", encoding="utf-8")
        report = validate_manifest(self.manifest)
        self.assertFalse(report.ok)
        self.assertIn("invalid_json", [i.code for i in report.issues])


class ModelConfigTests(unittest.TestCase):
    def test_model_requires_explicit_verification(self):
        issues = validate_model_config({"model_id": "org/model", "language_code": "sat"})
        codes = [i.code for i in issues]
        self.assertIn("model_not_verified", codes)
        self.assertIn("license_review_needed", codes)

    def test_bad_repository_path_rejected(self):
        issues = validate_model_config({"model_id": "../local", "language_code": "sat"})
        self.assertIn("invalid_model_id", [i.code for i in issues])

    def test_verified_config_passes_without_warnings(self):
        issues = validate_model_config({
            "model_id": "org/model-name",
            "language_code": "sat",
            "verified": True,
            "commercial_use_reviewed": True,
        })
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
