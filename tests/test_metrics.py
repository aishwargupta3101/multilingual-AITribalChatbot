import unittest
from scripts.evaluate_santali_single_clip import calculate_metrics, levenshtein_distance


class MetricTests(unittest.TestCase):
    def test_levenshtein(self):
        self.assertEqual(levenshtein_distance(list("kitten"), list("sitting")), 3)
        self.assertEqual(levenshtein_distance([], list("abc")), 3)

    def test_exact_match(self):
        m = calculate_metrics("ᱤᱧᱟᱜ ᱵᱚᱦᱚᱜ", "ᱤᱧᱟᱜ ᱵᱚᱦᱚᱜ")
        self.assertTrue(m["exact_match"])
        self.assertEqual(m["cer_with_spaces"], 0)
        self.assertEqual(m["cer_without_spaces"], 0)
        self.assertEqual(m["wer"], 0)

    def test_spacing_only_match(self):
        m = calculate_metrics("ᱢᱤᱫᱥᱟᱭ", "ᱢᱤᱫ ᱥᱟᱭ")
        self.assertFalse(m["exact_match"])
        self.assertTrue(m["spacing_only_match"])
        self.assertEqual(m["cer_without_spaces"], 0)
        self.assertGreater(m["wer"], 0)

    def test_character_error(self):
        m = calculate_metrics("abc", "axc")
        self.assertEqual(m["char_edits_with_spaces"], 1)
        self.assertAlmostEqual(m["cer_with_spaces"], 1/3)


if __name__ == "__main__":
    unittest.main()
