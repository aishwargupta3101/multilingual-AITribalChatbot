import uuid
import streamlit as st
from utils.constants import SUPPORTED_LANGUAGES

def show_sidebar():
    with st.sidebar:
        st.title("🌿 Tribal AI")
        st.divider()
        if st.button("🆕 New Chat" , use_container_width=True):
            st.session_state.messages =[]
            st.session_state.session_id= str(uuid.uuid4())
            st.rerun()
        st.divider()
        st.session_state.selected_page = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "💬 Chat",
                "📄 Documents",
                "🎤 Voice",
                "📜 History",
                "⚙ Settings"
            ]
        )
        st.divider()
        st.session_state.language = st.selectbox(
            "Language",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(
                st.session_state.language
            )
        )
        st.write("Languages:" ,SUPPORTED_LANGUAGES)