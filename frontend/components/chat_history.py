import json
import streamlit as st

def show_chat_history():
    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 Chat History")
    messages = st.session_state.messages
    st.sidebar.write(f"Total Messages {len(messages)}")
    if not messages:
        st.sidebar.info("No conversation yet.")
        return
    for index, message in enumerate(messages,start=1):
        role ="👤" if message["role"] == "user" else "🤖"
        st.sidebar.write(
            f"{index}.{role}{message['content'][:35]}"
        )
    st.sidebar.download_button(
        label=" Download Chat",
        data=json.dumps(messages,indent=4),
        file_name="Chat_history.json",
        mime="application/json"
    )