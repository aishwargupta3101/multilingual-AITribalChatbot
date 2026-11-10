import json
import html
from datetime import datetime
import streamlit as st


def html_block(content):
    """
    Convert multiline HTML into a single-line HTML block
    so Streamlit renders it correctly.
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


def _format_when(value):
    """Format stored timestamps without failing on older history records."""
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value or "Date not recorded")


def _show_learning_and_download_history():
    """Show learning records and download events recorded in this Streamlit session."""
    st.divider()
    st.subheader("🎓 Learning & Download History")
    st.caption(
        "This section shows items recorded in the current Streamlit session. "
        "Persistent history across logins/restarts requires saving these records to the backend database."
    )

    learning_items = st.session_state.get("learning_history", [])
    audio_items = st.session_state.get("audio_learning_history", [])
    download_items = st.session_state.get("download_history", [])

    video_tab, audio_tab, downloads_tab = st.tabs(
        ["📘 Video Lessons", "🎧 Audio Learning", "⬇ Downloads"]
    )

    with video_tab:
        videos = [item for item in learning_items if item.get("kind", "video") == "video"]
        if not videos:
            st.info("No video lessons recorded in this session yet. Generate a lesson in Video Learning first.")
        for idx, item in enumerate(reversed(videos)):
            title = item.get("title") or item.get("video_url") or "Video lesson"
            with st.expander(f"📘 {title}"):
                st.caption(f"{_format_when(item.get('created_at'))} · {item.get('language', 'Language not recorded')}")
                if item.get("video_url"):
                    st.markdown(f"[▶ Open original video]({item['video_url']})")
                lesson = item.get("lesson", "")
                if lesson:
                    st.markdown(lesson)
                    st.download_button(
                        "Download saved lesson (.md)",
                        data=str(lesson).encode("utf-8"),
                        file_name=f"video_lesson_{idx + 1}.md",
                        mime="text/markdown",
                        key=f"history_video_download_{idx}_{len(videos)}",
                    )

    with audio_tab:
        if not audio_items:
            st.info(
                "No audio-learning records are available in this session. Audio history will appear here when the audio page records its lessons.")
        for idx, item in enumerate(reversed(audio_items)):
            title = item.get("title", "Audio lesson") if isinstance(item, dict) else "Audio lesson"
            with st.expander(f"🎧 {title}"):
                if isinstance(item, dict):
                    st.caption(_format_when(item.get("created_at")))
                    if item.get("transcript") or item.get("text") or item.get("lesson"):
                        st.write(item.get("transcript") or item.get("text") or item.get("lesson"))
                    if item.get("audio_path") and item.get("audio_bytes"):
                        st.audio(item["audio_bytes"])
                    elif item.get("audio_url"):
                        st.markdown(f"[Open audio]({item['audio_url']})")
                    else:
                        st.caption(
                            "Audio playback is available only if the audio file or a valid audio URL is retained.")

    with downloads_tab:
        if not download_items:
            st.info("No downloads recorded in this session yet.")
        else:
            for item in reversed(download_items):
                st.write(
                    f"**{item.get('filename', 'Downloaded file')}** · "
                    f"{item.get('format', 'file').upper()} · {_format_when(item.get('created_at'))}"
                )


def _inject_history_styles():
    st.markdown("""
    <style>
    .stApp { background:#f6faf8; }
    .history-page-header { display:flex; align-items:center; gap:16px; padding:24px 26px; margin:4px 0 24px; border:1px solid #dcece5; border-radius:22px; background:linear-gradient(135deg,#fff 0%,#effaf4 100%); box-shadow:0 8px 24px rgba(31,87,62,.06); }
    .history-header-icon { display:flex; align-items:center; justify-content:center; width:54px; height:54px; border-radius:16px; background:#dff4e8; font-size:25px; flex-shrink:0; }
    .history-header-title { color:#173b2d; font-size:27px; font-weight:750; letter-spacing:-.5px; }
    .history-header-subtitle { color:#648074; font-size:14px; margin-top:4px; }
    .history-header-language { margin-left:auto; padding:7px 12px; border-radius:999px; background:#e2f4e9; color:#216447; font-size:12px; font-weight:700; }
    .history-stat-card { height:100%; min-height:112px; padding:18px; border:1px solid #deebe4; border-radius:18px; background:#fff; box-shadow:0 5px 18px rgba(31,87,62,.045); }
    .history-stat-icon { font-size:20px; }
    .history-stat-number { color:#1d4432; font-size:28px; font-weight:750; margin-top:7px; }
    .history-stat-label { color:#718579; font-size:12px; font-weight:600; }
    .history-empty-card { text-align:center; padding:30px 20px; border:1px dashed #cbded2; border-radius:18px; background:#fff; }
    .history-empty-icon { font-size:28px; }
    .history-empty-title { color:#234b39; font-size:18px; font-weight:700; margin-top:8px; }
    .history-empty-text { color:#718579; font-size:13px; margin-top:5px; }
    .history-section-header { margin:26px 0 14px; }
    .history-section-title { color:#234b39; font-size:19px; font-weight:700; }
    .history-section-subtitle { color:#718579; font-size:13px; margin-top:3px; }
    .history-message { margin:12px 0; padding:17px 19px; border:1px solid #deebe4; border-radius:18px; background:#fff; box-shadow:0 4px 14px rgba(31,87,62,.035); }
    .history-user-message { border-left:4px solid #6bbf91; }
    .history-ai-message { border-left:4px solid #a8cdb8; background:#fbfefc; }
    .history-message-top { display:flex; align-items:center; gap:9px; margin-bottom:10px; }
    .history-message-icon { font-size:17px; }
    .history-message-role { color:#244b38; font-size:13px; font-weight:750; }
    .history-message-number { margin-left:auto; color:#8a9b90; font-size:11px; }
    .history-message-content { color:#344c3e; font-size:14px; line-height:1.7; white-space:pre-wrap; overflow-wrap:anywhere; }
    .history-actions-title { color:#234b39; font-size:18px; font-weight:700; margin:26px 0 10px; }
    div[data-testid="stTabs"] button { color:#527260; font-weight:650; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color:#176b4a; border-bottom-color:#53a879; }
    div[data-testid="stExpander"] { border:1px solid #deebe4; border-radius:14px; background:#fff; }
    div[data-testid="stDownloadButton"] button { border-radius:12px; border:1px solid #b9ddc8; color:#1d6847; background:#effaf4; font-weight:650; }

    /* Force the History page canvas to match the light Document workspace. */
    html, body, [data-testid="stApp"], .stApp,
    [data-testid="stAppViewContainer"], [data-testid="stMain"],
    .main, .main .block-container {
        background: #f6faf8 !important;
        color: #173b2d !important;
        color-scheme: light !important;
    }
    /* Light Streamlit top header and toolbar to match the page canvas. */
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stHeader"] > div, [data-testid="stToolbar"] > div,
    header[data-testid="stHeader"] {
        background: #f6faf8 !important;
        color: #173b2d !important;
    }
    [data-testid="stHeader"] button, [data-testid="stToolbar"] button,
    [data-testid="stHeader"] svg, [data-testid="stToolbar"] svg {
        color: #315443 !important;
        fill: #315443 !important;
    }
    .main .block-container { background: #f6faf8 !important; }
    .main p, .main label, .main [data-testid="stMarkdownContainer"],
    .main [data-testid="stCaptionContainer"], .main h1, .main h2,
    .main h3, .main h4, .main h5, .main h6 {
        color: #294b3a;
    }
    div[data-testid="stTabs"] [role="tab"] { color: #527260 !important; }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        color: #294b3a !important;
    }
</style>
    """, unsafe_allow_html=True)


def show_chat_history():
    _inject_history_styles()
    messages = st.session_state.get("messages", [])
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
        <div class="history-page-header">

            <div class="history-header-icon">
                📜
            </div>

            <div class="history-header-content">

                <div class="history-header-title">
                    Conversation History
                </div>

                <div class="history-header-subtitle">
                    Review your current conversation with Tribal AI.
                </div>

            </div>

            <div class="history-header-language">
                {language_name}
            </div>

        </div>
        """
    )
    user_messages = sum(
        1
        for message in messages
        if message.get("role") == "user"
    )
    assistant_messages = sum(
        1
        for message in messages
        if message.get("role") == "assistant"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        html_block(
            f"""
            <div class="history-stat-card">

                <div class="history-stat-icon">
                    💬
                </div>

                <div class="history-stat-number">
                    {len(messages)}
                </div>

                <div class="history-stat-label">
                    Total Messages
                </div>

            </div>
            """
        )
    with col2:
        html_block(
            f"""
            <div class="history-stat-card">

                <div class="history-stat-icon">
                    👤
                </div>

                <div class="history-stat-number">
                    {user_messages}
                </div>

                <div class="history-stat-label">
                    Your Messages
                </div>

            </div>
            """
        )
    with col3:
        html_block(
            f"""
            <div class="history-stat-card">

                <div class="history-stat-icon">
                    🤖
                </div>

                <div class="history-stat-number">
                    {assistant_messages}
                </div>

                <div class="history-stat-label">
                    AI Responses
                </div>

            </div>
            """
        )
    if not messages:
        html_block(
            """
            <div class="history-empty-card">

                <div class="history-empty-icon">
                    💬
                </div>

                <div class="history-empty-title">
                    No conversation yet
                </div>

                <div class="history-empty-text">
                    Start a conversation with Tribal AI and
                    your messages will appear here.
                </div>

            </div>
            """
        )
    html_block(
        """
        <div class="history-section-header">

            <div>

                <div class="history-section-title">
                    Current Conversation
                </div>

                <div class="history-section-subtitle">
                    Your messages and Tribal AI responses
                </div>

            </div>

        </div>
        """
    )
    for index, message in enumerate(
            messages,
            start=1
    ):
        role = message.get(
            "role",
            "assistant"
        )
        content = html.escape(
            str(
                message.get(
                    "content",
                    ""
                )
            )
        )
        if role == "user":
            html_block(
                f"""
                <div class="history-message history-user-message">

                    <div class="history-message-top">

                        <div class="history-message-icon">
                            👤
                        </div>

                        <div class="history-message-role">
                            You
                        </div>

                        <div class="history-message-number">
                            #{index}
                        </div>

                    </div>

                    <div class="history-message-content">
                        {content}
                    </div>

                </div>
                """
            )
        else:
            html_block(
                f"""
                <div class="history-message history-ai-message">

                    <div class="history-message-top">

                        <div class="history-message-icon">
                            🌿
                        </div>

                        <div class="history-message-role">
                            Tribal AI
                        </div>

                        <div class="history-message-number">
                            #{index}
                        </div>

                    </div>

                    <div class="history-message-content">
                        {content}
                    </div>

                </div>
                """
            )
    html_block(
        """
        <div class="history-actions-title">
            Export Conversation
        </div>
        """
    )
    history_json = json.dumps(
        messages,
        indent=4,
        ensure_ascii=False
    )
    st.download_button(
        label="⬇ Download Chat History",
        data=history_json,
        file_name="chat_history.json",
        mime="application/json",
        use_container_width=True,
        key="download_chat_history"
    )
    _show_learning_and_download_history()
