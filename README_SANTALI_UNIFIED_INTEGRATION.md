# Tribal AI — Unified Santali Integration (recovery-aware installer)

This is an **integration package for your existing repository**, not a second chatbot project. Extract it at the root of `multilingual-AITribalChatbot` so the temporary `santali_unified_payload/` and `scripts/` folders are alongside your existing `frontend/` and `backend/` folders. The installer removes the staging payload after successful installation.

## Important recovery behavior

Your current `frontend/views/voice.py` was found to contain `show_santali_voice_page(...)` instead of the application's expected `show_voice_page()`. That explains the installer validation error. This package handles that state automatically:

1. backs up the current `voice.py` before it changes anything;
2. preserves its Santali page code as `frontend/views/santali_voice.py`;
3. restores the general Voice Assistant entrypoint from the last general voice file uploaded earlier in this conversation (`voice_legacy_base.py` bundled in the payload); and
4. adds a route that sends the selected Santali language to the dedicated Santali voice page while leaving other languages on the general voice page.

Because the restored general voice page is based on the prior uploaded source, review it against any personal changes you made to the old generic voice page after that upload. The current Santali-only page is preserved separately.

## Install

From the root of your existing project with its `.venv` activated:

```powershell
python scripts/install_santali_unified.py
```

Do not run a backend or install packages just to run the installer. It validates the project files first and writes only after it can prepare the changes. It creates `.santali_unified.bak` backups before overwriting files.

Then run the environment checker:

```powershell
python scripts/check_santali_unified_dependencies.py
```

The installer updates the existing `requirements.txt`/recognized existing requirement files only when required entries are missing; it does not create a new Santali-specific requirements file. Do not reinstall the full dependency list unless the checker reports missing dependencies.

## Intended user experience

With **Santali (Ol Chiki)** selected as the reply language:

- Typed English question → existing Tribal AI chatbot/RAG → Santali translated answer.
- Typed Ol Chiki question → English translation → existing chatbot/RAG → Santali translated answer.
- Voice input lets the user choose whether the spoken question is English or Santali. English uses the existing ASR route; Santali uses the ONNX STT endpoint. Both request a Santali answer.
- Santali text answers attempt optional Santali Piper-based speech output; the text remains visible if TTS fails.

There is no per-conversation experimental checkbox in the target flow. The Santali STT endpoint is enabled by default by the installer, unless an explicit false override remains elsewhere in the environment. Do not expose an experimental endpoint publicly until authentication, resource limits and broader evaluation have been reviewed.

## Validate after installation

```powershell
python -m py_compile frontend\components\chat_box.py frontend\views\voice.py frontend\views\santali_voice.py frontend\api\santali_onnx_client.py frontend\api\santali_translation.py frontend\api\santali_chat_bridge.py frontend\api\santali_tts.py backend\main.py backend\tribal_languages\santali_onnx_router.py backend\tribal_languages\santali_onnx_stt_service.py backend\tribal_languages\santali_language_router.py backend\tribal_languages\santali_translation_service.py backend\tribal_languages\santali_tts_service.py
python -m unittest discover -s tests -p "test_santali_unified.py" -v
python -m unittest discover -s tests -p "test_santali_voice_source.py" -v
python -m unittest discover -s tests -p "test_santali_onnx_router.py" -v
```

Then start the backend and Streamlit normally. Select Santali (Ol Chiki), type a simple English question and confirm the text response. Then type a short Ol Chiki question, followed by voice questions in English and Santali. The first translation/TTS use may download models and may be slow.

## Honest status

The Santali ONNX STT endpoint was previously tested locally with Common Voice audio. The new translation → chat → Santali text and Santali TTS flow still needs live model execution, adequate-memory review and language-quality review by a Santali speaker. This package wires the intended route; it cannot guarantee the generated translation or speech is linguistically correct.
