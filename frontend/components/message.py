import streamlit as st
def render_message(
    role: str,
    content: str,
    language: str = None,
    detected_language: str = None,
    sources: list = None,
    timestamp: str = None
):
    """
    Render a chat message with optional metadata.
    """
    with st.chat_message(role):
        st.markdown(content)
        if language:
            st.caption(
                f"🌍 Response Language: {language.title()}"
            )
        if detected_language:
            st.caption(
                f"📝 Detected Language: {detected_language.title()}"
            )
        if sources:
            with st.expander("📚 Sources"):
                for source in sources:
                    st.write(
                        f"📄 {source.get('document','Unknown')} "
                        f"(Page {source.get('page','-')})"
                    )
        if timestamp:
            st.caption(f"🕒 {timestamp}")