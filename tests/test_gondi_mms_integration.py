from __future__ import annotations

import csv
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "backend" / "tribal_languages"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


speech = load_module("gondi_mms_service_test", MODULES / "gondi_mms_service.py")
translation = load_module("gondi_local_mt_test", MODULES / "gondi_local_translation_service.py")
train = load_module("train_gondi_mt5_test", ROOT / "scripts" / "train_gondi_mt5.py")


class GondiScriptConversionTests(unittest.TestCase):
    def test_devanagari_to_telugu_uses_mms_tts_script(self):
        converted = speech.devanagari_to_telugu("किताब")
        self.assertEqual(converted, "కితాబ")

    def test_telugu_asr_result_converts_to_devanagari_approximation(self):
        converted = speech.telugu_to_devanagari("కితాబ")
        self.assertEqual(converted, "किताब")

    def test_common_ai_acronym_does_not_leave_latin_chars(self):
        converted = speech.devanagari_to_telugu("AI")
        self.assertEqual(converted, "అయి")


class GondiLocalTranslationTests(unittest.TestCase):
    def test_missing_checkpoint_is_reported_without_loading_model(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"GONDI_MT5_MODEL_DIR": str(Path(tmp) / "missing")}):
            service = translation.GondiLocalTranslationService()
            self.assertFalse(service.status()["translation_ready"])
            with self.assertRaisesRegex(RuntimeError, "has not been trained yet"):
                service.translate("नमस्ते", "hindi_to_gondi")

    def test_invalid_translation_direction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Hindi-to-Gondi"):
            translation.GondiLocalTranslationService().translate("hello", "english_to_gondi")


class GondiTrainingDataTests(unittest.TestCase):
    def test_reads_hindi_gondi_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["Hindi", "Gondi"])
                writer.writeheader()
                writer.writerow({"Hindi": "यह घर है।", "Gondi": "इद घर।"})
            self.assertEqual(train.read_parallel_csv(path), [("यह घर है।", "इद घर।")])

    def test_creates_both_translation_directions(self):
        examples = train.make_examples([("यह घर है।", "इद घर।")])
        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0][0], "translate Hindi to Gondi: यह घर है।")
        self.assertEqual(examples[0][1], "इद घर।")
        self.assertEqual(examples[1][0], "translate Gondi to Hindi: इद घर।")
        self.assertEqual(examples[1][1], "यह घर है।")


if __name__ == "__main__":
    unittest.main()
