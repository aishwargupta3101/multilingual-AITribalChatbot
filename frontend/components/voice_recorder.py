
import logging
import streamlit as st
from api.client import APIClient
logger = logging.getLogger(__name__)
def show_voice_recorder():
    st.subheader("🎤 Voice Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "language" not in st.session_state:
        st.session_state.language = "english"
    audio = st.audio_input("Record your question")
    if audio is None:
        return
    st.audio(audio)
    if not st.button("Convert Speech to Text", key="convert_voice"):
        return
    with st.spinner("Transcribing your voice..."):
        result = APIClient.speech_to_text(
            audio.getvalue(),
            st.session_state.language,
        )
    if not result.get("success"):
        st.error(
            result.get("error", "Speech recognition failed.")
        )
        return

    question = str(result.get("text", "")).strip()
    if not question:
        st.warning("No speech was detected. Please try again.")
        return
    st.success("Speech converted successfully!")
    st.session_state.voice_text = question
    st.markdown("### 🎤 You Said")
    st.info(question)
    session_id = st.session_state.get("session_id")
    if not session_id:
        st.error(
            "Chat session is not initialized. Please start a new chat."
        )
        return
    with st.spinner("Generating response..."):
        chat_result = APIClient.chat(
            question=question,
            session_id=session_id,
            language=st.session_state.language,
        )

    if not chat_result.get("success"):
        st.error(
            chat_result.get("error", "Failed to generate a response.")
        )
        return
    data = chat_result.get("data") or {}
    answer = str(data.get("answer", "")).strip()
    if not answer:
        st.error("The chatbot returned an empty response.")
        return
    st.session_state.voice_response = answer
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })
    st.markdown("### 🤖 AI Response")
    st.success(answer)
    language = (
        st.session_state.language.lower().strip()
    )
    if language not in {"english", "hindi"}:
        st.info(
            "Voice playback is currently supported only "
            "for English and Hindi. Your text response is available above."
        )
        return

    with st.spinner("Generating voice response..."):
        audio_bytes = APIClient.text_to_speech(
            text=answer,
            language=language,
        )
    if not audio_bytes:
        st.warning(
            "The AI answer was generated, but audio playback failed. "
            "Please check the backend terminal for TTS errors."
        )
        return
    st.markdown("### 🔊 AI Voice")
    st.audio(audio_bytes, format="audio/mp3")