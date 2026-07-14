import streamlit as st

def show_settings():
    st.subheader("⚙ Settings")
    st.session_state.voice_output = st.checkbox(
        "Enable Voice Response",
        value=st.session_state.voice_output
    )
    st.session_state.theme = st.selectbox(
        "Theme",
        [
            "Light",
            "Dark"
        ],
        index=0 if st.session_state.theme == "Light" else 1
    )
    st.caption("AI Model : Llama 3")
    st.caption("Temperature : 0.3")