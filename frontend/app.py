import streamlit as st
from components.sidebar import show_sidebar
from pages.home import show_home
from utils.session import initialize_session
st.set_page_config(
    page_title="Tribal AI Chatbot",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)
initialize_session()
show_home()
show_sidebar()