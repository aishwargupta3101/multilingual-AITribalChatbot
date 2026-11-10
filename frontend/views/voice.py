"""
Tribal AI — Voice Studio
A redesigned Streamlit voice translation page.

The existing speech/translation API calls and language codes are intentionally
preserved. Styling is additive and local to the voice page.
"""
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from api.client import APIClient

# Make the project root importable when Streamlit is launched from frontend/.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.translation.meitei_script_converter import convert_bengali_to_meitei


SUPPORTED_LANGUAGES = {
    "English": "english",
    "Hindi": "hindi",
    "Manipuri": "manipuri",
    "Assamese": "assamese",
    "Bengali": "bengali",
    "Gujarati": "gujarati",
    "Kannada": "kannada",
    "Malayalam": "malayalam",
    "Marathi": "marathi",
    "Nepali": "nepali",
    "Punjabi": "punjabi",
    "Sanskrit": "sanskrit",
    "Tamil": "tamil",
    "Telugu": "telugu",
    "Urdu": "urdu",
}


def _voice_styles() -> None:
    """Inject page-specific styling without replacing the app's global theme."""
    st.markdown(
        """
        <style>
        :root {
            --voice-bg: #070b08;
            --voice-panel: #101812;
            --voice-panel-2: #142219;
            --voice-border: #2a4331;
            --voice-green: #49d982;
            --voice-green-bright: #75efa0;
            --voice-text: #eff7f0;
            --voice-muted: #a8b9ac;
        }

        /* Page width and typography */
        .main .block-container {
            max-width: 1280px !important;
            padding-top: 1.45rem !important;
            padding-bottom: 2.8rem !important;
        }
        .voice-page-title {
            color: var(--voice-text);
            font-size: clamp(28px, 3.4vw, 42px);
            font-weight: 820;
            line-height: 1.12;
            letter-spacing: -1.3px;
            margin: 0 0 9px 0;
        }
        .voice-page-title span { color: var(--voice-green); }
        .voice-page-subtitle {
            color: var(--voice-muted);
            font-size: 14px;
            line-height: 1.75;
            max-width: 700px;
            margin: 0;
        }
        .voice-eyebrow {
            color: var(--voice-green-bright);
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 2px;
            font-weight: 850;
            margin-bottom: 12px;
        }
        .voice-hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--voice-border);
            border-radius: 22px;
            padding: clamp(22px, 3.6vw, 38px);
            margin: 0 0 22px 0;
            background:
                radial-gradient(ellipse at 82% 0%, rgba(54, 190, 103, .18), transparent 42%),
                linear-gradient(135deg, #111d14 0%, #0b100c 76%);
            box-shadow: 0 16px 40px rgba(0,0,0,.12);
        }
        .voice-hero-mark {
            display: inline-flex;
            width: 46px; height: 46px;
            align-items: center; justify-content: center;
            border-radius: 14px;
            background: #153521;
            border: 1px solid #2f6841;
            color: #80eea2;
            font-size: 24px;
            margin-bottom: 17px;
        }
        .voice-section-title {
            color: #edf6ef;
            font-size: 18px;
            font-weight: 760;
            letter-spacing: -.35px;
            margin: 0 0 5px 0;
        }
        .voice-section-subtitle {
            color: #a8b9ac;
            font-size: 12px;
            line-height: 1.65;
            margin: 0 0 14px 0;
        }
        .voice-card {
            height: 100%;
            min-height: 104px;
            padding: 16px;
            background: linear-gradient(145deg, #121d15, #0d130f);
            border: 1px solid #2b4331;
            border-radius: 15px;
        }
        .voice-card-icon {
            width: 34px; height: 34px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 11px;
            background: #153521;
            border: 1px solid #2e6942;
            color: #67e997;
            font-size: 17px;
            margin-bottom: 11px;
        }
        .voice-card-title { color: #eef6ef; font-size: 13px; font-weight: 750; margin-bottom: 5px; }
        .voice-card-text { color: #a8b9ac; font-size: 11px; line-height: 1.65; }
        .voice-kicker {
            color: #77d997;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: 1.7px;
            text-transform: uppercase;
            margin: 5px 0 10px;
        }
        .voice-status {
            display: inline-flex; align-items: center; gap: 7px;
            padding: 7px 11px; border-radius: 999px;
            border: 1px solid #2d4c36; background: #101b13;
            color: #c8ddce; font-size: 11px; font-weight: 650;
        }
        .voice-status-dot {
            width: 7px; height: 7px; border-radius: 50%;
            display: inline-block; background: #49d982;
            box-shadow: 0 0 11px rgba(73,217,130,.55);
        }
        .voice-result-card {
            background: linear-gradient(145deg, #111b14, #0c120e);
            border: 1px solid #2b4432;
            border-radius: 16px;
            padding: 17px;
            height: 100%;
        }
        .voice-result-label {
            display: flex; align-items: center; gap: 8px;
            color: #79e59a; font-size: 10px; font-weight: 850;
            letter-spacing: 1.25px; text-transform: uppercase;
            margin-bottom: 12px;
        }
        .voice-result-copy { color: #e9f2eb; font-size: 14px; line-height: 1.8; overflow-wrap: anywhere; }
        .voice-divider { border: 0; border-top: 1px solid #263b2b; margin: 22px 0; }
        .voice-footnote { color: #84988a; font-size: 10px; line-height: 1.7; }
        .voice-empty {
            text-align: center;
            border: 1px dashed #365640;
            border-radius: 16px;
            background: rgba(17, 29, 20, .72);
            padding: 17px;
            color: #a8b9ac;
            font-size: 12px;
        }

        /* Voice recorder component buttons */
        .main [data-testid="stAudioInput"],
        .main [data-testid="stAudio"] {
            border-radius: 14px !important;
        }
        .main .stButton > button,
        .main .stDownloadButton > button {
            min-height: 43px !important;
            border-radius: 11px !important;
            border: 1px solid #35533d !important;
            background: #142219 !important;
            color: #edf7ef !important;
            font-weight: 700 !important;
            transition: transform .16s ease, border-color .16s ease, background .16s ease !important;
        }
        .main .stButton > button:hover,
        .main .stDownloadButton > button:hover {
            background: #1b3423 !important;
            border-color: #4ca568 !important;
            color: #ffffff !important;
            transform: translateY(-1px);
        }
        .main .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2eaf62, #168247) !important;
            border-color: #38c370 !important;
            color: #ffffff !important;
            box-shadow: 0 6px 18px rgba(30,151,76,.17) !important;
        }
        .main .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #3acb75, #1d9952) !important;
        }

        /* Select boxes and their labels */
        .main [data-testid="stWidgetLabel"] p,
        .main label { color: #dce9df !important; font-weight: 650 !important; }
        .main [data-baseweb="select"] > div {
            background: #111b14 !important;
            border: 1px solid #35523d !important;
            border-radius: 11px !important;
            min-height: 43px;
        }
        .main [data-baseweb="select"] input,
        .main [data-baseweb="select"] div,
        .main [data-baseweb="select"] span { color: #edf6ef !important; }
        div[data-baseweb="popover"] { z-index: 999999 !important; }
        div[data-baseweb="popover"] [role="option"] { color: #183b26 !important; }

        /* Audio playback: rounded frame; native browser controls stay functional */
        .main audio { width: 100%; border-radius: 12px; }
        .main [data-testid="stAudio"] { margin-top: 6px; margin-bottom: 8px; }

        /* Status messages remain legible on dark surfaces */
        .main [data-testid="stAlert"] {
            border-radius: 12px !important;
            background: #111d14 !important;
            color: #e9f4eb !important;
            border-color: #355b3e !important;
        }
        @media (max-width: 700px) {
            .main .block-container { padding: 1rem .8rem 2rem !important; }
            .voice-hero { padding: 22px 18px; border-radius: 17px; }
            .voice-page-title { font-size: 29px; }
            .voice-card { min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_feature_cards() -> None:
    cols = st.columns(3, gap="medium")
    items = [
        ("↗", "Speak naturally", "Record a voice message in your chosen input language."),
        ("文", "Understand clearly", "Review the recognized words and their translation."),
        ("♫", "Listen back", "Generate and play translated speech when supported."),
    ]
    for col, (icon, title, description) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="voice-card">
                    <div class="voice-card-icon">{icon}</div>
                    <div class="voice-card-title">{title}</div>
                    <div class="voice-card-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_result_card(label: str, icon: str, text: str) -> None:
    # Escape transcript text before placing it inside HTML.
    import html

    st.markdown(
        f"""
        <div class="voice-result-card">
            <div class="voice-result-label"><span>{icon}</span>{label}</div>
            <div class="voice-result-copy">{html.escape(text) if text else "No text returned."}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _process_recording(audio_bytes: bytes, input_language: str, response_language: str, response_label: str) -> None:
    """Run the existing audio translation endpoint and persist its result."""
    audio_path = None
    st.session_state["voice_processing"] = True
    try:
        audio_dir = PROJECT_ROOT / "data" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".wav",
            dir=str(audio_dir),
            delete=False,
        ) as temp_audio:
            temp_audio.write(audio_bytes)
            audio_path = temp_audio.name

        progress = st.progress(8, text="Preparing your recording…")
        try:
            progress.progress(24, text="Sending audio for speech recognition…")
            response = APIClient.translate_audio(
                audio_path=audio_path,
                input_language=input_language,
                response_language=response_language,
            )
            progress.progress(100, text="Finishing translation…")
        finally:
            # Remove the temporary progress widget after the operation.
            progress.empty()

        if not isinstance(response, dict):
            st.error("The speech service returned an unexpected response.")
            st.session_state["voice_last_status"] = "error"
            return

        if not response.get("success"):
            st.error(response.get("error", "Voice translation failed."))
            st.session_state["voice_last_status"] = "error"
            return

        transcription = str(response.get("transcription") or "").strip()
        translated_text = str(response.get("translated_text") or "").strip()

        if not transcription:
            st.warning("No speech could be recognized. Try recording a little closer to the microphone.")
            st.session_state["voice_last_status"] = "empty"
            return

        st.session_state["voice_transcription"] = transcription
        st.session_state["voice_translated_text"] = translated_text
        # Keep the original widget key separate from the processed result.
        st.session_state["voice_processed_response_language"] = response_language
        st.session_state["voice_response_label"] = response_label
        st.session_state["voice_processed_input_label"] = st.session_state.get(
            "voice_input_language", "English"
        )
        st.session_state["voice_last_status"] = "success"
        st.success("Voice translated successfully. Review the result below.")
    except Exception as exc:
        st.session_state["voice_last_status"] = "error"
        st.error(f"Voice translation failed: {exc}")
    finally:
        st.session_state["voice_processing"] = False
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


