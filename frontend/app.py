import streamlit as st
from styles import apply_custom_css
from components.sidebar import show_sidebar
from views.home import show_home
from views.chat import show_chat_page
from views.documents import show_documents_page
from views.voice import show_voice_page
from views.history import show_history_page
from views.settings import show_settings_page
from utils.session import initialize_session
from utils.professional_ui import apply_professional_ui
from views.video_learning import show_video_learning_page
from views.education import show_education_page
from views.presentation_generator import show_presentation_generator_page

st.set_page_config(
    page_title="Tribal AI Chatbot",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)
initialize_session()

# Streamlit starts a fresh browser session without a selected route.
# Use the exact page label expected by the sidebar and page router.
VALID_PAGES = {
    "🏠 Home",
    "💬 Chat",
    "📄 Documents",
    "🎤 Voice",
    "📜 History",
    "⚙ Settings",
    "🎓 Video Learning",
    "🌿 Education Assistant",
    "📊 Presentation Generator",
}

if st.session_state.get("selected_page") in (None, "", "Home"):
    st.session_state.selected_page = "🏠 Home"
elif st.session_state.get("selected_page") not in VALID_PAGES:
    st.session_state.selected_page = "🏠 Home"

# Keep the sidebar radio aligned on a new/invalid navigation state.
if st.session_state.get("sidebar_navigation") not in VALID_PAGES:
    st.session_state.sidebar_navigation = st.session_state.selected_page

# Defensive initialization for chat components that append to this list.
if "messages" not in st.session_state:
    st.session_state.messages = []

apply_professional_ui()
apply_custom_css()
show_sidebar()

page = st.session_state.selected_page
if page == "🏠 Home":
    show_home()
elif page == "💬 Chat":
    show_chat_page()
elif page == "📄 Documents":
    show_documents_page()
elif page == "🎤 Voice":
    show_voice_page()
elif page == "📜 History":
    show_history_page()
elif page == "⚙ Settings":
    show_settings_page()
elif page == "🎓 Video Learning":
    show_video_learning_page()
elif page == "🌿 Education Assistant":
    show_education_page()
elif page == "📊 Presentation Generator":
    show_presentation_generator_page()
