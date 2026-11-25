import html
import streamlit as st


def html_block(content):
    """Render a compact HTML block inside Streamlit."""
    st.markdown(content, unsafe_allow_html=True)


def _inject_settings_styles(theme):
    """Apply theme-aware styling without forcing the whole app into Light mode."""
    is_dark = theme == "Dark"
    palette = {
        "page": "#101a15" if is_dark else "#f6faf8",
        "surface": "#17251d" if is_dark else "#ffffff",
        "surface_alt": "#1d3025" if is_dark else "#effaf4",
        "border": "#2d4938" if is_dark else "#dcece5",
        "heading": "#e2f3e8" if is_dark else "#173b2d",
        "text": "#c0d4c7" if is_dark else "#294b3a",
        "muted": "#9bb5a4" if is_dark else "#718579",
        "accent": "#65c995" if is_dark else "#176b4a",
        "icon_bg": "#244332" if is_dark else "#dff4e8",
        "shadow": "rgba(0,0,0,.18)" if is_dark else "rgba(31,87,62,.06)",
        "control": "#203329" if is_dark else "#ffffff",
    }

    css = """
    <style>
    :root { color-scheme: __SCHEME__; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    .main, .main .block-container {
        background: __PAGE__ !important;
        color: __TEXT__ !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stAppHeader"], [data-testid="stDecoration"] {
        background: __PAGE__ !important;
        color: __TEXT__ !important;
        border-bottom: 1px solid __BORDER__ !important;
    }
    .main .block-container { padding-top: 2rem; }
    .settings-page-header {
        display:flex; align-items:center; gap:16px; padding:24px 26px;
        margin:4px 0 28px; border:1px solid __BORDER__; border-radius:22px;
        background:linear-gradient(135deg, __SURFACE__ 0%, __ALT__ 100%);
        box-shadow:0 8px 24px __SHADOW__;
    }
    .settings-header-icon {
        display:flex; align-items:center; justify-content:center; width:54px;
        height:54px; border-radius:16px; background:__ICON_BG__;
        color:__ACCENT__; font-size:26px; flex-shrink:0;
    }
    .settings-header-title { color:__HEADING__; font-size:28px; font-weight:750; letter-spacing:-.5px; }
    .settings-header-subtitle { color:__MUTED__; font-size:14px; margin-top:4px; }
    .settings-section { margin:24px 0 12px; }
    .settings-section-title { color:__HEADING__; font-size:18px; font-weight:700; }
    .settings-section-description { color:__MUTED__; font-size:13px; margin-top:4px; }
    .settings-info-card,.settings-model-card,.settings-about-card {
        background:__SURFACE__; border:1px solid __BORDER__; border-radius:18px;
        padding:18px 20px; box-shadow:0 5px 18px __SHADOW__;
    }
    .settings-info-card,.settings-about-card { display:flex; align-items:center; gap:14px; }
    .settings-info-icon,.settings-about-icon {
        display:flex; align-items:center; justify-content:center; width:44px;
        height:44px; border-radius:14px; background:__ICON_BG__;
        font-size:22px; flex-shrink:0;
    }
    .settings-info-label,.settings-model-label { color:__MUTED__; font-size:12px; font-weight:600; }
    .settings-info-value,.settings-model-value { color:__HEADING__; font-size:18px; font-weight:700; margin-top:4px; }
    .settings-about-title { color:__HEADING__; font-size:17px; font-weight:700; }
    .settings-about-text { color:__MUTED__; font-size:13px; line-height:1.6; margin-top:5px; }
    div[data-testid="stCheckbox"] {
        background:__SURFACE__; border:1px solid __BORDER__;
        border-radius:14px; padding:12px 16px;
    }
    div[data-testid="stCheckbox"] label,
    div[data-testid="stSelectbox"] label { color:__TEXT__ !important; font-weight:600; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background:__CONTROL__; border-color:__BORDER__; border-radius:12px;
    }
    div[data-testid="stSelectbox"] * { color:__TEXT__; }
    @media (max-width: 640px) {
        .settings-page-header { padding:18px; gap:12px; }
        .settings-header-title { font-size:24px; }
        .settings-info-card,.settings-about-card { padding:15px; }
    }
    </style>
    """
    replacements = {
        "__SCHEME__": "dark" if is_dark else "light",
        "__PAGE__": palette["page"], "__SURFACE__": palette["surface"],
        "__ALT__": palette["surface_alt"], "__BORDER__": palette["border"],
        "__HEADING__": palette["heading"], "__TEXT__": palette["text"],
        "__MUTED__": palette["muted"], "__ACCENT__": palette["accent"],
        "__ICON_BG__": palette["icon_bg"], "__SHADOW__": palette["shadow"],
        "__CONTROL__": palette["control"],
    }
    for token, value in replacements.items():
        css = css.replace(token, value)
    st.markdown(css, unsafe_allow_html=True)


