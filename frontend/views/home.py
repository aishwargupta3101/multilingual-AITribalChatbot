import streamlit as st


def _navigate(page: str):
    """Keep the sidebar radio and app page state in sync."""
    st.session_state["main_navigation"] = page
    st.session_state["selected_page"] = page


def _open_chat():
    _navigate("💬 Chat")


def _open_voice():
    _navigate("🎤 Voice")


def _open_documents():
    _navigate("📄 Documents")


def show_home():
    """Dark, green-accented Tribal AI landing page inspired by the supplied reference."""
    language = str(st.session_state.get("language", "english")).replace("_", " ").title()

    st.markdown(
        f"""
        <section class="ta-home-hero">
            <div class="ta-eyebrow"><span class="ta-live-dot"></span> INTELLIGENT&nbsp; · &nbsp;MULTILINGUAL&nbsp; · &nbsp;CULTURAL</div>
            <div class="ta-brand-mark">🌿</div>
            <p class="ta-brand-name">TRIBAL AI</p>
            <h1 class="ta-home-title">How can I help you <span>today?</span></h1>
            <p class="ta-home-subtitle">
                Your multilingual knowledge assistant for community stories, culture,
                traditions, learning, and everyday questions.
            </p>
            <div class="ta-language-pill">🌐 &nbsp; Current language <strong>{language}</strong></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ta-section-label">START EXPLORING</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown(
            """
            <div class="ta-feature-card">
                <div class="ta-feature-icon">▦</div>
                <div class="ta-feature-title">Explore knowledge</div>
                <p class="ta-feature-description">Discover tribal culture, traditions, community stories, and local knowledge.</p>
                <div class="ta-feature-tag">LEARN & DISCOVER</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Explore with Tribal AI  ↗", key="home_chat_button", type="primary",
                  use_container_width=True, on_click=_open_chat)
    with col2:
        st.markdown(
            """
            <div class="ta-feature-card">
                <div class="ta-feature-icon">✳</div>
                <div class="ta-feature-title">Ask a question</div>
                <p class="ta-feature-description">Get helpful answers in your selected language with a simple conversation.</p>
                <div class="ta-feature-tag">CHAT ASSISTANT</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Start a conversation  ↗", key="home_voice_button",
                  use_container_width=True, on_click=_open_chat)
    with col3:
        st.markdown(
            """
            <div class="ta-feature-card">
                <div class="ta-feature-icon">◉</div>
                <div class="ta-feature-title">Use your voice</div>
                <p class="ta-feature-description">Speak naturally and explore voice-based multilingual assistance.</p>
                <div class="ta-feature-tag">VOICE ASSISTANT</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Open voice assistant  ↗", key="home_documents_button",
                  use_container_width=True, on_click=_open_voice)

    st.markdown(
        """
        <div class="ta-home-bottom">
            <div class="ta-bottom-rule"></div>
            <span>🌿 &nbsp; TRIBAL AI</span>
            <span>Preserving knowledge · Connecting cultures</span>
            <span class="ta-bottom-status"><span class="ta-live-dot"></span> SYSTEM READY</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    show_home()
