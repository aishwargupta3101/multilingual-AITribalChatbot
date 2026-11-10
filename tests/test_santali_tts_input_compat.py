import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SantaliTtsInputCompatibilityTests(unittest.TestCase):
    def test_tts_service_uses_actual_onnx_input_names(self):
        source = (ROOT / "backend/tribal_languages/santali_tts_service.py").read_text(encoding="utf-8")
        self.assertIn("actual_input_names = [item.name for item in session.get_inputs()]", source)
        self.assertIn("input_feed = {name: candidate_feed[name] for name in actual_input_names}", source)
        self.assertNotIn('"sid": np.asarray([0], dtype=np.int64),\n        },', source)

    def test_santali_voice_uses_common_voice_assistant_heading(self):
        source = (ROOT / "frontend/views/santali_voice.py").read_text(encoding="utf-8")
        self.assertIn('st.markdown("## Voice Assistant")', source)
        self.assertNotIn('st.markdown("## Santali Voice Assistant")', source)

if __name__ == "__main__":
    unittest.main()
