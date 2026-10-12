import streamlit as st
from api.client import APIClient
from api.endpoints import CHAT_ENDPOINT
from components.message import render_message
from components.image_gallery import render_images

def get_language():
    return st.session_state.get("language", "english")

def get_language_name(language):
    return language.replace("_", " ").title()

def ask_ai(question):
    """
    Send a question to the backend and safely process its response.
    """
    try:
        response = APIClient.chat(
            question=question,
            session_id=st.session_state.session_id,
            language=get_language()
        )
        print("\n========== CHAT API RESPONSE ==========")
        print(response)
        print("=======================================\n")
        if not isinstance(response, dict):
            raise ValueError(
                f"Unexpected API response type: {type(response)}"
            )
        if response.get("success") is False:
            raise ValueError(
                response.get("error", "Chat API returned an error.")
            )
        data = response.get("data")
        if not isinstance(data, dict):
            data = response
        answer = (
            data.get("answer")
            or data.get("response")
            or data.get("message")
        )
        if not answer:
            raise ValueError(
                f"No answer found in API response: {response}"
            )
        return {
            "answer": answer,
            "detected_language": data.get(
                "detected_language",
                "unknown"
            ),
            "language": data.get(
                "language",
                get_language()
            ),
            "sources": data.get("sources", []),
            "images": data.get("images", []),
            "timestamp": data.get("timestamp", "")
        }
    except Exception as e:
        print("\n========== CHAT ERROR ==========")
        print(f"Error: {type(e).__name__}: {e}")
        print("================================\n")
        raise

def ask_ai_stream(question, placeholder):
    """Stream an English response and return the final chat data."""
    answer_parts = []
    final_response = None
    for event in APIClient.chat_stream(
        question=question,
        session_id=st.session_state.session_id,
        language=get_language(),
    ):
        event_type = event.get("type")
        if event_type == "token":
            token = event.get("content", "")
            answer_parts.append(token)
            placeholder.markdown(
                "".join(answer_parts) + "▌"
            )
        elif event_type == "complete":
            final_response = event.get("data")
        elif event_type == "error":
            raise ValueError(
                event.get("message", "Streaming failed.")
            )
    if not isinstance(final_response, dict):
        raise ValueError("Streaming did not return a completed response.")
    if final_response.get("success") is False:
        raise ValueError(
            final_response.get("error", "Streaming failed.")
        )
    data = final_response.get("data")
    if not isinstance(data, dict):
        data = final_response
    answer = (
        data.get("answer")
        or data.get("response")
        or data.get("message")
        or "".join(answer_parts)
    )
    if not answer:
        raise ValueError("No answer found in streaming response.")
    return {
        "answer": answer,
        "detected_language": data.get(
            "detected_language",
            "unknown"
        ),
        "language": data.get(
            "language",
            get_language()
        ),
        "sources": data.get("sources", []),
        "images": data.get("images", []),
        "timestamp": data.get("timestamp", ""),
    }

def clear_conversation():
    """
    Clear only the current chat.
    Knowledge documents and backend knowledge remain untouched.
    """
    st.session_state.messages = []
    st.session_state.voice_text = ""
    st.session_state.document_id = None
    st.rerun()

def regenerate_answer(message_index):
    """
    Regenerate the AI response for the selected user question.
    """
    messages = st.session_state.messages
    if message_index <= 0:
        return
    user_message = None
    for index in range(message_index - 1, -1, -1):
        if messages[index].get("role") == "user":
            user_message = messages[index]
            break
    if not user_message:
        return
    question = user_message.get("content", "")
    del messages[message_index]
    with st.spinner("🌿 Tribal AI is thinking..."):
        try:
            result = ask_ai(question)
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "language": result["language"],
                "detected_language": result["detected_language"],
                "sources": result["sources"],
                "timestamp": result["timestamp"],
                "images": result["images"]
            })
        except Exception as e:
            st.error(f"Chat error: {type(e).__name__}: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Sorry, I couldn't generate a new response right now. Please try again.",
                "language": get_language(),
                "detected_language": "unknown",
                "sources": [],
                "timestamp": "",
                "images": []
            })
    st.rerun()

