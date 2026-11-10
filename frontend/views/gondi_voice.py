"""Gondi voice view: recording/upload -> MMS ASR -> existing chat/RAG -> Gondi MT -> MMS TTS."""
from __future__ import annotations

import uuid
import streamlit as st
from streamlit_mic_recorder import mic_recorder

try:
    from api.gondi_speech import synthesize_gondi_audio, transcribe_gondi_audio
    from api.gondi_chat_bridge import ask_gondi_question
except ModuleNotFoundError:
    from frontend.api.gondi_speech import synthesize_gondi_audio, transcribe_gondi_audio
    from frontend.api.gondi_chat_bridge import ask_gondi_question


def show_gondi_voice_page() -> None:
    st.markdown("## Gondi Voice Assistant — Adilabad Gondi")
    st.caption(
        "Experimental MMS speech models. First use downloads model files. "
        "Speech recognition/output is for Adilabad Gondi (wsg); translation requires the local mT5 fine-tuned checkpoint."
    )
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    source_mode = st.radio(
        "Question input",
        ["Record / upload Gondi audio", "Type a question"],
        horizontal=True,
        key="gondi_voice_input_mode",
    )
    if source_mode == "Record / upload Gondi audio":
        audio = mic_recorder(
            start_prompt="🎙 Start Gondi recording",
            stop_prompt="⏹ Stop recording",
            key="gondi_mms_voice_recorder",
        )
        uploaded = st.file_uploader(
            "Or upload a Gondi WAV/FLAC file",
            type=["wav", "flac"],
            key="gondi_mms_voice_upload",
        )
        audio_bytes = uploaded.getvalue() if uploaded is not None else (audio.get("bytes") if audio else None)
        filename = uploaded.name if uploaded is not None else "gondi-recording.wav"
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            if st.button("Transcribe Gondi audio", use_container_width=True, key="gondi_mms_transcribe"):
                try:
                    with st.spinner("Loading the Gondi speech model and transcribing..."):
                        result = transcribe_gondi_audio(audio_bytes, filename)
                    st.session_state["gondi_mms_last_transcript"] = str(result.get("text") or "").strip()
                    st.session_state["gondi_mms_last_raw_transcript"] = str(result.get("raw_text") or "").strip()
                    st.session_state.pop("gondi_mms_last_answer", None)
                except Exception as exc:
                    st.error(f"Gondi transcription failed: {type(exc).__name__}: {exc}")

        transcript = st.session_state.get("gondi_mms_last_transcript", "")
        if transcript:
            st.markdown("### Recognized Gondi text (Devanagari approximation)")
            st.write(transcript)
            raw = st.session_state.get("gondi_mms_last_raw_transcript", "")
            if raw and raw != transcript:
                with st.expander("Original MMS transcript"):
                    st.write(raw)
            st.caption("The script conversion is approximate; confirm the transcript with a Gondi speaker.")
            if st.button("Ask Tribal AI and answer in Gondi", use_container_width=True, key="gondi_mms_ask_from_transcript"):
                try:
                    with st.spinner("Tribal AI is answering and translating into Gondi..."):
                        answer = ask_gondi_question(transcript, st.session_state["session_id"], "gondi")
                    st.session_state["gondi_mms_last_answer"] = str(answer.get("answer") or "")
                except Exception as exc:
                    st.error(f"Gondi chat/translation failed: {type(exc).__name__}: {exc}")

    else:
        input_language = st.selectbox(
            "Question language",
            ["English", "Gondi (Devanagari)"],
            key="gondi_mms_typed_input_language",
        )
        question = st.text_area("Ask Tribal AI", key="gondi_mms_typed_question", height=110)
        if st.button("Get answer in Gondi", use_container_width=True, key="gondi_mms_typed_ask"):
            if not question.strip():
                st.warning("Enter a question first.")
            else:
                try:
                    with st.spinner("Tribal AI is answering and translating into Gondi..."):
                        answer = ask_gondi_question(
                            question,
                            st.session_state["session_id"],
                            "english" if input_language == "English" else "gondi",
                        )
                    st.session_state["gondi_mms_last_answer"] = str(answer.get("answer") or "")
                except Exception as exc:
                    st.error(f"Gondi chat/translation failed: {type(exc).__name__}: {exc}")

    answer_text = st.session_state.get("gondi_mms_last_answer", "")
    if answer_text:
        st.markdown("### Tribal AI answer in Gondi")
        st.markdown(answer_text)
        if st.button("🔊 Speak Gondi answer", use_container_width=True, key="gondi_mms_speak_answer"):
            try:
                with st.spinner("Generating Adilabad Gondi speech..."):
                    wav_data = synthesize_gondi_audio(answer_text)
                st.audio(wav_data, format="audio/wav")
                st.success("Gondi speech generated.")
            except Exception as exc:
                st.error(f"Gondi speech generation failed: {type(exc).__name__}: {exc}")


    with st.expander("Test Gondi TTS with a sentence (does not require the translator)"):
        tts_sample = st.text_area(
            "Gondi sentence in Devanagari",
            key="gondi_mms_tts_sample_text",
            height=80,
            placeholder="Enter a short Gondi sentence here",
        )
        if st.button("Generate sample speech", key="gondi_mms_tts_test", use_container_width=True):
            if not tts_sample.strip():
                st.warning("Enter a Gondi sentence first.")
            else:
                try:
                    with st.spinner("Loading MMS TTS and generating sample speech..."):
                        sample_wav = synthesize_gondi_audio(tts_sample)
                    st.audio(sample_wav, format="audio/wav")
                except Exception as exc:
                    st.error(f"Gondi TTS sample failed: {type(exc).__name__}: {exc}")

    st.divider()
    st.caption(
        "Readiness: GET /api/v1/tribal-languages/gondi/status. "
        "MMS ASR/TTS and the trained translation model are experimental; this is not a claim of native-speaker-verified accuracy."
    )
