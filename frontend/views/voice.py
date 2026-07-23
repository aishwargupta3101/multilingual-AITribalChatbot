import streamlit as st
from components.voice_recorder import show_voice_recorder

def show_voice_page():
    st.title("🎤 Voice Assistant")
    st.write("Speak your question and convert it to text.")
    show_voice_recorder()
    if "voice_text" in st.session_state and st.session_state.voice_text:
        st.markdown("###🎤 You Said")
        st.info(st.session_state.voice_text)

    if "voice_response" in st.session_state and st.session_state.voice_response:
        st.markdown("###🤖 AI Response")
        st.success(st.session_state.voice_response)