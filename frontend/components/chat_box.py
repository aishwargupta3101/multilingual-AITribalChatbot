import streamlit as st


def render_tribal_ai_orb() -> None:
    """Render the lightweight CSS-only 3D Tribal AI orb."""
    st.markdown(
        '<div class="tribal-orb-ring"><div class="tribal-ai-orb"></div></div>',
        unsafe_allow_html=True,
    )


def render_tribal_typing_indicator() -> None:
    """Render an accessible animated three-dot thinking indicator."""
    st.markdown(
        '<div class="tribal-typing" aria-label="Tribal AI is thinking">'
        '<span></span><span></span><span></span></div>',
        unsafe_allow_html=True,
    )


import re
from api.client import APIClient
from api.endpoints import CHAT_ENDPOINT
from components.message import render_message, normalize_assistant_markdown
from components.response_formatter import format_for_display


def get_language():
    return st.session_state.get("language", "english")


def get_language_name(language):
    return language.replace("_", " ").title()


def _queue_prompt(prompt):
    """Queue a suggested starter question for the normal chat pipeline."""
    st.session_state["pending_prompt"] = prompt


def _with_visual_format_hint(question):
    """
    Add strict teaching and visual-format instructions without exposing them
    in the rendered user bubble or stored-history display.
    """
    text = str(question or "").strip()
    visual_instruction = (
        "\\n\\n[TRIBAL AI RESPONSE FORMAT — follow these rules strictly: "
        "Teach the concept to a curious student in clear, natural language. "
        "Start with a concise plain-language explanation, then use a small number "
        "of useful headings, short paragraphs, and meaningful bullets. Explain "
        "technical terms when first introduced. Use an analogy only when it helps. "
        "VISUAL RULE: Decide whether a diagram materially improves understanding. "
        "For processes, pipelines, architectures, networks, data flows, or connected "
        "components, include exactly one Mermaid diagram in a fenced ```mermaid code "
        "block immediately after the short paragraph introducing that process. "
        "Use only simple valid Mermaid flowchart syntax: start with `flowchart TD` "
        "or `flowchart LR`, give every node a short readable label, and connect nodes "
        "with ordinary arrows. Keep diagrams compact (about 3–7 nodes where possible). "
        "After the diagram, explain its flow in a few sentences. "
        "ABSOLUTELY FORBIDDEN: ASCII art, text boxes made from +--- or | characters, "
        "arrow-only text drawings, pseudo-diagrams in ordinary code blocks, or headings "
        "such as 'Simple Diagram (textual representation)'. Never substitute a text "
        "drawing for Mermaid. If a diagram is not useful, omit it completely and explain "
        "normally; do not create a textual substitute. "
        "TABLE RULE: use a Markdown table only for at least 3 comparable items, with a "
        "header, separator, and one complete row per item. Never create pipe-separated "
        "pseudo-tables. Numbered lists must start at 1 and be sequential. Every bullet "
        "must be a complete point with its explanation. Proofread spacing, headings, "
        "and formatting. Avoid repetition, unnecessary sections, and oversized answers.]"
    )
    return text + visual_instruction


def _clean_stored_user_message(content):
    """Hide legacy presentation instructions saved in older chat records."""
    text = str(content or "")
    marker = "\\n\\n[Tribal AI teaching and presentation instructions:"
    if marker in text:
        text = text.split(marker, 1)[0]
    # Also handle records where line endings were normalized before persistence.
    marker_plain = "[Tribal AI teaching and presentation instructions:"
    if marker_plain in text:
        text = text.split(marker_plain, 1)[0].rstrip()
    return text.strip()


def _should_show_official_sources(question):
    """Show citations only for source-seeking or current/official-information queries."""
    q = str(question or "").lower()
    cues = (
        "source", "sources", "reference", "references", "citation", "cite",
        "official website", "official link", "latest", "current", "today",
        "recent", "government scheme", "scholarship", "eligibility",
        "application", "deadline", "notification", "policy", "rules",
        "statistics", "report", "research paper", "according to"
    )
    return any(cue in q for cue in cues)


