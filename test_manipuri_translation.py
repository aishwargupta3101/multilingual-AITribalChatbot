"""Isolated English-to-Manipuri translation comparison; does not modify project files.
Run from project root: pip install sarvamai; set SARVAM_API_KEY=...; python test_manipuri_translation.py
"""
import os
import textwrap
from dotenv import load_dotenv
load_dotenv()
SAMPLE_TEXTS = [
    "Artificial intelligence is a field of computer science.",
    "Education helps students learn new skills and understand the world.",
    "The government provides scholarships to eligible students.",
]

def try_existing_nllb(text):
    try:
        from backend.translation.nllb_service import nllb_service
        return nllb_service.translate(text=text, source_language="english", target_language="manipuri")
    except Exception as exc:
        return f"[NLLB test failed: {type(exc).__name__}: {exc}]"

def try_sarvam(text):
    api_key = os.getenv("SARVAM_API_KEY", "").strip()
    if not api_key:
        return "[Skipped: set SARVAM_API_KEY to enable Sarvam comparison]"
    try:
        from sarvamai import SarvamAI
        client = SarvamAI(api_subscription_key=api_key)
        response = client.text.translate(input=text[:2000], source_language_code="en-IN", target_language_code="mni-IN", model="sarvam-translate:v1")
        result = getattr(response, "translated_text", None)
        if result:
            return result
        if isinstance(response, dict):
            return response.get("translated_text", str(response))
        return str(response)
    except Exception as exc:
        return f"[Sarvam test failed: {type(exc).__name__}: {exc}]"

def main():
    print("=" * 72)
    print("ISOLATED MANIPURI TRANSLATION TEST — no project files are changed")
    print("=" * 72)
    for index, source in enumerate(SAMPLE_TEXTS, 1):
        print(f"\nTEST {index}\nENGLISH: {source}\n")
        print("CURRENT NLLB:")
        print(textwrap.fill(str(try_existing_nllb(source)), width=100))
        print("\nSARVAM TRANSLATE:")
        print(textwrap.fill(str(try_sarvam(source)), width=100))
        print("-" * 72)
    print("Compare meaning and natural Manipuri wording with a fluent speaker.")
    print("Do not switch production routing based on one test sentence.")

if __name__ == "__main__":
    main()
