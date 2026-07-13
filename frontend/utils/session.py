import streamlit as st

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages =[]
    if "language" not in st.session_state:
        st.session_state.language="English"
    if "page" not in st.session_state:
        st.session_state.page ="Home"