def _render_speech_output(translated_text: str, saved_language: str, saved_label: str) -> None:
    """Preserve the current language-specific TTS behavior."""
    if not translated_text or not saved_language:
        st.info("Audio generation will be available when a translated response is returned.")
        return

    if saved_language == "manipuri":
        st.markdown('<div class="voice-kicker">Manipuri speech settings</div>', unsafe_allow_html=True)
        script_options = {
            "Bengali Script": "bengali",
            "Meitei Mayek": "meitei_mayek",
        }
        selected_script = st.selectbox(
            "Choose the output script",
            list(script_options.keys()),
            key="manipuri_tts_script",
        )

        if st.button(
            "♫  Generate Manipuri speech",
            type="primary",
            use_container_width=True,
            key="generate_manipuri_tts",
        ):
            tts_text = translated_text
            tts_script = script_options[selected_script]
            try:
                with st.spinner("Generating Manipuri speech. This may take several minutes on CPU…"):
                    if tts_script == "meitei_mayek":
                        tts_text = convert_bengali_to_meitei(translated_text)
                        if not tts_text:
                            st.error("Could not convert the translated text to Meitei Mayek.")
                            return

                    audio_bytes = APIClient.manipuri_text_to_speech(
                        text=tts_text,
                        script=tts_script,
                        speaker="female",
                    )

                if not audio_bytes:
                    st.error("Manipuri speech generation failed. Check the backend logs.")
                else:
                    st.session_state["voice_generated_audio"] = audio_bytes
                    st.session_state["voice_generated_audio_name"] = f"manipuri_{tts_script}.wav"
                    st.session_state["voice_generated_audio_mime"] = "audio/wav"
                    st.success("Manipuri speech is ready.")
            except Exception as exc:
                st.error(f"Manipuri speech generation failed: {exc}")

    else:
        if st.button(
            "♫  Generate translated speech",
            type="primary",
            use_container_width=True,
            key="generate_standard_voice",
        ):
            try:
                with st.spinner(f"Generating audio in {saved_label}…"):
                    audio_response = APIClient.text_to_speech(translated_text, saved_language)

                # The API client should return MP3 bytes. Avoid treating JSON error
                # bodies or arbitrary truthy values as playable audio.
                if isinstance(audio_response, (bytes, bytearray)) and len(audio_response) > 100:
                    audio_bytes_candidate = bytes(audio_response)
                    looks_like_mp3 = (
                        audio_bytes_candidate.startswith(b"ID3")
                        or (
                            len(audio_bytes_candidate) > 1
                            and audio_bytes_candidate[0] == 0xFF
                            and (audio_bytes_candidate[1] & 0xE0) == 0xE0
                        )
                    )
                    if looks_like_mp3:
                        st.session_state["voice_generated_audio"] = audio_bytes_candidate
                        st.session_state["voice_generated_audio_name"] = f"{saved_language}_speech.mp3"
                        st.session_state["voice_generated_audio_mime"] = "audio/mpeg"
                        st.success(f"Audio generated in {saved_label}.")
                    else:
                        st.error(
                            "The TTS endpoint did not return valid MP3 audio. "
                            "Check the backend log for the provider error."
                        )
                elif isinstance(audio_response, dict):
                    st.error(audio_response.get("error", "TTS generation failed."))
                else:
                    st.error(
                        f"Audio generation failed for {saved_label}. "
                        "Check backend connectivity and the TTS provider."
                    )
            except Exception as exc:
                st.error(f"Audio generation failed: {exc}")

    audio_bytes = st.session_state.get("voice_generated_audio")
    if audio_bytes:
        st.markdown('<div class="voice-kicker">Audio player</div>', unsafe_allow_html=True)
        st.audio(
            audio_bytes,
            format=st.session_state.get("voice_generated_audio_mime", "audio/mpeg"),
        )
        st.download_button(
            "⬇  Download audio",
            data=audio_bytes,
            file_name=st.session_state.get("voice_generated_audio_name", "tribal_ai_voice.mp3"),
            mime=st.session_state.get("voice_generated_audio_mime", "audio/mpeg"),
            use_container_width=True,
            key="download_generated_voice_audio",
        )