def ask_ai(question):
    """
    Send a question to the backend and safely process its response.
    """
    # SANTALI_UNIFIED_CHAT_ROUTING: route Santali-output chat through the shared translation -> chat -> Santali path.
    if get_language().strip().lower() == "santali":
        from api.santali_chat_bridge import ask_santali_question
        return ask_santali_question(
            question=_with_visual_format_hint(question),
            session_id=st.session_state.session_id,
        )
    try:
        response = APIClient.chat(
            question=_with_visual_format_hint(question),
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
            question=_with_visual_format_hint(question),
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
    question = _clean_stored_user_message(user_message.get("content", ""))
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

        /* ChatGPT-inspired composer row and plus/tools launcher */
        [data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(.st-key-tribal_plus_menu) {
            align-items: flex-end !important;
            gap: .55rem !important;
        }
        .st-key-tribal_plus_menu {
            margin-bottom: .18rem !important;
        }
        .st-key-tribal_plus_menu [data-testid="stPopover"] > button {
            width: 48px !important;
            min-width: 48px !important;
            height: 48px !important;
            min-height: 48px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            border: 1px solid #c9dfd0 !important;
            background: linear-gradient(145deg,#ffffff,#e8f6ec) !important;
            color: #17643a !important;
            box-shadow: 0 4px 14px rgba(28,91,50,.10) !important;
            transition: transform .2s ease, box-shadow .2s ease, background .2s ease !important;
        }
        .st-key-tribal_plus_menu [data-testid="stPopover"] > button:hover {
            transform: translateY(-2px) rotate(8deg) !important;
            background: #e1f4e7 !important;
            border-color: #82c497 !important;
            box-shadow: 0 7px 18px rgba(28,120,60,.16) !important;
        }
        .st-key-tribal_plus_menu [data-testid="stPopover"] > button p,
        .st-key-tribal_plus_menu [data-testid="stPopover"] > button span,
        .st-key-tribal_plus_menu [data-testid="stPopover"] > button svg {
            color: #17643a !important;
            fill: #17643a !important;
            font-size: 22px !important;
            font-weight: 700 !important;
        }
        div[data-testid="stPopoverBody"] {
            width: min(360px, calc(100vw - 28px)) !important;
            padding: 17px !important;
            border: 1px solid #d7e8dc !important;
            border-radius: 20px !important;
            background: rgba(255,255,255,.98) !important;
            box-shadow: 0 18px 48px rgba(18,54,31,.17) !important;
            backdrop-filter: blur(16px) !important;
        }
        div[data-testid="stPopoverBody"] .tools-heading {
            color: #173b28 !important;
            font-size: 15px !important;
            font-weight: 800 !important;
            letter-spacing: -.01em !important;
            margin: 0 0 3px !important;
        }
        div[data-testid="stPopoverBody"] .tools-subheading {
            color: #718477 !important;
            font-size: 12px !important;
            margin-bottom: 13px !important;
        }
        div[data-testid="stPopoverBody"] [data-testid="stButton"] button {
            min-height: 48px !important;
            border-radius: 13px !important;
            border: 1px solid #e0ebe3 !important;
            background: linear-gradient(145deg,#ffffff,#f5faf6) !important;
            color: #244b33 !important;
            font-size: 13px !important;
            font-weight: 650 !important;
            box-shadow: 0 2px 7px rgba(26,80,44,.035) !important;
            transition: all .18s ease !important;
        }
        div[data-testid="stPopoverBody"] [data-testid="stButton"] button:hover {
            transform: translateY(-2px) !important;
            border-color: #8fc9a0 !important;
            background: #eff9f2 !important;
            box-shadow: 0 7px 16px rgba(26,120,60,.09) !important;
        }
        div[data-testid="stPopoverBody"] [data-testid="stButton"] button p,
        div[data-testid="stPopoverBody"] [data-testid="stButton"] button span {
            color: #244b33 !important;
            font-size: 13px !important;
        }
        [data-testid="stChatInput"] {
            border: 1px solid #d4e4d9 !important;
            border-radius: 25px !important;
            background: rgba(255,255,255,.98) !important;
            box-shadow: 0 8px 28px rgba(28,82,47,.075) !important;
            transition: border-color .2s ease, box-shadow .2s ease !important;
            padding: .35rem .5rem !important;
        }
        [data-testid="stChatInput"]:focus-within {
            border-color: #75bd8c !important;
            box-shadow: 0 0 0 4px rgba(105,185,133,.12),0 10px 30px rgba(28,82,47,.09) !important;
        }
        [data-testid="stChatInput"] textarea {
            min-height: 42px !important;
            padding-top: .72rem !important;
            color: #203b2b !important;
        }
        [data-testid="stChatInput"] button {
            border-radius: 50% !important;
            background: #18834a !important;
            color: #fff !important;
            border: 0 !important;
            width: 36px !important;
            height: 36px !important;
            transition: transform .18s ease, background .18s ease !important;
        }
        [data-testid="stChatInput"] button:hover {
            transform: translateY(-2px) !important;
            background: #116c3b !important;
        }
        @media (max-width:768px) {
            .st-key-tribal_plus_menu [data-testid="stPopover"] > button {
                width: 42px !important; min-width:42px !important;
                height:42px !important; min-height:42px !important;
            }
            div[data-testid="stPopoverBody"] { width:min(320px,calc(100vw - 24px)) !important; }
        }

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

        /* Tribal AI 3D white-space experience */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background: #FFFFFF !important;
            color: #202B24 !important;
        }
        [data-testid="stMainBlockContainer"] {
            position: relative !important;
            isolation: isolate !important;
        }
        [data-testid="stMainBlockContainer"]::before {
            content: "";
            position: fixed;
            z-index: -1;
            width: 360px;
            height: 360px;
            top: 10%;
            right: -170px;
            pointer-events: none;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(108,205,139,.10), transparent 68%);
            animation: tribalAmbientFloat 13s ease-in-out infinite alternate;
        }

        /* Welcome heading: crisp text with a subtle entrance */
        .tribal-welcome, .tribal-home-title, .tribal-chat-welcome {
            color: #183B28 !important;
            animation: tribalWelcomeIn .8s cubic-bezier(.2,.7,.2,1) both;
        }

        /* Raised cards: dimensional hover without reducing readability */
        .tribal-starter-card,
        .tribal-feature-card,
        [data-testid="stMainBlockContainer"] .st-key-starter_card {
            background: linear-gradient(145deg,#FFFFFF 0%,#F8FCF9 100%) !important;
            border: 1px solid #DCEBE0 !important;
            border-radius: 20px !important;
            box-shadow: 0 5px 0 #E6F0E9, 0 12px 28px rgba(24,77,43,.07) !important;
            transition: transform .24s ease, box-shadow .24s ease, border-color .24s ease !important;
        }
        .tribal-starter-card:hover,
        .tribal-feature-card:hover {
            transform: translateY(-6px) perspective(900px) rotateX(2deg) !important;
            border-color: #8BC99D !important;
            box-shadow: 0 7px 0 #D7EBDD, 0 20px 38px rgba(24,112,55,.13) !important;
        }

        /* Floating 3D orb for the AI welcome area */
        .tribal-ai-orb {
            position: relative;
            width: 112px;
            height: 112px;
            margin: 12px auto 20px;
            border-radius: 50%;
            background:
                radial-gradient(circle at 32% 25%, #FFFFFF 0 4%, #C9F8D6 10%, transparent 24%),
                radial-gradient(circle at 38% 32%, #8BE8A8 0%, #31B96B 28%, #087B42 62%, #064B2D 100%);
            box-shadow:
                inset -12px -15px 25px rgba(0,43,23,.36),
                inset 8px 8px 20px rgba(255,255,255,.75),
                0 12px 25px rgba(20,111,58,.22),
                0 0 0 9px rgba(70,180,103,.07),
                0 0 35px rgba(66,190,105,.20);
            animation: tribalOrbFloat 4.2s ease-in-out infinite;
        }
        .tribal-ai-orb::before {
            content: "";
            position: absolute;
            inset: 12px 17px 18px 12px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,.5);
            transform: rotate(-28deg);
            box-shadow: 0 0 16px rgba(255,255,255,.2);
        }
        .tribal-ai-orb::after {
            content: "✦";
            position: absolute;
            top: 27px;
            left: 42px;
            color: #F4FFF6;
            font-size: 32px;
            text-shadow: 0 0 15px rgba(255,255,255,.95), 0 0 25px #B9FFD0;
            animation: tribalOrbSpark 2.8s ease-in-out infinite;
        }
        .tribal-orb-ring {
            position: relative;
            width: 146px;
            height: 146px;
            margin: 0 auto;
            display: grid;
            place-items: center;
        }
        .tribal-orb-ring::before,
        .tribal-orb-ring::after {
            content: "";
            position: absolute;
            inset: 3px;
            border: 1px solid rgba(49,166,91,.34);
            border-radius: 50%;
            transform: rotateX(68deg) rotate(-18deg);
            animation: tribalRingSpin 9s linear infinite;
        }
        .tribal-orb-ring::after {
            inset: 12px -5px;
            border-color: rgba(112,205,139,.42);
            transform: rotateX(68deg) rotate(35deg);
            animation-direction: reverse;
            animation-duration: 12s;
        }

        /* Typing indicator: three softly bouncing green lights */
        .tribal-typing {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 10px 14px;
            border: 1px solid #E0ECE3;
            border-radius: 16px;
            background: #FFFFFF;
            box-shadow: 0 5px 16px rgba(24,77,43,.06);
        }
        .tribal-typing span {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #269653;
            animation: tribalDotBounce 1.1s ease-in-out infinite;
        }
        .tribal-typing span:nth-child(2) { animation-delay: .15s; }
        .tribal-typing span:nth-child(3) { animation-delay: .3s; }

        /* Message entrances and clean message surfaces */
        [data-testid="stChatMessage"] {
            animation: tribalMessageIn .42s cubic-bezier(.2,.7,.2,1) both;
            border-radius: 18px !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #F5FAF6 !important;
            border: 1px solid #E4EEE6 !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: #FFFFFF !important;
            border: 1px solid #EDF2EE !important;
            box-shadow: 0 5px 18px rgba(24,77,43,.035) !important;
        }


        /* Minimal animated empty state: no welcome banner and no prompt tiles */
        .tribal-empty-stage {
            min-height: 390px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            overflow: hidden;
            padding: 30px 16px 24px;
            background:
                radial-gradient(ellipse at 50% 48%, rgba(220,247,228,.38), transparent 43%),
                #FFFFFF;
            border-radius: 26px;
        }
        .tribal-empty-stage::before,
        .tribal-empty-stage::after {
            content: "";
            position: absolute;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            border: 1px solid rgba(52,166,91,.10);
            animation: tribalHaloDrift 12s ease-in-out infinite alternate;
            pointer-events: none;
        }
        .tribal-empty-stage::after {
            width: 330px;
            height: 330px;
            border-color: rgba(52,166,91,.07);
            animation-duration: 17s;
            animation-direction: alternate-reverse;
        }
        .tribal-orb-ring {
            width: 190px !important;
            height: 190px !important;
            margin: 0 auto 22px !important;
            filter: drop-shadow(0 18px 24px rgba(31,126,66,.14));
        }
        .tribal-ai-orb {
            width: 116px !important;
            height: 116px !important;
            background:
                radial-gradient(circle at 28% 22%, #FFFFFF 0 3%, #E5FFEC 7%, transparent 21%),
                radial-gradient(circle at 35% 30%, #A9F4BC 0%, #55D77F 22%, #20A957 48%, #08743D 75%, #064526 100%) !important;
            box-shadow:
                inset -18px -20px 28px rgba(0,48,25,.43),
                inset 10px 9px 22px rgba(255,255,255,.82),
                0 17px 28px rgba(14,105,51,.24),
                0 0 35px rgba(54,190,100,.28) !important;
            animation: tribalOrbFloat 3.8s ease-in-out infinite, tribalOrbTilt 8s ease-in-out infinite !important;
        }
        .tribal-ai-orb::after {
            content: "✧" !important;
            top: 30px !important;
            left: 42px !important;
            font-size: 38px !important;
            color: #F4FFF6 !important;
            text-shadow: 0 0 12px #FFFFFF, 0 0 28px #A8FFC0 !important;
        }
        .tribal-orb-ring::before {
            inset: 3px !important;
            border-width: 2px !important;
            border-color: rgba(34,166,83,.32) !important;
            transform: rotateX(68deg) rotate(-18deg) !important;
            animation: tribalOrbitOne 7s linear infinite !important;
        }
        .tribal-orb-ring::after {
            inset: 15px -4px !important;
            border-width: 1px !important;
            border-color: rgba(89,199,123,.48) !important;
            transform: rotateX(68deg) rotate(35deg) !important;
            animation: tribalOrbitTwo 10s linear infinite !important;
        }
        .tribal-orb-caption {
            color: #1D6038;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .20em;
            text-transform: uppercase;
            margin-bottom: 10px;
            animation: tribalFadeUp .8s ease both;
        }
        .tribal-orb-title {
            color: #183B28;
            font-size: clamp(1.55rem,3vw,2.15rem);
            line-height: 1.2;
            font-weight: 750;
            letter-spacing: -.035em;
            margin: 0;
            animation: tribalFadeUp .9s .12s ease both;
        }
        .tribal-orb-subtitle {
            color: #647568;
            font-size: .94rem;
            margin-top: 10px;
            animation: tribalFadeUp 1s .22s ease both;
        }
        .tribal-orb-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            margin-top: 18px;
            border: 1px solid #DDEDE1;
            border-radius: 999px;
            background: rgba(255,255,255,.9);
            color: #467155;
            font-size: .76rem;
            box-shadow: 0 5px 16px rgba(30,92,49,.055);
            animation: tribalFadeUp 1s .32s ease both;
        }
        .tribal-orb-status i {
            width: 7px;height: 7px;border-radius:50%;
            background:#27AD5B;box-shadow:0 0 0 4px rgba(39,173,91,.12),0 0 12px #53D981;
            animation: tribalStatusPulse 1.8s ease-in-out infinite;
        }
        .tribal-particle {
            position:absolute;
            width:6px;height:6px;border-radius:50%;
            background:radial-gradient(circle,#C9FFD7,#42C875 65%,transparent 75%);
            box-shadow:0 0 12px rgba(47,190,99,.48);
            pointer-events:none;
            animation: tribalParticleFloat 6s ease-in-out infinite;
        }
        .tribal-particle.p1{top:22%;left:25%;animation-delay:-1s}
        .tribal-particle.p2{top:34%;right:24%;width:4px;height:4px;animation-delay:-3s}
        .tribal-particle.p3{bottom:24%;left:34%;width:5px;height:5px;animation-delay:-2s}
        .tribal-particle.p4{bottom:30%;right:31%;width:3px;height:3px;animation-delay:-4s}
        @keyframes tribalHaloDrift{from{transform:translate(-16px,-8px) scale(.94)}to{transform:translate(18px,12px) scale(1.08)}}
        @keyframes tribalOrbitOne{from{transform:rotateX(68deg) rotate(0deg)}to{transform:rotateX(68deg) rotate(360deg)}}
        @keyframes tribalOrbitTwo{from{transform:rotateX(68deg) rotate(360deg)}to{transform:rotateX(68deg) rotate(0deg)}}
        @keyframes tribalOrbTilt{0%,100%{rotate:-5deg}50%{rotate:5deg}}
        @keyframes tribalFadeUp{from{opacity:0;transform:translateY(13px)}to{opacity:1;transform:translateY(0)}}
        @keyframes tribalStatusPulse{0%,100%{box-shadow:0 0 0 3px rgba(39,173,91,.10),0 0 8px #53D981}50%{box-shadow:0 0 0 7px rgba(39,173,91,.04),0 0 16px #53D981}}
        @keyframes tribalParticleFloat{0%,100%{transform:translate3d(0,0,0);opacity:.35}50%{transform:translate3d(12px,-24px,0);opacity:1}}

        /* Reduced motion preference remains respected */
        @keyframes tribalOrbFloat {
            0%,100% { transform: translateY(0) rotate(-4deg); }
            50% { transform: translateY(-11px) rotate(5deg); }
        }
        @keyframes tribalOrbSpark {
            0%,100% { transform: scale(.86) rotate(-8deg); opacity:.75; }
            50% { transform: scale(1.12) rotate(12deg); opacity:1; }
        }
        @keyframes tribalRingSpin {
            from { rotate: 0deg; }
            to { rotate: 360deg; }
        }
        @keyframes tribalAmbientFloat {
            from { transform: translate(-20px,-10px) scale(.9); }
            to { transform: translate(-90px,80px) scale(1.2); }
        }
        @keyframes tribalWelcomeIn {
            from { opacity:0; transform:translateY(15px); }
            to { opacity:1; transform:translateY(0); }
        }
        @keyframes tribalMessageIn {
            from { opacity:0; transform:translateY(9px); }
            to { opacity:1; transform:translateY(0); }
        }
        @keyframes tribalDotBounce {
            0%,60%,100% { transform:translateY(0); opacity:.55; }
            30% { transform:translateY(-5px); opacity:1; }
        }
        @media (prefers-reduced-motion: reduce) {
            .tribal-ai-orb, .tribal-orb-ring::before, .tribal-orb-ring::after,
            .tribal-ai-orb::after, .tribal-typing span,
            [data-testid="stChatMessage"], .tribal-welcome {
                animation: none !important;
                transition: none !important;
            }
        }


        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stHeader"] {
            background: #FFFFFF !important;
            background-image: none !important;
            color: #202B24 !important;
        }

</style>
        """,
        unsafe_allow_html=True
    )

    # Theme-aware overrides must follow the shared base styles above.
    if st.session_state.get("theme", "Light") == "Dark":
        st.markdown(
            """
            <style>
            :root { color-scheme: dark; }
            [data-testid="stAppViewContainer"],
            [data-testid="stMain"],
            [data-testid="stMainBlockContainer"],
            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stDecoration"] {
                background-color: #101714 !important;
                color: #e8f1eb !important;
            }
            [data-testid="stAppViewContainer"] {
                background-image:
                    radial-gradient(ellipse at 8% 0%, rgba(38,92,55,.18), transparent 36%),
                    radial-gradient(ellipse at 95% 10%, rgba(35,78,49,.14), transparent 32%) !important;
            }
            .tribal-welcome {
                background: linear-gradient(135deg,#17251d 0%,#121b16 78%) !important;
                border-color: #2d4034 !important;
            }
            .tribal-eyebrow,.tribal-starters-label,.chat-toolbar-label { color:#a9c4b1 !important; }
            .tribal-welcome h2,.tribal-welcome p { color:#e5efe8 !important; }
            div[data-testid="stButton"] button[kind="secondary"],
            div[data-testid="stDownloadButton"] > button {
                background:#17211c !important; border-color:#365041 !important; color:#dce9df !important;
            }
            div[data-testid="stButton"] button[kind="secondary"]:hover,
            div[data-testid="stDownloadButton"] > button:hover {
                background:#203328 !important; border-color:#54755f !important; color:#fff !important;
            }
            [data-testid="stChatInput"],
            [data-testid="stChatInput"] > div {
                background:#17211c !important; border-color:#365041 !important;
            }
            [data-testid="stChatInput"] textarea { background:#17211c !important; color:#e8f1eb !important; }
            [data-testid="stChatInput"] textarea::placeholder { color:#82958a !important; }
            [data-testid="stPopoverBody"] { background:#17211c !important; border-color:#365041 !important; }
            [data-testid="stPopoverBody"] * { color:#e2ece5 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<style>:root { color-scheme: light; }</style>", unsafe_allow_html=True)


def show_chat_box():
    apply_chat_box_ui()
    if "language" not in st.session_state:
        st.session_state.language = "english"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""

    # Minimal animated empty state: no welcome banner or starter prompt cards.
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="tribal-empty-stage">
                <span class="tribal-particle p1"></span>
                <span class="tribal-particle p2"></span>
                <span class="tribal-particle p3"></span>
                <span class="tribal-particle p4"></span>
                <div class="tribal-orb-ring"><div class="tribal-ai-orb"></div></div>
                <div class="tribal-orb-caption">TRIBAL AI · INTELLIGENT · MULTILINGUAL</div>
                <h2 class="tribal-orb-title">What would you like to explore?</h2>
                <div class="tribal-orb-subtitle">Ask a question and let's learn something together.</div>
                <div class="tribal-orb-status"><i></i> AI assistant ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
        if role == "user":
            content = _clean_stored_user_message(content)
        language = message.get("language")
        detected_language = message.get("detected_language")
        sources = message.get("sources")
        timestamp = message.get("timestamp")
        images = message.get("images", [])
        preceding_question = ""
        if role == "assistant":
            for previous in reversed(st.session_state.messages[:index]):
                if previous.get("role") == "user":
                    preceding_question = _clean_stored_user_message(
                        previous.get("content", "")
                    )
                    break
        render_message(
            role=role,
            content=content,
            language=language,
            detected_language=detected_language,
            sources=sources,
            timestamp=timestamp,
            show_sources=_should_show_official_sources(preceding_question)
        )
        if role == "assistant":
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
        st.caption(
            "Reply language: Santali (Ol Chiki). Type your question in English or Ol Chiki; answers are returned in Santali.")
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
