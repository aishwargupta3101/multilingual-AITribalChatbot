
import streamlit as st
from api.client import APIClient
from api.endpoints import CHAT_ENDPOINT
from components.message import render_message
def show_chat_box():
    for message in st.session_state.messages:
        render_message(

            role=message["role"],
            content=message["content"],
            language=message.get("language"),
            detected_language=message.get("detected_language"),
            sources=message.get("sources"),
            timestamp=message.get("timestamp")
        )
    voice_text= st.session_state.get("voice_test","")
    user_input = st.chat_input("Ask something....")
    if not user_input and voice_text:
        user_input = voice_text
        st.session_state.voice_text =""
    if not user_input:
        return

    st.session_state.messages.append(
            {
                "role":"user",
                "content":user_input,
                "language":st.session_state.language
            }
        )
    render_message(
        role="user",
        content=user_input,
        language=st.session_state.language
    )
    payload={
        "session_id":st.session_state.session_id,
        "question":user_input,
        "language":st.session_state.language,
        "document_id": st.session_state.get("document_id")
    }
    with st.spinner("Thinking..."):
        try:
            response = APIClient.post(
                CHAT_ENDPOINT,
                payload
            )
            data = response.get("data", {})
            answer = data.get(
                "answer",
                "No answer received."
            )
            detected_language = data.get(
                "detected_language",
                "unknown"
            )
            response_language= data.get(
                "language",
                st.session_state.language
            )
            sources =data.get(
                "sources",
                []
            )
            timestamp = data.get(
                "timestamp",
                ""
            )
        except Exception as e:
            answer = str(e)
            detected_language = "unknown"
            response_language = st.session_state.language
            sources = []
            timestamp = ""
    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer,
            "language":response_language,
            "detected_language": detected_language,
            "sources": sources,
            "timestamp": timestamp

        }
    )
    render_message(
        role="assistant",
        content=answer,
        language=response_language,
        detected_language=detected_language,
        sources=sources,
        timestamp=timestamp
    )
