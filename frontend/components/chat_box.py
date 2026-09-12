import streamlit as st
from api.client import APIClient
from api.endpoints import CHAT_ENDPOINT
from components.message import render_message
from components.image_gallery import render_images

def get_language():
    return st.session_state.get(
        "language",
        "english"
    )
def get_language_name(language):
    return language.replace(
        "_",
        " "
    ).title()


def ask_ai(question):
    """
    Send a question to the existing backend.
    This keeps the existing RAG, translation,
    image search and language logic untouched.
    """

    payload = {
        "session_id": st.session_state.session_id,
        "question": question,
        "language": get_language(),
        "document_id": st.session_state.get(
            "document_id"
        )
    }
    response = APIClient.post(
        CHAT_ENDPOINT,
        payload
    )
    data = response.get(
        "data",
        {}
    )
    return {
        "answer": data.get(
            "answer",
            "No answer received."
        ),
        "detected_language": data.get(
            "detected_language",
            "unknown"
        ),
        "language": data.get(
            "language",
            get_language()
        ),
        "sources": data.get(
            "sources",
            []
        ),
        "images": data.get(
            "images",
            []
        ),
        "timestamp": data.get(
            "timestamp",
            ""
        )
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
    Regenerate the AI response for the selected
    user question.
    """

    messages = st.session_state.messages
    if message_index <= 0:
        return
    user_message = None

    for index in range(
        message_index - 1,
        -1,
        -1
    ):
        if messages[index].get("role") == "user":
            user_message = messages[index]
            break
    if not user_message:
        return
    question = user_message.get(
        "content",
        ""
    )

    del messages[message_index]
    with st.spinner(
        "🌿 Tribal AI is thinking..."
    ):
        try:
            result = ask_ai(question)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "language": result["language"],
                    "detected_language": result[
                        "detected_language"
                    ],
                    "sources": result["sources"],
                    "timestamp": result["timestamp"],
                    "images": result["images"]
                }
            )
        except Exception:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "Sorry, I couldn't generate a "
                        "new response right now. "
                        "Please try again."
                    ),
                    "language": get_language(),
                    "detected_language": "unknown",
                    "sources": [],
                    "timestamp": "",
                    "images": []
                }
            )
    st.rerun()


def show_chat_box():
    if "language" not in st.session_state:
        st.session_state.language = "english"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""

    if st.session_state.messages:

        col1, col2 = st.columns(
            [5, 1]
        )
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

    for index, message in enumerate(
        st.session_state.messages
    ):
        role = message.get(
            "role",
            "assistant"
        )
        content = message.get(
            "content",
            ""
        )
        language = message.get(
            "language"
        )
        detected_language = message.get(
            "detected_language"
        )
        sources = message.get(
            "sources"
        )
        timestamp = message.get(
            "timestamp"
        )
        images = message.get(
            "images",
            []
        )
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
            action_col1, action_col2 = st.columns(
                [1, 5]
            )
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
                        "🔄 Regenerate",
                        key=f"regenerate_answer_{index}",
                        use_container_width=False
                    ):
                        regenerate_answer(index)

    voice_text = st.session_state.get(
        "voice_text",
        ""
    )
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
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
            "language": current_language
        }
    )
    render_message(
        role="user",
        content=user_input,
        language=current_language
    )
    with st.spinner(
        "🌿 Tribal AI is thinking..."
    ):
        try:
            result = ask_ai(
                user_input
            )
            answer = result["answer"]
            detected_language = result[
                "detected_language"
            ]
            response_language = result[
                "language"
            ]
            sources = result[
                "sources"
            ]
            images = result[
                "images"
            ]
            timestamp = result[
                "timestamp"
            ]

        except Exception:
            answer = (
                "Sorry, I couldn't process your "
                "question right now. Please try again."
            )
            detected_language = "unknown"
            response_language = current_language
            sources = []
            images = []
            timestamp = ""
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "language": response_language,
            "detected_language": detected_language,
            "sources": sources,
            "timestamp": timestamp,
            "images": images
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
    render_images(
        images
    )
    action_col1, action_col2 = st.columns(
        [1, 5]
    )
    with action_col1:
        st.download_button(
            label="📋 Copy",
            data=answer,
            file_name="tribal_ai_answer.txt",
            mime="text/plain",
            key=f"copy_latest_{len(st.session_state.messages)}",
            use_container_width=True
        )
    with action_col2:
        if st.button(
            "🔄 Regenerate",
            key=f"regenerate_latest_{len(st.session_state.messages)}"
        ):
            regenerate_answer(
                len(st.session_state.messages) - 1
            )