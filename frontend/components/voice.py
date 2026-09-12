import os

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from api.client import APIClient
from api.endpoints import SPEECH_UPLOAD_ENDPOINT

def show_voice_component():
    language = st.session_state.get(
        "language",
        "english"
    )
    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=False,
        use_container_width=True,
        format="wav",
        key="voice_component_recorder"
    )
    if not audio:
        return
    os.makedirs(
        "data/audio",
        exist_ok=True
    )
    audio_path = os.path.join(
        "data/audio",
        "user_audio.wav"
    )
    try:
        with open(
            audio_path,
            "wb"
        ) as f:
            f.write(
                audio["bytes"]
            )

    except Exception as e:
        st.error(
            f"Unable to save recording: {e}"
        )
        return

    st.audio(
        audio["bytes"],
        format="audio/wav"
    )
    if st.button(
        "🌿 Process Voice",
        use_container_width=True,
        key="component_process_voice"
    ):
        try:
            with st.spinner(
                "🎙 Converting voice to text..."
            ):
                response = APIClient.upload_audio(
                    SPEECH_UPLOAD_ENDPOINT,
                    audio_path,
                    language
                )
        except Exception as e:
            st.error(
                f"Speech recognition failed: {e}"
            )
            return
        if not isinstance(
            response,
            dict
        ):
            st.error(
                "Invalid speech service response."
            )
            return
        if not response.get(
            "success",
            False
        ):
            st.error(
                response.get(
                    "error",
                    "Speech recognition failed."
                )
            )
            return
        transcription = (
            response.get("transcription")
            or response.get("text")
            or response.get("transcript")
            or ""
        )
        transcription = str(
            transcription
        ).strip()
        if not transcription:
            st.warning(
                "No speech could be recognized."
            )
            return
        st.success(
            "Voice processed successfully."
        )
        st.markdown(
            "### Your Transcription"
        )
        st.write(
            transcription
        )

