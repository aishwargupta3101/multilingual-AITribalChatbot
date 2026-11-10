import os
import sys
import unittest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

from backend.tribal_languages.santali_translation_service import _model_config
from api.santali_chat_bridge import (
    ask_santali_question,
    build_translated_chat_prompt,
    detect_source_language,
    extract_chat_answer,
)
from api import santali_translation, santali_tts


class SantaliUnifiedTests(unittest.TestCase):
    def test_language_codes_and_models_are_set_for_both_directions(self):
        to_english = _model_config("sat_to_en")
        to_santali = _model_config("en_to_sat")
        self.assertEqual(to_english[1:], ("sat_Olck", "eng_Latn"))
        self.assertEqual(to_santali[1:], ("eng_Latn", "sat_Olck"))
        self.assertIn("indic-en", to_english[0])
        self.assertIn("en-indic", to_santali[0])

    def test_prompt_instructs_clear_answer_and_uncertainty(self):
        prompt = build_translated_chat_prompt("What is this?")
        self.assertIn("What is this?", prompt)
        self.assertIn("machine-translated", prompt)
        self.assertIn("ask one concise clarification", prompt)

    def test_empty_chat_answer_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_chat_answer({"success": True, "data": {"answer": "  "}})

    @patch("api.santali_chat_bridge.translate_english_to_santali", return_value="ᱚᱞ ᱪᱤᱠᱤ ᱛᱮ ᱵᱟᱝ")
    @patch("api.santali_chat_bridge._chat_call")
    @patch("api.santali_chat_bridge.translate_santali_to_english", return_value="What is the weather?")
    def test_full_typed_chat_translates_in_and_out(self, mock_in, mock_chat, mock_out):
        mock_chat.return_value = {
            "success": True,
            "data": {
                "answer": "I need a current weather source to answer accurately.",
                "sources": ["weather-tool"],
                "images": [],
                "timestamp": "test-time",
            },
        }
        result = ask_santali_question("ᱟᱞᱮ ᱪᱮᱫ?", "session-123")
        self.assertEqual(result["language"], "santali")
        self.assertEqual(result["answer"], "ᱚᱞ ᱪᱤᱠᱤ ᱛᱮ ᱵᱟᱝ")
        self.assertEqual(result["english_question"], "What is the weather?")
        self.assertEqual(result["sources"], ["weather-tool"])
        mock_in.assert_called_once_with("ᱟᱞᱮ ᱪᱮᱫ?")
        mock_out.assert_called_once_with("I need a current weather source to answer accurately.")
        mock_chat.assert_called_once()
        args, kwargs = mock_chat.call_args
        self.assertEqual(args[1] if len(args) > 1 else kwargs["session_id"], "session-123")
        self.assertIn("What is the weather?", args[0] if args else kwargs["prompt"])

    def test_empty_santali_question_is_rejected_before_translation(self):
        with patch("api.santali_chat_bridge.translate_santali_to_english") as mocked:
            with self.assertRaises(ValueError):
                ask_santali_question(" ", "session-123")
            mocked.assert_not_called()

    def test_ol_chiki_script_is_detected_as_santali_and_latin_as_english(self):
        self.assertEqual(detect_source_language("ᱟᱞᱮ ᱪᱮᱫ?"), "santali")
        self.assertEqual(detect_source_language("What is the weather?"), "english")

    @patch("api.santali_chat_bridge.translate_santali_to_english")
    @patch("api.santali_chat_bridge.translate_english_to_santali", return_value="ᱥᱟᱱᱛᱟᱞᱤ ᱡᱚᱵᱟᱵ")
    @patch("api.santali_chat_bridge._chat_call")
    def test_english_question_returns_santali_without_input_translation(
        self, mock_chat, mock_out, mock_in
    ):
        mock_chat.return_value = {
            "success": True,
            "data": {"answer": "It is sunny today.", "sources": [], "images": []},
        }
        result = ask_santali_question("What is the weather?", "session-en")
        self.assertEqual(result["answer"], "ᱥᱟᱱᱛᱟᱞᱤ ᱡᱚᱵᱟᱵ")
        self.assertEqual(result["input_language"], "english")
        self.assertEqual(result["output_language"], "santali")
        self.assertEqual(result["english_question"], "What is the weather?")
        mock_in.assert_not_called()
        mock_out.assert_called_once_with("It is sunny today.")
        mock_chat.assert_called_once()

    @patch("api.santali_chat_bridge.translate_santali_to_english", return_value="What does this mean?")
    @patch("api.santali_chat_bridge.translate_english_to_santali", return_value="ᱥᱟᱱᱛᱟᱞᱤ")
    @patch("api.santali_chat_bridge._chat_call")
    def test_explicit_english_source_overrides_script_autodetection(
        self, mock_chat, mock_out, mock_in
    ):
        mock_chat.return_value = {"success": True, "data": {"answer": "A short answer."}}
        result = ask_santali_question("What does this mean?", "session-explicit", source_language="english")
        self.assertEqual(result["input_language"], "english")
        mock_in.assert_not_called()

    @patch("api.santali_translation.requests.post")
    def test_translation_client_calls_backend_route(self, mock_post):
        response = MagicMock()
        response.ok = True
        response.json.return_value = {"success": True, "translation": "What is this?"}
        mock_post.return_value = response
        result = santali_translation.translate_santali_to_english("ᱟᱞᱮ")
        self.assertEqual(result, "What is this?")
        args, kwargs = mock_post.call_args
        self.assertTrue(args[0].endswith("/api/v1/tribal-languages/santali/translate"))
        self.assertEqual(kwargs["json"]["direction"], "santali_to_english")

    @patch("api.santali_tts.requests.post")
    def test_tts_client_returns_backend_wav_bytes(self, mock_post):
        response = MagicMock()
        response.ok = True
        response.headers = {"content-type": "audio/wav"}
        response.content = b"RIFF-test-wave"
        mock_post.return_value = response
        result = santali_tts.synthesize_santali_wav("ᱚᱞ")
        self.assertEqual(result, b"RIFF-test-wave")


if __name__ == "__main__":
    unittest.main()
