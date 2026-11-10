import streamlit as st
import re
from api.client import APIClient
from api.endpoints import CHAT_ENDPOINT
from components.message import render_message, normalize_assistant_markdown
from components.image_gallery import render_images
from components.response_formatter import format_for_display

def get_language():
    return st.session_state.get("language", "english")

def get_language_name(language):
    return language.replace("_", " ").title()


def _queue_prompt(prompt):
    """Queue a suggested starter question for the normal chat pipeline."""
    st.session_state["pending_prompt"] = prompt


def ask_ai(question):
    """
    Send a question to the backend and safely process its response.
    """
    # SANTALI_UNIFIED_CHAT_ROUTING: route Santali-output chat through the shared translation -> chat -> Santali path.
    if get_language().strip().lower() == "santali":
        from api.santali_chat_bridge import ask_santali_question
        return ask_santali_question(
            question=question,
            session_id=st.session_state.session_id,
        )
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

def _requires_verified_response(question):
    """Use complete-response mode for math/programming so malformed partial tokens aren't shown."""
    q = (question or "").lower()
    cues = (
        "three sum", "two sum", "leetcode", "write code", "write a program",
        "debug", "fix this code", "implement", "algorithm", "time complexity",
        "space complexity", "code in python", "code in java", "code in c++",
        "calculate", "solve", "equation", "arithmetic", "percentage",
        "probability", "integral", "derivative", "simplify", "evaluate",
        "what is the value", "math", "mathematics",
    )
    return any(cue in q for cue in cues) or bool(re.search(r"\d\s*[+\-*/%]\s*\d", q))


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
            preview = format_for_display(normalize_assistant_markdown("".join(answer_parts)), get_language())
            placeholder.markdown(preview + " ▌")
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
    """Apply the shared light-mint workspace theme to the chat page."""
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] { background: #f3faf5 !important; }
        [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"] { background: #f3faf5 !important; }
        [data-testid="stMainBlockContainer"] {
            max-width: 1180px; padding-top: 1.5rem; padding-bottom: 2.5rem;
        }
        [data-testid="stAppViewContainer"] {
            background-image: radial-gradient(ellipse at 8% 0%, rgba(187,232,202,.32), transparent 36%),
                              radial-gradient(ellipse at 95% 10%, rgba(211,239,220,.28), transparent 32%) !important;
        }
        .tribal-welcome {
            padding: 1.55rem 1.7rem 1.35rem; border: 1px solid rgba(22,101,52,.14);
            border-radius: 22px; background: linear-gradient(135deg,#e8f7ed 0%,#fff 78%);
            box-shadow: 0 8px 28px rgba(25,75,45,.045); margin: .25rem 0 1.25rem;
        }
        .tribal-eyebrow { color:#267548; font-size:.74rem; font-weight:750; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.5rem; }
        .tribal-welcome h2 { color:#173b28; font-size:clamp(1.55rem,3vw,2.15rem); line-height:1.18; margin:0 0 .6rem; }
        .tribal-welcome p { color:#52665a; font-size:.96rem; line-height:1.65; margin:0; max-width:780px; }
        .tribal-starters-label { font-size:.78rem; font-weight:750; letter-spacing:.08em; color:#587064; margin:.25rem 0 .65rem; }
        div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button {
            border-radius:12px !important; min-height:40px !important; font-weight:600 !important; transition:all .18s ease !important;
        }
        div[data-testid="stButton"] button[kind="secondary"] {
            border:1px solid rgba(75,115,88,.18) !important; background:rgba(255,255,255,.88) !important;
            color:#284b36 !important; text-align:left; white-space:normal; min-height:3.45rem;
            box-shadow:0 3px 12px rgba(25,75,45,.025);
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            border-color:#68b987 !important; color:#17643a !important; background:#f0faf3 !important; transform:translateY(-1px);
        }
        div[data-testid="stDownloadButton"] > button { border:1px solid rgba(75,115,88,.2) !important; background:rgba(255,255,255,.88) !important; color:#284b36 !important; }
        div[data-testid="stDownloadButton"] > button:hover { border-color:rgba(34,140,78,.5) !important; transform:translateY(-1px); }
        .chat-toolbar-label { font-size:.82rem; font-weight:700; color:#52705e; letter-spacing:.025em; padding:.45rem 0; }
        .chat-toolbar-label::before { content:"●"; color:#2b9a59; font-size:.65rem; margin-right:.45rem; vertical-align:1px; }
        .chat-actions-divider { height:1px; background:rgba(76,112,87,.13); margin:.45rem 0 .8rem; }
        [data-testid="stChatInput"] {
            border:1px solid rgba(66,125,83,.22) !important; border-radius:18px !important;
            background:rgba(255,255,255,.96) !important; box-shadow:0 8px 26px rgba(28,82,47,.07) !important;
        }
        [data-testid="stChatInput"] textarea { color:#203b2b !important; }
        [data-testid="stChatInput"] textarea::placeholder { color:#829488 !important; }
        [data-testid="stChatInput"]:focus-within { border-color:#69b985 !important; box-shadow:0 0 0 3px rgba(105,185,133,.13),0 8px 26px rgba(28,82,47,.07) !important; }
        [data-testid="stChatMessage"] {
            border:1px solid rgba(76,112,87,.12); border-radius:18px; padding:.85rem 1rem;
            background:rgba(255,255,255,.88); box-shadow:0 4px 16px rgba(28,82,47,.035);
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background:#e9f7ed; border-color:rgba(48,135,78,.16); }
        @media (max-width:768px) {
            [data-testid="stMainBlockContainer"] { padding:1rem .8rem 2rem; }
            .tribal-welcome { padding:1.2rem 1.1rem; border-radius:18px; }
            .chat-toolbar-label { font-size:.76rem; }
            div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button { min-height:36px !important; font-size:.78rem !important; }
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

    # Startup-friendly empty state: explain the product and help first-time users begin.
    if not st.session_state.messages:
        st.markdown(
            """
            <style>
            .tribal-welcome {
                padding: 1.35rem 1.4rem 1.15rem;
                border: 1px solid rgba(22, 101, 52, 0.16);
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(240, 253, 244, 0.95), rgba(255,255,255,0.98) 72%);
                margin: 0.25rem 0 1.1rem;
            }
            .tribal-eyebrow {
                color: #166534; font-size: 0.76rem; font-weight: 750;
                letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 0.45rem;
            }
            .tribal-welcome h2 {
                color: #163b28; font-size: clamp(1.45rem, 3vw, 2rem);
                line-height: 1.18; margin: 0 0 0.55rem 0;
            }
            .tribal-welcome p {
                color: #475569; font-size: 0.98rem; line-height: 1.6;
                margin: 0; max-width: 760px;
            }
            .tribal-starters-label {
                font-size: 0.82rem; font-weight: 700; color: #475569;
                margin: 0.25rem 0 0.55rem;
            }
            div[data-testid="stButton"] button[kind="secondary"] {
                border: 1px solid rgba(100,116,139,0.22);
                background: rgba(255,255,255,0.92);
                text-align: left;
                white-space: normal;
                min-height: 3.3rem;
            }
            div[data-testid="stButton"] button[kind="secondary"]:hover {
                border-color: #16a34a;
                color: #166534;
                background: #f0fdf4;
            }
            </style>
            <section class="tribal-welcome">
                <div class="tribal-eyebrow">Multilingual learning assistant</div>
                <h2>Learn in the language that feels like home.</h2>
                <p>Ask questions, explore learning materials, and get step-by-step explanations. Choose your reply language and start with a suggested question below.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="tribal-starters-label">TRY ASKING</div>', unsafe_allow_html=True)
        starter_prompts = [
            ("📘", "Explain a difficult topic simply", "Explain artificial intelligence in simple words with three examples."),
            ("🧠", "Help me prepare for an exam", "Create five practice questions on an important topic and include the answers."),
            ("🌐", "Translate and explain a concept", "Explain why language translation is useful in education, with examples."),
            ("🔎", "Ask about tribal knowledge", "Explain how local and traditional knowledge can be preserved using digital tools."),
        ]
        starter_cols = st.columns(2)
        for starter_index, (starter_icon, starter_title, starter_question) in enumerate(starter_prompts):
            with starter_cols[starter_index % 2]:
                if st.button(
                    f"{starter_icon}  {starter_title}",
                    key=f"tribal_starter_{starter_index}",
                    use_container_width=True,
                ):
                    _queue_prompt(starter_question)
                    st.rerun()

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
            if str(message.get("language", "")).lower() == "santali":
                santali_audio_key = f"santali_tts_audio_{index}"
                if st.button("🔊 Speak Santali answer", key=f"santali_tts_button_{index}"):
                    try:
                        from api.santali_tts import synthesize_santali_wav
                        with st.spinner("Generating Santali speech..."):
                            st.session_state[santali_audio_key] = synthesize_santali_wav(content)
                    except Exception as tts_error:
                        st.error(f"Santali speech generation failed: {type(tts_error).__name__}: {tts_error}")
                if st.session_state.get(santali_audio_key):
                    st.audio(st.session_state[santali_audio_key], format="audio/wav")
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
    # SANTALI_UNIFIED_INPUT_GUIDANCE: Santali is the reply language.
    if get_language().strip().lower() == "santali":
        st.caption("Reply language: Santali (Ol Chiki). Type your question in English or Ol Chiki; answers are returned in Santali.")
    # ChatGPT-style plus menu. This is additive; the existing chat_input and
    # ask_ai / ask_ai_stream processing pipeline remain unchanged.
    from components.attachment_menu import render_plus_menu
    composer_col_plus, composer_col_hint = st.columns([0.55, 9.45], vertical_alignment="bottom")
    with composer_col_plus:
        render_plus_menu()
    with composer_col_hint:
        user_input = st.chat_input(
            "Ask a question, request an explanation, or explore a topic..."
        )
    if not user_input:
        user_input = st.session_state.pop("pending_prompt", "")
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
            if (
                current_language in {"english", "hindi", "manipuri", "manipuri_mtei"}
                and not _requires_verified_response(user_input)
            ):
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    result = ask_ai_stream(
                        user_input,
                        response_placeholder,
                    )
            else:
                # Math/code responses are returned only after backend validation,
                # cleanup, and any repair attempt have completed.
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
