
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from backend.schemas.chat import ChatRequest
from backend.services.chat_service import chat_service
from backend.repositories.chat_repository import chat_repository
from backend.repositories.session_repository import session_repository
from backend.experimental_voice.meitei_mayek.stt import ExperimentalMeiteiSTT
from backend.experimental_voice.bengali_script.tts import ExperimentalManipuriTTS
ROOT = Path(__file__).resolve().parents[3]
AUDIO_PATH = ROOT / "experimental_outputs" / "manipuri_tts" / "manipuri_meitei_mayek_test.wav"
OUTPUT_DIR = ROOT / "experimental_outputs" / "end_to_end"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
async def run_test():
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Test audio not found: {AUDIO_PATH}")
    results = {
        "success": False,
        "input_audio": str(AUDIO_PATH),
        "steps": {},
    }
    total_start = time.perf_counter()
    stt = ExperimentalMeiteiSTT()
    tts = ExperimentalManipuriTTS()
    # Step 1: Speech recognition
    start = time.perf_counter()
    stt_result = stt.transcribe(str(AUDIO_PATH))
    recognized_text = stt_result.get("text", "").strip()
    results["steps"]["stt"] = {
        **stt_result,
        "success": bool(recognized_text),
        "elapsed_seconds": round(time.perf_counter() - start, 2),
    }
    if not recognized_text:
        raise RuntimeError("STT returned empty text.")
    print("\nSTT:", recognized_text)
    # Step 2: Chatbot, with persistence disabled for this test
    session_id = f"phase8-test-{uuid4().hex}"
    request = ChatRequest(
        question=recognized_text,
        session_id=session_id,
        language="manipuri_mtei",
    )
    start = time.perf_counter()
    with (
        patch.object(
            session_repository,
            "create_session",
            new_callable=AsyncMock,
        ),
        patch.object(
            session_repository,
            "update_activity",
            new_callable=AsyncMock,
        ),
        patch.object(
            chat_repository,
            "get_recent_message",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch.object(
            chat_repository,
            "save_message",
            new_callable=AsyncMock,
        ),
    ):
        chat_result = await chat_service.process_chat(request)
    chat_elapsed = time.perf_counter() - start
    if not isinstance(chat_result, dict):
        raise TypeError(
            "Unexpected chat response type. Inspect ResponseBuilder.success()."
        )
    chat_data = chat_result.get("data", {})
    answer = chat_data.get("answer", "").strip()
    if not answer:
        raise RuntimeError(
            f"Chatbot returned no answer. Response: {chat_result}"
        )
    results["steps"]["chatbot"] = {
        "success": True,
        "answer": answer,
        "language": chat_data.get("language"),
        "answer_source": chat_data.get("answer_source"),
        "elapsed_seconds": round(chat_elapsed, 2),
    }
    print("\nChatbot response:", answer)
    # Step 3: Generate audio from the already-translated answer
    start = time.perf_counter()
    tts_result = tts.generate(
        text=answer,
        script="meitei_mayek",
        output_name="phase8_meitei_mayek_response.wav",
    )
    tts_elapsed = time.perf_counter() - start
    results["steps"]["tts"] = {
        **tts_result,
        "elapsed_seconds": round(tts_elapsed, 2),
    }
    if not tts_result.get("success"):
        raise RuntimeError(f"TTS failed: {tts_result.get('error')}")
    results["success"] = True
    results["total_elapsed_seconds"] = round(
        time.perf_counter() - total_start, 2
    )
    output_file = OUTPUT_DIR / "phase8_results.json"
    output_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("\n========== PHASE 8 RESULT ==========")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nResults saved to: {output_file}")
    print("====================================")
if __name__ == "__main__":
    asyncio.run(run_test())