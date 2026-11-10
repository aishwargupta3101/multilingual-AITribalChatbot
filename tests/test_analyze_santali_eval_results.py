import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze_santali_eval_results.py"
spec = importlib.util.spec_from_file_location("santali_diag", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class SantaliDiagnosticTests(unittest.TestCase):
    def test_exact_match(self):
        self.assertEqual(module.classify("ᱟᱡ ᱵᱟᱵᱟ", "ᱟᱡ   ᱵᱟᱵᱟ"), "exact_match")

    def test_spacing_only(self):
        self.assertEqual(module.classify("ᱢᱤᱫᱥᱟᱭ", "ᱢᱤᱫ ᱥᱟᱭ"), "spacing_only")

    def test_character_level_difference(self):
        self.assertEqual(module.classify("ᱠᱮᱢᱯ", "ᱠᱮᱢ"), "character_level_difference")

    def test_word_edit_distance(self):
        self.assertEqual(module.edit_distance(["one", "two"], ["one", "three"]), 1)


if __name__ == "__main__":
    unittest.main()
