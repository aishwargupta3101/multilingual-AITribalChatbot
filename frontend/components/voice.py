import os
from http.client import responses

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from api.client import APIClient
from api.endpoints import SPEECH_UPLOAD_ENDPOINT

def show_voice():
    st.subheader("🎤 Voice Chat")
    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop Recording",
        key="voice_recorder"
    )
    if audio:
        os.makedirs("data/audio",exist_ok=True)
        audio_path="data/audio/user_audio.wav"
        with open(audio_path,"wb") as f:
            f.write(audio["bytes"])
        st.audio(audio["bytes"])
        if st.button("Upload Voice"):
            response =APIClient.upload_audio(
                SPEECH_UPLOAD_ENDPOINT,
                audio_path
            )
            st.success("Voice Uploaded")
            st.json(response)