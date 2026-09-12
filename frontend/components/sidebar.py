import uuid
from datetime import datetime, timezone

import requests
import streamlit as st
from utils.constants import SUPPORTED_LANGUAGES
BASE_URL = "http://127.0.0.1:8000"

def html_block(html):
    """
    Render HTML safely in Streamlit.

    Converts multiline HTML into a single line so that
    Streamlit does not interpret the HTML as a code block.
    """
    html = " ".join(
        line.strip()
        for line in html.splitlines()
        if line.strip()
    )
    st.markdown(
        html,
        unsafe_allow_html=True
    )


def get_recent_chats(limit=8):
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/history/recent",
            params={
                "limit": limit
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data.get(
                "data",
                []
            )
        return []

    except Exception as e:
        print(
            f"Recent chat error: {e}"
        )
        return []


def load_chat(session_id):

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/history/{session_id}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            return []
        history = data.get(
            "message",
            []
        )
        messages = []
        for item in history:
            role = item.get(
                "role"
            )
            content = item.get(
                "message",
                ""
            )
            language = item.get(
                "language",
                "english"
            )
            created_at = item.get(
                "created_at",
                ""
            )
            messages.append(
                {
                    "role": role,
                    "content": content,
                    "language": language,
                    "timestamp": str(
                        created_at
                    )
                }
            )
        return messages

    except Exception as e:
        st.error(
            f"Unable to load conversation: {e}"
        )
        return []


def format_chat_date(date_value):
    if not date_value:
        return ""

    try:
        if isinstance(
            date_value,
            str
        ):
            date_value = datetime.fromisoformat(
                date_value.replace(
                    "Z",
                    "+00:00"
                )
            )
        now = datetime.now(
            timezone.utc
        )

        if date_value.tzinfo is None:
            date_value = date_value.replace(
                tzinfo=timezone.utc
            )
        difference = now - date_value
        if difference.days == 0:
            return "Today"
        if difference.days == 1:
            return "Yesterday"

        if difference.days < 7:
            return (
                f"{difference.days} days ago"
            )
        return date_value.strftime(
            "%d %b %Y"
        )
    except Exception:
        return ""


def get_chat_title(chat):
    messages = chat.get(
        "messages",
        []
    )
    for message in reversed(
        messages
    ):
        if message.get(
            "role"
        ) == "user":

            text = message.get(
                "message",
                ""
            ).strip()
            if text:
                if len(text) > 32:
                    return (
                        text[:32]
                        + "..."
                    )

                return text
    last_message = chat.get(
        "last_message",
        "New conversation"
    )
    last_message = str(
        last_message
    ).strip()

    if len(last_message) > 32:
        return (
            last_message[:32]
            + "..."
        )
    return (
        last_message
        or "New conversation"
    )
def show_sidebar():
    with st.sidebar:
        html_block(
            """
            <div class="tribal-brand">
                <div class="brand-symbol">
                    🌿
                </div>
                <div class="brand-name">
                    Tribal AI
                </div>
                <div class="brand-subtitle">
                    Intelligent • Multilingual • Cultural
                </div>
                <div class="online-badge">
                    <span class="online-dot"></span>
                    AI SYSTEM ONLINE
                </div>
            </div>
            """
        )
        if st.button(
            "✨  Start New Conversation",
            use_container_width=True
        ):

            st.session_state.messages = []
            st.session_state.session_id = str(
                uuid.uuid4()
            )
            st.session_state.selected_page = (
                "💬 Chat"
            )
            st.rerun()

        html_block(
            """
            <div class="sidebar-space-small"></div>
            """
        )
        html_block(
            """
            <div class="sidebar-section-title">
                EXPLORE
            </div>
            """
        )
        st.session_state.selected_page = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "💬 Chat",
                "📄 Documents",
                "🎤 Voice",
                "📜 History",
                "⚙ Settings"
            ],
            label_visibility="collapsed"
        )
        html_block(
            """
            <div class="sidebar-divider"></div>
            """
        )
        html_block(
            """
            <div class="sidebar-section-title">
                RECENT CHATS
            </div>
            """
        )
        recent_chats = get_recent_chats(
            limit=8
        )
        if recent_chats:
            for index, chat in enumerate(
                recent_chats
            ):
                session_id = chat.get(
                    "_id",
                    ""
                )
                if not session_id:
                    continue
                title = get_chat_title(
                    chat
                )
                date_text = format_chat_date(
                    chat.get(
                        "last_activity"
                    )
                )
                language = chat.get(
                    "language",
                    "english"
                )
                if language.lower() in [
                    "tai_khamti",
                    "tai khamti"
                ]:
                    icon = "🌿"

                else:
                    icon = "💬"
                button_text = (
                    f"{icon}  {title}"
                )
                if date_text:

                    button_text += (
                        f"\n   {date_text}"
                    )

                if st.button(
                    button_text,
                    key=(
                        f"recent_chat_"
                        f"{index}_"
                        f"{session_id}"
                    ),
                    use_container_width=True
                ):
                    loaded_messages = load_chat(
                        session_id
                    )

                    if loaded_messages:
                        st.session_state.messages = (
                            loaded_messages
                        )
                        st.session_state.session_id = (
                            session_id
                        )
                        st.session_state.language = (
                            loaded_messages[0].get(
                                "language",
                                "english"
                            )
                        )
                        st.session_state.selected_page = (
                            "💬 Chat"
                        )
                        st.rerun()

        else:
            html_block(
                """
                <div class="no-chats">
                    No previous conversations yet.
                </div>
                """
            )
        html_block(
            """
            <div class="sidebar-divider"></div>
            """
        )
        html_block(
            """
            <div class="sidebar-section-title">
                CONVERSATION LANGUAGE
            </div>
            """
        )
        if "language" not in st.session_state:
            st.session_state.language = (
                SUPPORTED_LANGUAGES[0]
            )
        if (
            st.session_state.language
            not in SUPPORTED_LANGUAGES
        ):
            st.session_state.language = (
                SUPPORTED_LANGUAGES[0]
            )

        # Language selector
        with st.popover(
                f"🌐 {st.session_state.language.replace('_', ' ').title()}",
                use_container_width=True
        ):
            st.markdown(
                "### Select Language"
            )
            selected_language = st.radio(
                "Language",
                SUPPORTED_LANGUAGES,
                index=SUPPORTED_LANGUAGES.index(
                    st.session_state.language
                ),
                format_func=lambda x:
                x.replace(
                    "_",
                    " "
                ).title(),
                label_visibility="collapsed",
                key="conversation_language_radio"
            )
            if selected_language != st.session_state.language:
                st.session_state.language = selected_language
                st.rerun()
        language = (
            st.session_state.language.lower()
        )
        if language in [
            "tai_khamti",
            "tai khamti"
        ]:
            html_block(
                """
                <div class="language-mode tai-mode">

                    <div class="mode-icon">
                        🌿
                    </div>
                    <div class="mode-content">
                        <div class="mode-title">
                            Tai Khamti Mode
                        </div>

                        <div class="mode-description">
                            Dedicated cultural knowledge
                        </div>
                    </div>

                    <div class="mode-status">
                        ●
                    </div>
                </div>
                """
            )

        else:
            pretty_language = (
                st.session_state.language
                .replace(
                    "_",
                    " "
                )
                .title()
            )
            html_block(
                f"""
                <div class="language-mode">
                    <div class="mode-icon">
                        🌐
                    </div>
                    <div class="mode-content">
                        <div class="mode-title">
                            {pretty_language} Mode
                        </div>
                        <div class="mode-description">
                            Standard AI knowledge
                        </div>
                    </div>
                    <div class="mode-status">
                        ●
                    </div>
                </div>
                """
            )
        html_block(
            """
            <div class="sidebar-bottom">
                <div class="bottom-title">
                    🌱 Preserving Knowledge
                </div>

                <div class="bottom-text">
                    Technology connecting people,
                    language and culture.
                </div>
                <div class="version">
                    TRIBAL AI • v1.0.0
                </div>
            </div>
            """
        )