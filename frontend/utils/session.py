import uuid
import streamlit as st

def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id =str(uuid.uuid4())
    if "language" not in st.session_state:
        st.session_state.language="English"
    if "messages" not in st.session_state:
        st.session_state.messages =[]
    if "page" not in st.session_state:
        st.session_state.page="Home"
    if"voice_output" not in st.session_state:
        st.session_state.voice_output= True
    if "theme" not in st.session_state:
        st.session_state.theme ="Light"

    if "selected_page" not in st.session_state:
        st.session_state.selected_page ="Home"