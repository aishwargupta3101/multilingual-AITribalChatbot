import uuid
from datetime import datetime, timezone

import requests
import streamlit as st
from utils.constants import SUPPORTED_LANGUAGES
import os
BASE_URL = os.getenv("BACKEND_URL","http://127.0.0.1:8000")

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
def _sync_sidebar_page():
    """Keep the app router in sync with the sidebar radio widget."""
    st.session_state.selected_page = st.session_state.sidebar_navigation


def _go_to_chat():
    """Return to the main chat workspace from any tool page."""
    st.session_state.selected_page = "💬 Chat"
    st.session_state.sidebar_navigation = "💬 Chat"


def _open_recent_chat(session_id):
    """Load a recent conversation before the next Streamlit rerun."""
    loaded_messages = load_chat(session_id)
    if loaded_messages:
        st.session_state.messages = loaded_messages
        st.session_state.session_id = session_id
        st.session_state.language = loaded_messages[0].get("language", "english")
        st.session_state.selected_page = "💬 Chat"
        st.session_state.sidebar_navigation = "💬 Chat"


def show_sidebar():
    with st.sidebar:
        # Keep recent conversation buttons readable against the dark sidebar.
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] div[class*="st-key-recent_chat_"] button {
                background: #123b2a !important;
                background-color: #123b2a !important;
                color: #f3fff6 !important;
                -webkit-text-fill-color: #f3fff6 !important;
                border: 1px solid rgba(137, 195, 153, .28) !important;
                border-radius: 12px !important;
                opacity: 1 !important;
                min-height: 48px !important;
                height: auto !important;
                padding: 9px 11px !important;
                text-align: left !important;
                box-shadow: none !important;
            }
            section[data-testid="stSidebar"] div[class*="st-key-recent_chat_"] button p,
            section[data-testid="stSidebar"] div[class*="st-key-recent_chat_"] button span {
                color: #f3fff6 !important;
                -webkit-text-fill-color: #f3fff6 !important;
                opacity: 1 !important;
                white-space: normal !important;
                line-height: 1.35 !important;
                font-size: .82rem !important;
            }
            section[data-testid="stSidebar"] div[class*="st-key-recent_chat_"] button:hover {
                background: #1a5038 !important;
                border-color: #69aa7e !important;
            }
            section[data-testid="stSidebar"] div[class*="st-key-recent_chat_"] {
                margin: 4px 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] .st-key-start_new_conversation button {
                background: #1f6b45 !important;
                background-color: #1f6b45 !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                border: 1px solid #4b9a6b !important;
                opacity: 1 !important;
                font-weight: 700 !important;
                min-height: 42px !important;
            }
            section[data-testid="stSidebar"] .st-key-start_new_conversation button p,
            section[data-testid="stSidebar"] .st-key-start_new_conversation button span {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                opacity: 1 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
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
            key="start_new_conversation",
            type="primary",
            use_container_width=True
        ):

            st.session_state.messages = []
            st.session_state.session_id = str(
                uuid.uuid4()
            )
            st.session_state.selected_page = "💬 Chat"
            st.session_state.sidebar_navigation = "💬 Chat"
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
        # Primary navigation stays in the sidebar.
        # Tool workspaces are opened from the Chat page's (+) menu.
        navigation_options = [
            "🏠 Home",
            "💬 Chat",
            "🎤 Voice",
            "📜 History",
            "⚙ Settings"
        ]

        if "sidebar_navigation" not in st.session_state:
            current_page = st.session_state.get("selected_page", "🏠 Home")
            st.session_state.sidebar_navigation = (
                current_page if current_page in navigation_options else "💬 Chat"
            )

        st.radio(
            "Navigation",
            navigation_options,
            key="sidebar_navigation",
            label_visibility="collapsed",
            on_change=_sync_sidebar_page
        )

        # The radio remains on Chat while a workspace is opened from the
        # (+) Tools menu. A dedicated button is therefore needed: clicking
        # an already-selected Chat radio option does not trigger on_change.
        if st.session_state.get("selected_page") not in (
            "🏠 Home",
            "💬 Chat",
            "🎤 Voice",
            "📜 History",
            "⚙ Settings",
        ):
            st.button(
                "← Back to Chat",
                key="back_to_chat_from_tool",
                use_container_width=True,
                on_click=_go_to_chat,
                type="primary",
            )

        # Do not overwrite selected_page here.
        # Tool buttons set selected_page directly and the app router
        # must be allowed to render the selected workspace.

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

                st.button(
                    button_text,
                    key=(
                        f"recent_chat_"
                        f"{index}_"
                        f"{session_id}"
                    ),
                    use_container_width=True,
                    on_click=_open_recent_chat,
                    args=(session_id,)
                )

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
        LANGUAGE_DISPLAY_NAMES = {
            "english": "English",
            "hindi": "Hindi",
            "manipuri": "Manipuri (Bengali Script)",
            "manipuri_mtei": "Manipuri (Meitei Mayek)",
            "monpa": "Monpa",
            "santali": "Santali (Ol Chiki)",
            "tai_khamti": "Tai Khamti",
            "naga": "Naga",
            "mishmi": "Mishmi"
        }
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

        with st.popover(
                f"🌐 {LANGUAGE_DISPLAY_NAMES.get(st.session_state.language, st.session_state.language.replace('_', ' ').title())}",
                use_container_width=True
        ):
            st.markdown("### Select Language")
            selected_language = st.radio(
                "Language",
                SUPPORTED_LANGUAGES,
                index=SUPPORTED_LANGUAGES.index(st.session_state.language),
                format_func=lambda x: LANGUAGE_DISPLAY_NAMES.get(
                    x, x.replace("_", " ").title()
                ),
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
            pretty_language = LANGUAGE_DISPLAY_NAMES.get(
                st.session_state.language,
                st.session_state.language.replace("_", " ").title()
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