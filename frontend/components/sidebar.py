import streamlit as st
from utils.constants import SUPPORTED_LANGUAGES

def show_sidebar():
    with st.sidebar:
        st.title("🌿 Tribal AI")
        st.divider()
        st.subheader("Language")
        st.session_state.language = st.selectbox(
            "Choose Language",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(
                st.session_state.language
            )
        )
        st.divider()
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            st.button("📜 Chat History", use_container_width=True)
            st.button("📂 Upload Document", use_container_width=True)
            st.button("⚙ Settings", use_container_width=True)
            st.divider()
            st.success(
                f"Current Language : {st.session_state.language}"
            )