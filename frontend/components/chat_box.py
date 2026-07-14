import uuid
import streamlit as st
from api.client import APIClient
from api.endpoints import CHAT_ENDPOINT
from components.message import render_message
def show_chat_box():
    for message in st.session_state.messages:
        render_message(
            message["role"],
            message["content"]
        )
    user_input = st.chat_input("Ask something....")
    if not user_input:
        return

    st.session_state.messages.append(
            {
                "role":"user",
                "content":user_input
            }
        )
    render_message("user",user_input)
    payload={
        "session_id":st.session_state.session_id,
        "question":user_input,
        "language":st.session_state.language
    }
    with st.spinner("Thinking..."):
        try:
            response = APIClient.post(
                CHAT_ENDPOINT,
                payload
            )
            answer =(
                response
                .get("data",{})
                .get("answer","No answer received.")
            )
        except Exception as e:
            answer = str(e)
    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )
    render_message(
        "assistant",
        answer
    )
