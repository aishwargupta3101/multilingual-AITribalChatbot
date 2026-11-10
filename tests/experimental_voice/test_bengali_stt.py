
from pathlib import Path

from backend.experimental_voice.bengali_script.stt import (
    BengaliScriptSTT,
)


def main():
    audio_path = input(
        "Enter the full path of your Manipuri audio file: "
    ).strip().strip('"')

    stt = BengaliScriptSTT()

    print("\nStarting experimental STT test...\n")

    result = stt.transcribe(audio_path)

    print("=" * 60)
    print("EXPERIMENTAL STT RESULT")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 60)


if __name__ == "__main__":
    main()