import streamlit as st
from components.voice_recorder import show_voice_recorder

def show_voice_page():
    st.title("🎤 Voice Assistant")
    st.write("Speak your question and convert it to text.")
    show_voice_recorder()