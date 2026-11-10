import requests
import streamlit as st
LOCAL_TTS_URL = "http://127.0.0.1:8002/tts"
def show_manipuri_tts_component():
    st.subheader("Manipuri Voice Assistant")
    script = st.selectbox(
        "Select Manipuri script",
        options=["bengali", "meitei_mayek"],
        format_func=lambda x: "Bengali Script" if x == "bengali" else "Meitei Mayek",
        key="manipuri_tts_script"
    )
    text = st.text_area(
        "Enter Manipuri text",
        placeholder="Enter your Manipuri text here...",
        height=120,
        key="manipuri_tts_text"
    )
    if st.button("Generate Manipuri Speech", key="generate_manipuri_tts"):
        if not text.strip():
            st.warning("Please enter text first.")
        else:
            with st.spinner("Generating Manipuri speech. This may take several minutes on CPU..."):
                try:
                    response = requests.post(
                        LOCAL_TTS_URL,
                        json={"text": text.strip(), "script": script},
                        timeout=900
                    )
                    if response.status_code == 200:
                        st.session_state["manipuri_audio_bytes"] = response.content
                        st.session_state["manipuri_audio_script"] = script
                        st.session_state["manipuri_audio_text"] = text.strip()
                        st.success("Manipuri speech generated successfully!")
                    else:
                        st.error(f"TTS failed ({response.status_code}): {response.text}")
                except requests.exceptions.Timeout:
                    st.error("Speech generation timed out. Please try again.")
                except requests.exceptions.RequestException as exc:
                    st.error(f"Could not connect to the local Manipuri TTS server: {exc}")
    audio_bytes = st.session_state.get("manipuri_audio_bytes")
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.download_button(
            "Download Manipuri Audio",
            data=audio_bytes,
            file_name="manipuri_speech.wav",
            mime="audio/wav",
            key="download_manipuri_tts"
        )