def apply_chat_box_ui():
    st.markdown(
        """
        <style>
        .chat-toolbar-label {
            font-size: 0.82rem;
            font-weight: 600;
            color: #6b7280;
            letter-spacing: 0.02em;
            padding: 0.45rem 0;
        }
        .chat-toolbar-label::before {
            content: "●";
            color: #22c55e;
            font-size: 0.65rem;
            margin-right: 0.45rem;
            vertical-align: 1px;
        }
        div[data-testid="stDownloadButton"] > button,
        div[data-testid="stButton"] > button {
            border-radius: 10px !important;
            min-height: 38px !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            transition: all 0.18s ease !important;
        }
        div[data-testid="stDownloadButton"] > button {
            border: 1px solid rgba(100, 116, 139, 0.22) !important;
            background: rgba(255, 255, 255, 0.72) !important;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-1px);
            border-color: rgba(34, 197, 94, 0.45) !important;
        }
        .chat-actions-divider {
            height: 1px;
            background: rgba(100, 116, 139, 0.12);
            margin: 0.45rem 0 0.8rem;
        }
        @media (max-width: 768px) {
            .chat-toolbar-label {
                font-size: 0.76rem;
            }
            div[data-testid="stDownloadButton"] > button,
            div[data-testid="stButton"] > button {
                min-height: 34px !important;
                font-size: 0.76rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_chat_box():
    apply_chat_box_ui()
    if "language" not in st.session_state:
        st.session_state.language = "english"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""
    if st.session_state.messages:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                """
                <div class="chat-toolbar-label">
                    Current Conversation
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            if st.button(
                "🗑 Clear",
                key="clear_chat_button",
                use_container_width=True
            ):
                clear_conversation()
    for index, message in enumerate(st.session_state.messages):
        role = message.get("role", "assistant")
        content = message.get("content", "")
        language = message.get("language")
        detected_language = message.get("detected_language")
        sources = message.get("sources")
        timestamp = message.get("timestamp")
        images = message.get("images", [])
        render_message(
            role=role,
            content=content,
            language=language,
            detected_language=detected_language,
            sources=sources,
            timestamp=timestamp
        )
        if role == "assistant":
            render_images(images)
            st.markdown(
                '<div class="chat-actions-divider"></div>',
                unsafe_allow_html=True
            )
            action_col1, action_col2, action_spacer = st.columns([1.1, 1.5, 4.4])
            with action_col1:
                st.download_button(
                    label="📋 Copy",
                    data=content,
                    file_name="tribal_ai_answer.txt",
                    mime="text/plain",
                    key=f"copy_answer_{index}",
                    use_container_width=True
                )
            if index > 0:
                with action_col2:
                    if st.button(
                        "↻ Regenerate",
                        key=f"regenerate_answer_{index}",
                        use_container_width=True
                    ):
                        regenerate_answer(index)
    voice_text = st.session_state.get("voice_text", "")
    user_input = st.chat_input(
        "Ask something about tribal knowledge..."
    )
    if not user_input and voice_text:
        user_input = voice_text
        st.session_state.voice_text = ""
    if not user_input:
        return
    user_input = user_input.strip()
    if not user_input:
        return
    current_language = get_language()
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "language": current_language
    })
    render_message(
        role="user",
        content=user_input,
        language=current_language
    )
    with st.spinner("🌿 Tribal AI is thinking..."):
        try:
            if current_language in {"english", "hindi", "manipuri", "manipuri_mtei"}:
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    result = ask_ai_stream(
                        user_input,
                        response_placeholder,
                    )
            else:
                result = ask_ai(user_input)
            answer = result["answer"]
            detected_language = result["detected_language"]
            response_language = result["language"]
            sources = result["sources"]
            images = result["images"]
            timestamp = result["timestamp"]
        except Exception as e:
            st.error(
                f"Chat error: {type(e).__name__}: {e}"
            )
            answer = (
                "Sorry, I couldn't process your question "
                "right now. Please try again."
            )
            detected_language = "unknown"
            response_language = current_language
            sources = []
            images = []
            timestamp = ""
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "language": response_language,
        "detected_language": detected_language,
        "sources": sources,
        "timestamp": timestamp,
        "images": images
    })
    st.rerun()