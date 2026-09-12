import json
import html
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
def show_chat_history():
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
        return
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