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

def show_settings():
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
    st.session_state.theme = selected_theme
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