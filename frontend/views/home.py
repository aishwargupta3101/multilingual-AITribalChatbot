import streamlit as st
from utils.constants import APP_NAME

def show_home():
    st.title(APP_NAME)
    st.write(
        "Welcome to the Multilingual Tribal AI Chatbot."
    )
    st.info(
        """
Choose an option from the sidebar.
💬 Chat
📄 Upload Documents
🎤 Voice Assistant
⚙ Settings
"""
    )