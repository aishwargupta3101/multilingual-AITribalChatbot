import streamlit as st


def html_block(content):
    """
    Render custom HTML safely as a single-line block.
    """
    content = " ".join(
        line.strip()
        for line in content.splitlines()
        if line.strip()
    )

    st.markdown(
        content,
        unsafe_allow_html=True
    )


def _inject_settings_styles():
    st.markdown("""
    <style>
    .stApp { background: #f6faf8; }
    .settings-page-header { display:flex; align-items:center; gap:16px; padding:24px 26px; margin:4px 0 28px; border:1px solid #dcece5; border-radius:22px; background:linear-gradient(135deg,#ffffff 0%,#effaf4 100%); box-shadow:0 8px 24px rgba(31,87,62,.06); }
    .settings-header-icon { display:flex; align-items:center; justify-content:center; width:54px; height:54px; border-radius:16px; background:#dff4e8; color:#176b4a; font-size:26px; flex-shrink:0; }
    .settings-header-title { color:#173b2d; font-size:28px; font-weight:750; letter-spacing:-.5px; }
    .settings-header-subtitle { color:#648074; font-size:14px; margin-top:4px; }
    .settings-section { margin:24px 0 12px; }
    .settings-section-title { color:#234b39; font-size:18px; font-weight:700; }
    .settings-section-description { color:#718579; font-size:13px; margin-top:4px; }
    .settings-info-card,.settings-model-card,.settings-about-card { background:#fff; border:1px solid #deebe4; border-radius:18px; padding:18px 20px; box-shadow:0 5px 18px rgba(31,87,62,.045); }
    .settings-info-card,.settings-about-card { display:flex; align-items:center; gap:14px; }
    .settings-info-icon,.settings-about-icon { display:flex; align-items:center; justify-content:center; width:44px; height:44px; border-radius:14px; background:#e7f7ee; font-size:22px; flex-shrink:0; }
    .settings-info-label,.settings-model-label { color:#74877b; font-size:12px; font-weight:600; }
    .settings-info-value,.settings-model-value { color:#1d4432; font-size:18px; font-weight:700; margin-top:4px; }
    .settings-about-title { color:#1d4432; font-size:17px; font-weight:700; }
    .settings-about-text { color:#718579; font-size:13px; line-height:1.6; margin-top:5px; }
    div[data-testid="stCheckbox"] label, div[data-testid="stSelectbox"] label { color:#315443 !important; font-weight:600; }
    div[data-testid="stCheckbox"] { background:#fff; border:1px solid #deebe4; border-radius:14px; padding:12px 16px; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div { background:#fff; border-color:#d7e7de; border-radius:12px; }

    /* Force the Settings page canvas to match the light Document workspace. */
    html, body, [data-testid="stApp"], .stApp,
    [data-testid="stAppViewContainer"], [data-testid="stMain"],
    .main, .main .block-container {
        background: #f6faf8 !important;
        color: #173b2d !important;
        color-scheme: light !important;
    }
    /* Streamlit's app header/toolbar are separate from the page canvas. */
    [data-testid="stHeader"],
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stAppHeader"],
    .stAppHeader,
    [data-testid="stDecoration"] {
        background: #f6faf8 !important;
        background-color: #f6faf8 !important;
        color: #173b2d !important;
        border-bottom: 1px solid #dcece5 !important;
    }
    [data-testid="stHeader"] *,
    [data-testid="stToolbar"] *,
    [data-testid="stAppHeader"] * {
        color: #173b2d !important;
    }
    .main .block-container { background: #f6faf8 !important; }
    .main p, .main label, .main [data-testid="stMarkdownContainer"],
    .main [data-testid="stCaptionContainer"], .main h1, .main h2,
    .main h3, .main h4, .main h5, .main h6 {
        color: #294b3a;
    }
    div[data-testid="stCheckbox"] label,
    div[data-testid="stSelectbox"] label {
        color: #315443 !important;
    }
</style>
    """, unsafe_allow_html=True)


def show_settings():
    _inject_settings_styles()
    html_block(
        """
        <div class="settings-page-header">

            <div class="settings-header-icon">
                ⚙
            </div>

            <div class="settings-header-content">

                <div class="settings-header-title">
                    Settings
                </div>

                <div class="settings-header-subtitle">
                    Customize your Tribal AI experience.
                </div>

            </div>

        </div>
        """
    )
    language = st.session_state.get(
        "language",
        "english"
    )
    language_name = language.replace(
        "_",
        " "
    ).title()
    html_block(
        f"""
        <div class="settings-section">

            <div class="settings-section-title">
                🌐 Language
            </div>

            <div class="settings-section-description">
                Your current conversation language.
            </div>

        </div>
        """
    )
    html_block(
        f"""
        <div class="settings-info-card">

            <div class="settings-info-icon">
                🌿
            </div>

            <div class="settings-info-content">

                <div class="settings-info-label">
                    Current Language
                </div>

                <div class="settings-info-value">
                    {language_name}
                </div>

            </div>

        </div>
        """
    )
    html_block(
        """
        <div class="settings-section">

            <div class="settings-section-title">
                🔊 Voice
            </div>

            <div class="settings-section-description">
                Control how Tribal AI handles voice responses.
            </div>

        </div>
        """
    )
    if "voice_output" not in st.session_state:
        st.session_state.voice_output = False
    st.session_state.voice_output = st.checkbox(
        "Enable Voice Response",
        value=st.session_state.voice_output,
        key="settings_voice_output"
    )
    html_block(
        """
        <div class="settings-section">

            <div class="settings-section-title">
                🎨 Appearance
            </div>

            <div class="settings-section-description">
                Choose your preferred interface theme.
            </div>

        </div>
        """
    )
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    previous_theme = st.session_state.theme

    selected_theme = st.selectbox(
        "Theme",
        [
            "Light",
            "Dark"
        ],
        index=(
            0
            if st.session_state.theme == "Light"
            else 1
        ),
        key="settings_theme"
    )

    if selected_theme != previous_theme:
        st.session_state.theme = selected_theme
        st.rerun()
    html_block(
        """
        <div class="settings-section">

            <div class="settings-section-title">
                🤖 AI Model
            </div>

            <div class="settings-section-description">
                Current AI configuration used by Tribal AI.
            </div>

        </div>
        """
    )
    col1, col2 = st.columns(2)
    with col1:
        html_block(
            """
            <div class="settings-model-card">

                <div class="settings-model-label">
                    AI Model
                </div>

                <div class="settings-model-value">
                    Llama 3
                </div>

            </div>
            """
        )
    with col2:
        html_block(
            """
            <div class="settings-model-card">

                <div class="settings-model-label">
                    Temperature
                </div>

                <div class="settings-model-value">
                    0.3
                </div>

            </div>
            """
        )
    html_block(
        """
        <div class="settings-section">
            <div class="settings-section-title">
                ℹ About Tribal AI
            </div>
            <div class="settings-section-description">
                A multilingual AI assistant designed to help
                preserve, access, and explore tribal knowledge.
            </div>

        </div>
        """
    )
    html_block(
        """
        <div class="settings-about-card">

            <div class="settings-about-icon">
                🌿
            </div>

            <div class="settings-about-content">

                <div class="settings-about-title">
                    Tribal AI Chatbot
                </div>

                <div class="settings-about-text">
                    Multilingual conversational AI with
                    knowledge retrieval, voice interaction,
                    and document-based knowledge support.
                </div>

            </div>

        </div>
        """
    )