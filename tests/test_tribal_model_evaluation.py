
import json
import tempfile
import unittest
from pathlib import Path

from backend.tribal_languages.model_evaluation import validate_evaluation_records, summarize_results


class ModelEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "evaluations.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, records):
        self.path.write_text(json.dumps({"evaluations": records}), encoding="utf-8")

    def valid_asr(self):
        return {
            "case_id": "asr-001", "language_code": "sat", "capability": "asr",
            "status": "pass", "notes": "reviewed", "reference_transcript": "hello",
            "predicted_transcript": "hello", "evidence": "output.txt"
        }

    def test_valid_asr_record_passes(self):
        self.write([self.valid_asr()])
        report = validate_evaluation_records(self.path)
        self.assertTrue(report.ok)
        self.assertEqual(report.eligible_records, 1)

    def test_missing_required_field_fails(self):
        record = self.valid_asr()
        del record["notes"]
        self.write([record])
        report = validate_evaluation_records(self.path)
        self.assertFalse(report.ok)
        self.assertIn("missing_notes", [i.code for i in report.issues])

    def test_invalid_capability_fails(self):
        record = self.valid_asr()
        record["capability"] = "magic"
        self.write([record])
        report = validate_evaluation_records(self.path)
        self.assertFalse(report.ok)
        self.assertIn("invalid_capability", [i.code for i in report.issues])

    def test_pass_without_evidence_warns(self):
        record = self.valid_asr()
        record["evidence"] = ""
        self.write([record])
        report = validate_evaluation_records(self.path)
        self.assertTrue(report.ok)
        self.assertIn("pass_without_evidence", [i.code for i in report.issues])

    def test_duplicate_case_ids_fail(self):
        record = self.valid_asr()
        self.write([record, dict(record)])
        report = validate_evaluation_records(self.path)
        self.assertFalse(report.ok)
        self.assertIn("duplicate_case_id", [i.code for i in report.issues])

    def test_translation_requires_human_review_metadata_warning(self):
        record = {
            "case_id": "tr-001", "language_code": "sat", "capability": "translation",
            "status": "needs_review", "notes": "review", "source_text": "hello",
            "translated_text": "output"
        }
        self.write([record])
        report = validate_evaluation_records(self.path)
        self.assertTrue(report.ok)
        self.assertIn("translation_review_missing", [i.code for i in report.issues])

    def test_summary_never_claims_production_ready(self):
        result = summarize_results([self.valid_asr()])
        self.assertFalse(result["asr"]["production_ready"])
        self.assertEqual(result["asr"]["pass"], 1)

    def test_invalid_json_fails(self):
        self.path.write_text("{broken", encoding="utf-8")
        report = validate_evaluation_records(self.path)
        self.assertFalse(report.ok)
        self.assertIn("invalid_json", [i.code for i in report.issues])


if __name__ == "__main__":
    unittest.main()