def show_settings():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    if "voice_output" not in st.session_state:
        st.session_state.voice_output = True

    # Keep the existing theme setting as the single source of truth.
    current_theme = st.session_state.get("theme", "Light")
    _inject_settings_styles(current_theme)

    html_block("""
        <div class="settings-page-header">
            <div class="settings-header-icon">⚙</div>
            <div class="settings-header-content">
                <div class="settings-header-title">Settings</div>
                <div class="settings-header-subtitle">Customize your Tribal AI experience.</div>
            </div>
        </div>
    """)

    language = st.session_state.get("language", "english")
    language_name = html.escape(language.replace("_", " ").title())
    html_block(f"""
        <div class="settings-section">
            <div class="settings-section-title">🌐 Language</div>
            <div class="settings-section-description">Your current conversation language.</div>
        </div>
        <div class="settings-info-card">
            <div class="settings-info-icon">🌿</div>
            <div class="settings-info-content">
                <div class="settings-info-label">Current Language</div>
                <div class="settings-info-value">{language_name}</div>
            </div>
        </div>
    """)

    html_block("""
        <div class="settings-section">
            <div class="settings-section-title">🔊 Voice</div>
            <div class="settings-section-description">Control how Tribal AI handles voice responses.</div>
        </div>
    """)
    st.session_state.voice_output = st.checkbox(
        "Enable Voice Response",
        value=st.session_state.voice_output,
        key="settings_voice_output",
    )

    html_block("""
        <div class="settings-section">
            <div class="settings-section-title">🎨 Appearance</div>
            <div class="settings-section-description">Choose your preferred interface theme.</div>
        </div>
    """)

    # Use the current value to initialize the widget, then rerun so all
    # theme-aware components receive the updated session-state value.
    selected_theme = st.selectbox(
        "Theme",
        ["Light", "Dark"],
        index=0 if current_theme == "Light" else 1,
        key="settings_theme",
    )
    if selected_theme != current_theme:
        st.session_state.theme = selected_theme
        st.rerun()

    html_block("""
        <div class="settings-section">
            <div class="settings-section-title">🤖 AI Model</div>
            <div class="settings-section-description">Current AI configuration used by Tribal AI.</div>
        </div>
    """)
    col1, col2 = st.columns(2)
    with col1:
        html_block("""
            <div class="settings-model-card">
                <div class="settings-model-label">AI Model</div>
                <div class="settings-model-value">Llama 3</div>
            </div>
        """)
    with col2:
        html_block("""
            <div class="settings-model-card">
                <div class="settings-model-label">Temperature</div>
                <div class="settings-model-value">0.3</div>
            </div>
        """)

    html_block("""
        <div class="settings-section">
            <div class="settings-section-title">ℹ About Tribal AI</div>
            <div class="settings-section-description">
                A multilingual AI assistant designed to help preserve, access, and explore tribal knowledge.
            </div>
        </div>
        <div class="settings-about-card">
            <div class="settings-about-icon">🌿</div>
            <div class="settings-about-content">
                <div class="settings-about-title">Tribal AI Chatbot</div>
                <div class="settings-about-text">
                    Multilingual conversational AI with knowledge retrieval, voice interaction,
                    and document-based knowledge support.
                </div>
            </div>
        </div>
    """)
