import html
import streamlit as st

from components.chat_box import show_chat_box


def html_block(content: str) -> None:
    """Render a trusted HTML fragment with Streamlit."""
    st.markdown(content, unsafe_allow_html=True)


def _render_chat_styles() -> None:
    """Style the chat view to match the supplied modern chat-app reference."""
    st.markdown(
        """
        <style>
        /* Scoped chat-page styling. Other pages and backend logic are untouched. */
        /* Match the light mint workspace used by the Document page. */
        .stApp:has(.ta-chat-page),
        [data-testid="stAppViewContainer"]:has(.ta-chat-page),
        .main:has(.ta-chat-page) {
            background: #EEF6F0 !important;
        }
        /* Lighten Streamlit's fixed top header and toolbar as well as the page canvas. */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stHeader"] > div,
        [data-testid="stToolbar"] > div {
            background: #EEF6F0 !important;
            color: #18352A !important;
        }
        [data-testid="stHeader"] button,
        [data-testid="stToolbar"] button,
        [data-testid="stHeader"] svg,
        [data-testid="stToolbar"] svg {
            color: #355746 !important;
            fill: #355746 !important;
        }
        header[data-testid="stHeader"] { background: #EEF6F0 !important; }
        .main:has(.ta-chat-page) .block-container {
            max-width: 1280px !important;
            padding: 1.15rem clamp(.8rem, 2.6vw, 2rem) 1.5rem !important;
            background: transparent !important;
        }
        .ta-chat-page {
            --chat-bg: #F7FBF8;
            --chat-panel: #FFFFFF;
            --chat-panel-2: #F0F7F2;
            --chat-border: #DCE9DF;
            --chat-green: #23834B;
            --chat-text: #18352A;
            --chat-muted: #65796C;
            color: var(--chat-text);
            min-height: 100px;
            background: #EEF6F0;
        }
        .ta-chat-topbar {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:14px;
            padding: 9px 2px 16px;
            border-bottom:1px solid #DCE9DF;
            margin-bottom:20px;
        }
        .ta-chat-brand { display:flex; align-items:center; gap:12px; min-width:0; }
        .ta-chat-logo {
            display:flex; align-items:center; justify-content:center;
            width:43px; height:43px; flex:0 0 43px;
            border:1px solid #2c5a3a; border-radius:13px;
            background:linear-gradient(145deg,#183d26,#0d2114);
            font-size:21px;
        }
        .ta-chat-brand-title { color:#18352A; font-size:16px; font-weight:800; line-height:1.35; }
        .ta-chat-brand-subtitle { color:#65796C; font-size:11px; margin-top:3px; }
        .ta-chat-top-meta { display:flex; align-items:center; justify-content:flex-end; flex-wrap:wrap; gap:8px; }
        .ta-chat-pill {
            display:inline-flex; align-items:center; gap:7px;
            padding:7px 10px; border:1px solid #CFE3D4; border-radius:999px;
            background:#F4FAF5; color:#355746; font-size:11px;
        }
        .ta-chat-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#23834B; box-shadow:0 0 10px #45d67566; }
        .ta-chat-welcome {
            max-width:760px; margin: clamp(22px,5vh,58px) auto 24px;
            padding: clamp(22px,4vw,34px);
            text-align:center;
            border:1px solid #D7E8DB; border-radius:20px;
            background:
                radial-gradient(ellipse at 50% 0%, rgba(37,132,65,.22), transparent 62%),
                linear-gradient(145deg,#F5FAF6,#FFFFFF);
            box-shadow:0 18px 50px #00000026, inset 0 1px #ffffff06;
        }
        .ta-chat-welcome-icon {
            width:48px; height:48px; display:flex; align-items:center; justify-content:center;
            margin:0 auto 14px; border-radius:15px;
            border:1px solid #B9DCC3; background:#E8F5EB; font-size:23px;
        }
        .ta-chat-welcome-kicker { color:#23834B; font-size:10px; font-weight:800; letter-spacing:.17em; }
        .ta-chat-welcome-title {
            color:#18352A; font-size:clamp(25px,3.4vw,36px); line-height:1.15;
            letter-spacing:-.035em; font-weight:800; margin:12px 0 10px;
        }
        .ta-chat-welcome-title span { color:#23834B; }
        .ta-chat-welcome-copy { max-width:570px; margin:0 auto; color:#617568; font-size:13px; line-height:1.8; }
        .ta-chat-topic-grid {
            display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
            gap:12px; max-width:900px; margin:0 auto 24px;
        }
        .ta-chat-topic {
            min-height:125px; padding:16px; border:1px solid #DCE9DF; border-radius:14px;
            background:linear-gradient(145deg,#FFFFFF,#F4FAF5);
        }
        .ta-chat-topic-icon {
            width:32px; height:32px; display:flex; align-items:center; justify-content:center;
            margin-bottom:11px; border:1px solid #B9DCC3; border-radius:10px;
            background:#E8F5EB; color:#23834B; font-size:16px;
        }
        .ta-chat-topic-title { color:#18352A; font-size:12px; font-weight:800; margin-bottom:5px; }
        .ta-chat-topic-copy { color:#aab9ae; font-size:11px; line-height:1.65; }
        .ta-chat-section-label {
            color:#557763; font-size:10px; font-weight:800; letter-spacing:.15em;
            margin:0 0 10px 2px;
        }

        /* Streamlit chat messages: readable text on light cards */
        [data-testid="stChatMessage"] {
            border:1px solid #DCE9DF !important;
            border-radius:15px !important;
            background:#FFFFFF !important;
            padding:14px 16px !important;
            margin:10px 0 !important;
            box-shadow:0 5px 18px #00000012;
        }
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
            color:#18352A !important;
            line-height:1.75 !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background:#E8F5EB !important;
            border-color:#B9DCC3 !important;
        }
        [data-testid="stChatMessage"] code {
            color:#1D5C36 !important; background:#F5FAF6 !important;
            border:1px solid #DCE9DF !important; border-radius:6px !important;
        }
        [data-testid="stChatInput"] {
            border:1px solid #CFE3D4 !important;
            border-radius:16px !important;
            background:#FFFFFF !important;
            box-shadow:0 10px 32px #00000022 !important;
        }
        [data-testid="stChatInput"] textarea {
            background:transparent !important; color:#18352A !important;
            caret-color:#23834B !important; border:0 !important;
        }
        [data-testid="stChatInput"] textarea::placeholder { color:#718477 !important; opacity:1 !important; }
        [data-testid="stChatInput"] button {
            color:#ffffff !important; background:#23834B !important;
            border:1px solid #23834B !important; border-radius:10px !important;
        }
        [data-testid="stChatInput"] button:hover { background:#1B6B3B !important; }

        /* Generic composer controls used by custom chat_box implementations */
        .main textarea, .main input,
        .main [data-baseweb="input"] input,
        .main [data-baseweb="textarea"] textarea {
            color:#18352A !important; background:#FFFFFF !important;
            border-color:#CFE3D4 !important; caret-color:#23834B !important;
        }
        .main textarea::placeholder, .main input::placeholder { color:#718477 !important; opacity:1 !important; }

        .ta-chat-footer {
            display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
            margin-top:20px; padding:13px 2px 0; border-top:1px solid #DCE9DF;
            color:#65796C; font-size:10px;
        }
        @media(max-width:760px) {
            .ta-chat-topbar { align-items:flex-start; }
            .ta-chat-top-meta { max-width:130px; }
            .ta-chat-welcome { margin-top:22px; padding:22px 15px; border-radius:16px; }
            .ta-chat-topic-grid { grid-template-columns:1fr; gap:9px; }
            .ta-chat-topic { min-height:auto; padding:13px; }
            .ta-chat-footer { justify-content:center; text-align:center; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_chat_page() -> None:
    """Render the redesigned chat interface and retain the existing chat engine."""
    _render_chat_styles()

    language = st.session_state.get("language", "english")
    language_name = html.escape(str(language).replace("_", " ").title())
    messages = st.session_state.get("messages", [])

    html_block(
        f"""
        <div class="ta-chat-page">
          <div class="ta-chat-topbar">
            <div class="ta-chat-brand">
              <div class="ta-chat-logo">🌿</div>
              <div>
                <div class="ta-chat-brand-title">Tribal AI</div>
                <div class="ta-chat-brand-subtitle">Your multilingual knowledge assistant</div>
              </div>
            </div>
            <div class="ta-chat-top-meta">
              <span class="ta-chat-pill">🌐 {language_name}</span>
              <span class="ta-chat-pill"><span class="ta-chat-dot"></span> Online</span>
            </div>
          </div>
        """
    )

    if not messages:
        html_block(
            """
            <section class="ta-chat-welcome">
              <div class="ta-chat-welcome-icon">🌿</div>
              <div class="ta-chat-welcome-kicker">MULTILINGUAL LEARNING ASSISTANT</div>
              <div class="ta-chat-welcome-title">How can I help you <span>today?</span></div>
              <p class="ta-chat-welcome-copy">
                Ask about tribal knowledge, culture, traditions, languages, or documents.
                Start a conversation in the language that feels like home.
              </p>
            </section>
            <div class="ta-chat-section-label">IDEAS TO GET YOU STARTED</div>
            <div class="ta-chat-topic-grid">
              <div class="ta-chat-topic">
                <div class="ta-chat-topic-icon">⌘</div>
                <div class="ta-chat-topic-title">Explore knowledge</div>
                <div class="ta-chat-topic-copy">Discover community stories, culture, and traditions.</div>
              </div>
              <div class="ta-chat-topic">
                <div class="ta-chat-topic-icon">✳</div>
                <div class="ta-chat-topic-title">Ask a question</div>
                <div class="ta-chat-topic-copy">Get helpful answers using the Tribal AI knowledge system.</div>
              </div>
              <div class="ta-chat-topic">
                <div class="ta-chat-topic-icon">◉</div>
                <div class="ta-chat-topic-title">Use your voice</div>
                <div class="ta-chat-topic-copy">Speak naturally and explore multilingual voice assistance.</div>
              </div>
            </div>
            """
        )
    else:
        html_block(
            '<div class="ta-chat-section-label">CONVERSATION</div>'
        )
    show_chat_box()

    html_block(
        """
          <div class="ta-chat-footer">
            <span>🌿 TRIBAL AI</span>
            <span>Preserving knowledge · Connecting cultures</span>
            <span><span class="ta-chat-dot"></span> YOUR CONVERSATION STAYS IN THIS WORKSPACE</span>
          </div>
        </div>
        """
    )
