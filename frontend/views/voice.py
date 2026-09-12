import os
import html
import uuid
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from api.client import APIClient
from api.endpoints import SPEECH_UPLOAD_ENDPOINT


def html_block(html_content):
    html_content = " ".join(
        line.strip()
        for line in html_content.splitlines()
        if line.strip()
    )
    st.markdown(
        html_content,
        unsafe_allow_html=True
    )
def show_voice_page():
    language = st.session_state.get(
        "language",
        "english"
    )
    language_name = (
        language
        .replace("_", " ")
        .title()
    )
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(
            uuid.uuid4()
        )
    session_id = st.session_state["session_id"]
    html_block(
        f"""
        <div class="voice-page-header">

            <div class="voice-header-icon">
                🎤
            </div>

            <div class="voice-header-content">

                <div class="voice-header-title">
                    Voice Assistant
                </div>

                <div class="voice-header-subtitle">
                    Speak naturally and interact with Tribal AI.
                </div>

            </div>

            <div class="voice-header-language">
                {html.escape(language_name)}
            </div>

        </div>
        """
    )

    html_block(
        f"""
        <div class="voice-language-card">

            <div class="voice-language-icon">
                🌐
            </div>

            <div class="voice-language-content">

                <div class="voice-language-title">
                    Current Voice Language
                </div>

                <div class="voice-language-text">
                    Your voice interaction will use the selected
                    conversation language.
                </div>

            </div>

            <div class="voice-language-badge">
                {html.escape(language_name)}
            </div>

        </div>
        """
    )
    html_block(
        """
        <div class="voice-record-card">

            <div class="voice-record-icon">
                🎙️
            </div>

            <div class="voice-record-title">
                Start speaking
            </div>

            <div class="voice-record-text">
                Press the microphone and speak your question.
            </div>

        </div>
        """
    )
    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop Recording",
        key="voice_recorder"
    )

    if audio:
        os.makedirs(
            "data/audio",
            exist_ok=True
        )
        audio_path = "data/audio/user_audio.wav"
        with open(
            audio_path,
            "wb"
        ) as f:
            f.write(
                audio["bytes"]
            )

        st.audio(
            audio["bytes"],
            format="audio/wav"
        )
        if st.button(
            "🌿 Process Voice",
            use_container_width=True,
            key="process_voice"
        ):
            try:
                with st.spinner(
                    "🎙 Converting your voice to text..."
                ):
                    speech_response = (
                        APIClient.upload_audio(
                            SPEECH_UPLOAD_ENDPOINT,
                            audio_path,
                            language
                        )
                    )
            except Exception as e:
                st.error(
                    f"Speech recognition failed: {e}"
                )
                return

            if not isinstance(
                speech_response,
                dict
            ):
                st.error(
                    "Invalid response from speech service."
                )
                return

            if not speech_response.get(
                "success",
                False
            ):
                st.error(
                    speech_response.get(
                        "error",
                        "Speech recognition failed."
                    )
                )
                return

            transcription = (
                speech_response.get("transcription")
                or speech_response.get("text")
                or speech_response.get("transcript")
                or ""
            )
            transcription = str(
                transcription
            ).strip()

            if not transcription:
                st.warning(
                    "Voice was processed, "
                    "but no transcription was returned."
                )
                with st.expander(
                    "View Processing Details"
                ):
                    st.json(
                        speech_response
                    )
                return

            st.success(
                "Voice processed successfully."
            )
            safe_transcription = html.escape(
                transcription
            )
            html_block(
                f"""
                <div class="voice-result-card">

                    <div class="voice-result-label">
                        YOUR TRANSCRIPTION
                    </div>

                    <div class="voice-result-text">
                        {safe_transcription}
                    </div>

                </div>
                """
            )
            print("=" * 60)
            print("VOICE → CHAT")
            print("Question:", transcription)
            print("Session ID:", session_id)
            print("Language:", language)
            print("=" * 60)

            try:
                with st.spinner(
                    "🌿 Tribal AI is thinking..."
                ):
                    chat_response = APIClient.chat(
                        question=transcription,
                        session_id=session_id,
                        language=language
                    )
                print("=" * 60)
                print("CHAT API RESPONSE")
                print(chat_response)
                print("=" * 60)

            except Exception as e:
                print("=" * 60)
                print("CHAT API ERROR")
                print(repr(e))
                print("=" * 60)
                st.error(
                    f"AI response failed: {e}"
                )
                return

            answer = ""
            if isinstance(
                chat_response,
                dict
            ):

                answer = (
                    chat_response.get("answer")
                    or chat_response.get("ai_response")
                    or chat_response.get("generated_answer")
                    or chat_response.get("content")
                    or ""
                )

                if not answer:
                    data = chat_response.get(
                        "data"
                    )
                    if isinstance(
                        data,
                        dict
                    ):
                        answer = (
                            data.get("answer")
                            or data.get("ai_response")
                            or data.get("generated_answer")
                            or data.get("content")
                            or ""
                        )
                    elif isinstance(
                        data,
                        str
                    ):
                        answer = data

                if not answer:
                    response_data = (
                        chat_response.get(
                            "response"
                        )
                    )
                    if isinstance(
                        response_data,
                        dict
                    ):
                        answer = (
                            response_data.get("answer")
                            or response_data.get("content")
                            or ""
                        )
                    elif (
                        isinstance(
                            response_data,
                            str
                        )
                        and response_data.strip().lower()
                        not in {
                            "chat processed successfully",
                            "processed successfully"
                        }
                    ):
                        answer = response_data
            answer = str(
                answer
            ).strip()

            if not answer:
                st.warning(
                    "The question was transcribed, "
                    "but Tribal AI did not return an answer."
                )
                with st.expander(
                    "View Chat API Response"
                ):
                    st.json(
                        chat_response
                    )
                return
            safe_answer = (
                html.escape(answer)
                .replace(
                    "\n",
                    "<br>"
                )
            )
            html_block(
                f"""
                <div class="voice-ai-card">

                    <div class="voice-ai-header">

                        <div class="voice-ai-icon">
                            🌿
                        </div>

                        <div>

                            <div class="voice-ai-title">
                                Tribal AI
                            </div>

                            <div class="voice-ai-language">
                                {html.escape(language_name)}
                            </div>

                        </div>

                    </div>

                    <div class="voice-ai-response">
                        {safe_answer}
                    </div>

                </div>
                """
            )
            if language not in {
                "english",
                "hindi"
            }:
                st.info(
                    f"Voice output is not currently available "
                    f"for {language_name}."
                )

                return

            try:
                with st.spinner(
                    "🔊 Generating voice response..."
                ):
                    tts_response = (
                        APIClient.text_to_speech(
                            text=answer,
                            language=language
                        )
                    )
            except Exception as e:
                print("=" * 60)
                print("TTS ERROR")
                print(repr(e))
                print("=" * 60)
                st.error(
                    f"Voice response generation failed: {e}"
                )
                return
            if not tts_response:
                st.warning(
                    "AI answer was generated, "
                    "but no audio response was returned."
                )
                return
            st.markdown(
                "### 🔊 Tribal AI Voice Response"
            )
            st.audio(
                tts_response,
                format="audio/mp3"
            )
            st.success(
                "Voice response generated successfully."
            )
    else:
        html_block(
            """
            <div class="voice-empty-card">

                <div class="voice-empty-icon">
                    🎤
                </div>

                <div class="voice-empty-title">
                    No recording yet
                </div>

                <div class="voice-empty-text">
                    Start a recording above to ask Tribal AI
                    a question using your voice.
                </div>

            </div>
            """
        )
    html_block(
        f"""
        <div class="voice-footer-info">

            <div class="voice-footer-item">
                🎙 Voice Input
            </div>

            <div class="voice-footer-item">
                🌐 {html.escape(language_name)}
            </div>

            <div class="voice-footer-item">
                🌿 Tribal AI
            </div>

        </div>
        """
    )