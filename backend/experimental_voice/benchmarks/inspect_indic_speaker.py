from TTS.utils.synthesizer import Synthesizer

FASTPITCH_MODEL = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\best_model.pth"
FASTPITCH_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\config.json"
SPEAKERS_FILE = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\speakers.pth"
HIFIGAN_MODEL = r"C:\Users\kunda\Downloads\mni\mni\hifigan\best_model.pth"
HIFIGAN_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\hifigan\config.json"

synthesizer = Synthesizer(
    tts_checkpoint=FASTPITCH_MODEL,
    tts_config_path=FASTPITCH_CONFIG,
    tts_speakers_file=SPEAKERS_FILE,
    vocoder_checkpoint=HIFIGAN_MODEL,
    vocoder_config=HIFIGAN_CONFIG,
    use_cuda=False
)

print("\n=== SPEAKER DEBUG ===")
print("tts_speakers_file:", synthesizer.tts_speakers_file)
print("speaker_manager:", synthesizer.tts_model.speaker_manager)
print("name_to_id:", synthesizer.tts_model.speaker_manager.name_to_id)
print("num_speakers:", synthesizer.tts_model.speaker_manager.num_speakers)
print("=====================")