import streamlit as st

from components.chat_box import show_chat_box
from components.backend_status import show_backend_status
from utils.constants import APP_NAME

def show_home():
    st.title(APP_NAME)
    st.caption(
        "Multilingual AI Assistant for Tribal Communities"
    )
    show_backend_status()
    st.divider()
    show_chat_box()