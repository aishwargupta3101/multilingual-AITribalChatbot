import streamlit as st

from components.chat_box import show_chat_box


def html_block(content):
    """
    Render custom HTML correctly in Streamlit.
    Converts multiline HTML into a single line
    so Streamlit does not display raw HTML.
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

def show_chat_page():
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
        <div class="chat-header">

            <div class="chat-title-area">

                <div class="chat-title-icon">
                    🌿
                </div>

                <div>

                    <div class="chat-title">
                        Tribal AI
                    </div>

                    <div class="chat-subtitle">
                        Your multilingual knowledge assistant
                    </div>

                </div>

            </div>

            <div class="chat-header-right">

                <div class="chat-language">
                    🌐 {language_name}
                </div>

                <div class="chat-status">
                    <span class="chat-status-dot"></span>
                    Online
                </div>

            </div>

        </div>
        """
    )
    if not st.session_state.get("messages"):
        html_block(
            """
            <div class="chat-welcome">

                <div class="chat-welcome-icon">
                    🌿
                </div>

                <div>

                    <div class="chat-welcome-title">
                        How can I help you?
                    </div>

                    <div class="chat-welcome-text">
                        Ask me about tribal knowledge, culture,
                        traditions, languages, documents, or
                        anything you would like to explore.
                    </div>

                </div>

            </div>
            """
        )
        html_block(
            """
            <div class="chat-suggestions-header">

                <div class="chat-suggestions-title">
                    Start exploring
                </div>

                <div class="chat-suggestions-subtitle">
                    Try one of these questions
                </div>

            </div>
            """
        )
        col1, col2, col3 = st.columns(
            3,
            gap="medium"
        )
        with col1:
            html_block(
                """
                <div class="chat-suggestion-card">

                    <div class="chat-suggestion-icon">
                        📚
                    </div>

                    <div class="chat-suggestion-title">
                        Explore Knowledge
                    </div>

                    <div class="chat-suggestion-text">
                        Discover tribal culture and traditions.
                    </div>

                </div>
                """
            )
        with col2:
            html_block(
                """
                <div class="chat-suggestion-card">

                    <div class="chat-suggestion-icon">
                        💬
                    </div>

                    <div class="chat-suggestion-title">
                        Ask a Question
                    </div>

                    <div class="chat-suggestion-text">
                        Get answers using the Tribal AI
                        knowledge system.
                    </div>

                </div>
                """
            )
        with col3:
            html_block(
                """
                <div class="chat-suggestion-card">

                    <div class="chat-suggestion-icon">
                        🎙
                    </div>

                    <div class="chat-suggestion-title">
                        Use Your Voice
                    </div>

                    <div class="chat-suggestion-text">
                        Speak naturally and let Tribal AI
                        process your question.
                    </div>

                </div>
                """
            )
    if st.session_state.get("messages"):
        html_block(
            """
            <div class="chat-conversation-heading">

                <div class="chat-conversation-title">
                    Conversation
                </div>

                <div class="chat-conversation-line"></div>

            </div>
            """
        )
    show_chat_box()