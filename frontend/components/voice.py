
import os
import tempfile
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from api.client import APIClient
from backend.translation.meitei_script_converter import convert_bengali_to_meitei

SUPPORTED_LANGUAGES = {
    "English": "english",
    "Hindi": "hindi",
    "Manipuri": "manipuri"
}

def show_voice_component():
    st.subheader("🎙 Voice Translation")
    col1, col2 = st.columns(2)
    with col1:
        input_label = st.selectbox(
            "Input Language",
            list(SUPPORTED_LANGUAGES.keys()),
            key="voice_input_language"
        )
    with col2:
        response_label = st.selectbox(
            "Response Language",
            list(SUPPORTED_LANGUAGES.keys()),
            index=1,
            key="voice_response_language"
        )
    input_language = SUPPORTED_LANGUAGES[input_label]
    response_language = SUPPORTED_LANGUAGES[response_label]
    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=False,
        use_container_width=True,
        format="wav",
        key="voice_component_recorder"
    )
    if audio:
        audio_bytes = audio.get("bytes")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            if st.button(
                "🌿 Translate Voice",
                use_container_width=True,
                key="component_process_voice"
            ):
                audio_path = None
                try:
                    os.makedirs("data/audio", exist_ok=True)
                    with tempfile.NamedTemporaryFile(
                        mode="wb",
                        suffix=".wav",
                        dir="data/audio",
                        delete=False
                    ) as temp_audio:
                        temp_audio.write(audio_bytes)
                        audio_path = temp_audio.name
                    with st.spinner("🎙 Transcribing and translating..."):
                        response = APIClient.translate_audio(
                            audio_path=audio_path,
                            input_language=input_language,
                            response_language=response_language
                        )
                    if not isinstance(response, dict):
                        st.error("Invalid response from speech service.")
                    elif not response.get("success"):
                        st.error(response.get("error", "Voice translation failed."))
                    else:
                        transcription = str(
                            response.get("transcription") or ""
                        ).strip()
                        translated_text = str(
                            response.get("translated_text") or ""
                        ).strip()
                        if not transcription:
                            st.warning("No speech could be recognized.")
                        else:
                            st.session_state["voice_transcription"] = transcription
                            st.session_state["voice_translated_text"] = translated_text
                            st.session_state["voice_response_language"] = response_language
                            st.session_state["voice_response_label"] = response_label
                            st.success("Voice processed successfully.")
                except Exception as e:
                    st.error(f"Voice translation failed: {e}")
                finally:
                    if audio_path and os.path.exists(audio_path):
                        try:
                            os.remove(audio_path)
                        except OSError:
                            pass
        else:
            st.warning("No audio recording found.")
    else:
        st.info("Start recording to translate your voice.")

    transcription = st.session_state.get("voice_transcription", "")
    translated_text = st.session_state.get("voice_translated_text", "")
    saved_language = st.session_state.get("voice_response_language", "")
    saved_label = st.session_state.get("voice_response_label", "")

    if not transcription:
        return

    st.markdown("### 📝 Original Transcription")
    st.write(transcription)
    st.markdown(f"### 🌐 Translated Response ({saved_label})")
    st.write(translated_text or "No translation returned.")

    if not translated_text:
        return

    if saved_language in ("english", "hindi"):
        st.markdown("### 🔊 Voice Output")
        if st.button(
            "🔊 Generate Audio",
            use_container_width=True,
            key="generate_standard_voice"
        ):
            try:
                with st.spinner("Generating audio..."):
                    audio_response = APIClient.text_to_speech(
                        translated_text,
                        saved_language
                    )
                if audio_response:
                    st.audio(audio_response, format="audio/mp3")
                    st.download_button(
                        "⬇️ Download Audio",
                        data=audio_response,
                        file_name=f"{saved_language}_speech.mp3",
                        mime="audio/mpeg"
                    )
                else:
                    st.error("Audio generation failed.")
            except Exception as e:
                st.error(f"Audio generation failed: {e}")

    elif saved_language == "manipuri":
        st.markdown("### 🔊 Manipuri Voice Output")
        script_options = {
            "Bengali Script": "bengali",
            "Meitei Mayek": "meitei_mayek"
        }
        selected_script = st.selectbox(
            "Select Manipuri Script",
            list(script_options.keys()),
            key="manipuri_tts_script"
        )
        if st.button(
            "🎙 Generate Manipuri Speech",
            use_container_width=True,
            key="generate_manipuri_tts"
        ):
            tts_text = translated_text
            tts_script = script_options[selected_script]
            try:
                if tts_script == "meitei_mayek":
                    tts_text = convert_bengali_to_meitei(translated_text)
                    if not tts_text:
                        st.error("Could not convert the translated text to Meitei Mayek.")
                        return

                with st.spinner(
                    "Generating Manipuri speech. This may take several minutes on CPU..."
                ):
                    audio_bytes = APIClient.manipuri_text_to_speech(
                        text=tts_text,
                        script=tts_script,
                        speaker="female"
                    )

                if not audio_bytes:
                    st.error(
                        "Manipuri speech generation failed. "
                        "Check the backend logs."
                    )
                else:
                    st.success("Manipuri speech generated successfully!")
                    st.audio(audio_bytes, format="audio/wav")
                    st.download_button(
                        "⬇️ Download Manipuri Audio",
                        data=audio_bytes,
                        file_name=f"manipuri_{tts_script}.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Manipuri speech generation failed: {e}")