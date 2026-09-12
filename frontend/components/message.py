import streamlit as st
from html import escape

def html_block(content):
    """
    Remove indentation/newlines before sending HTML
    to Streamlit Markdown.
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

def render_message(
    role,
    content,
    language=None,
    detected_language=None,
    sources=None,
    timestamp=None
):
    """
    Render user and AI messages as clean separate cards.

    Sources are intentionally NOT displayed.
    """
    content = escape(
        str(content)
    ).replace(
        "\n",
        "<br>"
    )
    if role == "user":
        html_block(
            f"""
            <div class="chat-row user-row">
                <div class="user-message-wrapper">
                    <div class="user-label">
                        You
                    </div>
                    <div class="user-message">
                        {content}
                    </div>
                </div>

                <div class="user-avatar">
                    👤
                </div>
            </div>
            """
        )
        return
    html_block(
        f"""
        <div class="chat-row assistant-row">

            <div class="ai-avatar">
                🌿
            </div>

            <div class="assistant-message-wrapper">

                <div class="ai-label">
                    Tribal AI
                    <span class="ai-online-dot"></span>
                </div>

                <div class="assistant-message">
                    {content}
                </div>

            </div>

        </div>
        """
    )
    info = []
    if language:
        info.append(
            f"🌐 {language.replace('_', ' ').title()}"
        )
    if detected_language:
        info.append(
            f"📝 Detected: "
            f"{detected_language.replace('_', ' ').title()}"
        )
    if timestamp:
        info.append(
            f"🕒 {timestamp}"
        )
    if info:
        html_block(
            f"""
            <div class="message-info">
                {" &nbsp; • &nbsp; ".join(info)}
            </div>
            """
        )