def show_voice_page():
    """Render the AI Voice Studio while preserving existing voice services."""
    _voice_styles()

    input_label = st.session_state.get("voice_input_language", "English")
    response_label = st.session_state.get("voice_response_language", "Hindi")
    if input_label not in SUPPORTED_LANGUAGES:
        input_label = "English"
    if response_label not in SUPPORTED_LANGUAGES:
        response_label = "Hindi"

    st.markdown(
        f"""
        <section class="voice-hero">
            <div class="voice-eyebrow">Tribal AI · Multilingual voice studio</div>
            <div class="voice-hero-mark">🌿</div>
            <h1 class="voice-page-title">Your voice. <span>Your language.</span></h1>
            <p class="voice-page-subtitle">
                Speak naturally, translate across supported languages, and listen to your
                message. A simple voice workspace designed to make every conversation feel easier.
            </p>
            <div style="margin-top:18px;">
                <span class="voice-status"><span class="voice-status-dot"></span> Voice assistant ready</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    _render_feature_cards()

    st.markdown('<hr class="voice-divider">', unsafe_allow_html=True)
    st.markdown('<div class="voice-kicker">01 · Set up your conversation</div>', unsafe_allow_html=True)
    st.markdown('<div class="voice-section-title">Choose your languages</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="voice-section-subtitle">Select the language you will speak and the language you want Tribal AI to respond in.</div>',
        unsafe_allow_html=True,
    )

    language_col, response_col = st.columns(2, gap="medium")
    with language_col:
        input_label = st.selectbox(
            "Speak in",
            list(SUPPORTED_LANGUAGES.keys()),
            key="voice_input_language",
        )
    with response_col:
        response_label = st.selectbox(
            "Translate to",
            list(SUPPORTED_LANGUAGES.keys()),
            index=list(SUPPORTED_LANGUAGES.keys()).index("Hindi"),
            key="voice_response_language",
        )

    input_language = SUPPORTED_LANGUAGES[input_label]
    response_language = SUPPORTED_LANGUAGES[response_label]

    st.markdown('<hr class="voice-divider">', unsafe_allow_html=True)
    st.markdown('<div class="voice-kicker">02 · Voice capture</div>', unsafe_allow_html=True)
    st.markdown('<div class="voice-section-title">Speak when you’re ready</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="voice-section-subtitle">Allow microphone access, start recording, and stop when you have finished speaking. You can listen to the recording before translating it.</div>',
        unsafe_allow_html=True,
    )

    recorder_col, guide_col = st.columns([1.6, 1], gap="large")
    with recorder_col:
        audio = mic_recorder(
            start_prompt="🎙  Start recording",
            stop_prompt="⏹  Stop recording",
            just_once=False,
            use_container_width=True,
            format="wav",
            key="voice_component_recorder",
        )
    with guide_col:
        st.markdown(
            """
            <div class="voice-card">
                <div class="voice-card-icon">●</div>
                <div class="voice-card-title">A quick recording tip</div>
                <div class="voice-card-text">
                    Speak clearly and keep your device close enough to capture your voice.
                    Reduce background noise for more reliable transcription.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    audio_bytes = audio.get("bytes") if isinstance(audio, dict) else None
    if audio_bytes:
        st.markdown('<div class="voice-kicker">Recording preview</div>', unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/wav")
        st.caption(f"Ready to process · {input_label} → {response_label}")

        if st.button(
            "🌿  Translate my voice",
            type="primary",
            use_container_width=True,
            key="component_process_voice",
        ):
            _process_recording(
                audio_bytes=audio_bytes,
                input_language=input_language,
                response_language=response_language,
                response_label=response_label,
            )
    else:
        st.markdown(
            '<div class="voice-empty">🎙 &nbsp; Your recording preview will appear here after you stop recording.</div>',
            unsafe_allow_html=True,
        )

    transcription = st.session_state.get("voice_transcription", "")
    translated_text = st.session_state.get("voice_translated_text", "")
    saved_language = st.session_state.get("voice_processed_response_language", "")
    saved_label = st.session_state.get("voice_response_label", "")

    if transcription:
        st.markdown('<hr class="voice-divider">', unsafe_allow_html=True)
        st.markdown('<div class="voice-kicker">03 · Your results</div>', unsafe_allow_html=True)
        st.markdown('<div class="voice-section-title">Your voice, understood</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="voice-section-subtitle">Review the recognized speech, compare the translation, and generate audio when the selected language is supported.</div>',
            unsafe_allow_html=True,
        )

        result_col, translated_col = st.columns(2, gap="medium")
        with result_col:
            _render_result_card("Original transcription", "✎", transcription)
        with translated_col:
            _render_result_card(f"Translated response · {saved_label or 'Target language'}", "文", translated_text)

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        _render_speech_output(translated_text, saved_language, saved_label)

    st.markdown('<hr class="voice-divider">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="voice-footnote">
            🌿 TRIBAL AI &nbsp;·&nbsp; PRESERVING KNOWLEDGE, CONNECTING CULTURES<br>
            Speech recognition, translation, and audio generation depend on the selected language
            and the capabilities configured in your backend.
        </div>
        """,
        unsafe_allow_html=True,
    )
