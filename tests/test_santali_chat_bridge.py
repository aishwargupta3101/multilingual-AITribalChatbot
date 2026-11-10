
import os
import sys
import unittest
from unittest.mock import patch

# Make the frontend API imports available during testing.
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

from api.santali_chat_bridge import (
    ask_santali_transcription,
    build_santali_interpretation_prompt,
    extract_chat_answer,
)


class SantaliChatBridgeTests(unittest.TestCase):

    def test_prompt_includes_transcription_and_cautious_instructions(self):
        transcript = "ᱟᱡ ᱵᱟᱵᱟ"

        prompt = build_santali_interpretation_prompt(transcript)

        self.assertIn(transcript, prompt)
        self.assertIn("Do not invent a meaning", prompt)

    def test_empty_transcript_is_rejected(self):
        with self.assertRaises(ValueError):
            build_santali_interpretation_prompt("  ")

    def test_extracts_nested_chat_answer(self):
        response = {
            "success": True,
            "data": {
                "answer": "Possible meaning: hello."
            },
        }

        answer = extract_chat_answer(response)

        self.assertEqual(answer, "Possible meaning: hello.")

    def test_chat_error_is_propagated(self):
        response = {
            "success": False,
            "error": "Chat not available",
        }

        with self.assertRaisesRegex(RuntimeError, "not available"):
            extract_chat_answer(response)

    @patch("api.santali_chat_bridge._chat_call")
    def test_uses_existing_chat_api_in_english(self, mock_chat):
        mock_chat.return_value = {
            "success": True,
            "data": {
                "answer": "I may have understood this as a greeting."
            },
        }

        answer = ask_santali_transcription(
            "ᱟᱡ ᱵᱟᱵᱟ",
            "test-session",
        )

        self.assertIn("greeting", answer)
        mock_chat.assert_called_once()

        args, kwargs = mock_chat.call_args

        prompt = args[0] if args else kwargs["prompt"]
        session_id = args[1] if len(args) > 1 else kwargs["session_id"]

        self.assertEqual(session_id, "test-session")
        self.assertIn("ᱟᱡ ᱵᱟᱵᱟ", prompt)


if __name__ == "__main__":
    unittest.main()
