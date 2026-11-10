from TTS.utils.synthesizer import Synthesizer

FASTPITCH_MODEL = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\best_model.pth"
FASTPITCH_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\config.json"
FASTPITCH_SPEAKERS = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\speakers.pth"
HIFIGAN_MODEL = r"C:\Users\kunda\Downloads\mni\mni\hifigan\best_model.pth"
HIFIGAN_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\hifigan\config.json"

print("Loading AI4Bharat Manipuri TTS...")

synthesizer = Synthesizer(
    tts_checkpoint=FASTPITCH_MODEL,
    tts_config_path=FASTPITCH_CONFIG,
    vocoder_checkpoint=HIFIGAN_MODEL,
    vocoder_config=HIFIGAN_CONFIG,
    use_cuda=False
)

print("MODEL LOAD: SUCCESS")
print("Sample rate:", synthesizer.output_sample_rate)