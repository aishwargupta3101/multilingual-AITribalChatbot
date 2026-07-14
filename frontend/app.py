import streamlit as st
from components.sidebar import show_sidebar
from views.home import show_home
from views.chat import show_chat_page
from views.documents import show_documents_page
from views.voice import show_voice_page
from views.history import show_history_page
from views.settings import show_settings_page
from utils.session import initialize_session
st.set_page_config(
    page_title="Tribal AI Chatbot",
    page_icon="🌿",
    layout="wide"
)
initialize_session()
show_sidebar()
page =st.session_state.selected_page
if page == "🏠 Home":
    show_home()
elif page == "💬 Chat":
    show_chat_page()
elif page =="📄 Documents":
    show_documents_page()
elif page == "🎤 Voice":
    show_voice_page()
elif page=="📜 History":
    show_history_page()
elif page=="⚙ Settings":
    show_settings_page()