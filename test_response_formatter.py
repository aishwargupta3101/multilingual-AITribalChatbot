import unittest
from backend.services.response_formatter import format_response, format_for_voice

class FormatterTests(unittest.TestCase):
    def test_heading_spacing(self):
        self.assertIn("## Artificial Intelligence", format_response("##Artificial Intelligence", "english"))
    def test_preserve_hindi_and_manipuri(self):
        self.assertIn("AI उपयोगी है।", format_response("##कृत्रिम बुद्धिमत्ता\n\nAI उपयोगी है।", "hindi"))
        self.assertIn("ꯃꯁꯤ ꯐꯖꯩ", format_response("##ꯃꯤꯇꯩ\n\nꯃꯁꯤ ꯐꯖꯩ", "manipuri"))
    def test_long_flat_paragraph_gets_breaks(self):
        text = "Sentence one. Sentence two. Sentence three. Sentence four. " * 6
        result = format_response(text, "english")
        self.assertIn("\n\n", result)
    def test_voice_removes_markdown(self):
        result = format_for_voice("## Heading\n\nThis is **important**.\n- First item", "manipuri")
        self.assertNotIn("##", result)
        self.assertNotIn("**", result)
        self.assertIn("important", result)
        self.assertIn("First item", result)

if __name__ == "__main__":
    unittest.main()
