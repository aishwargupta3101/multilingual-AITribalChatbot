import streamlit as st
def html_block(html):
    """
    Render HTML safely in Streamlit.

    Converts multiline HTML into a single line so that
    Streamlit does not interpret the HTML as a code block.
    """
    html = " ".join(
        line.strip()
        for line in html.splitlines()
        if line.strip()
    )
    st.markdown(
        html,
        unsafe_allow_html=True
    )

def feature_card(
    number,
    icon,
    title,
    description
):
    html_block(
        f"""
        <div class="feature-card">
            <div class="card-number">{number}</div>
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-text">{description}</div>
            <div class="card-arrow">→</div>
        </div>
        """
    )

def show_home():
    language = st.session_state.get(
        "language",
        "english"
    )
    language_name = (
        language
        .replace("_", " ")
        .title()
    )
    html_block(
        f"""
        <div class="hero-section">
            <div class="hero-glow hero-glow-one"></div>
            <div class="hero-glow hero-glow-two"></div>
            <div class="hero-badge">
                🌿 &nbsp; INTELLIGENT • MULTILINGUAL • CULTURAL
            </div>
            <div class="hero-title">
                Explore Knowledge.<br>
                <span>Preserve Culture.</span>
            </div
            <div class="hero-description">
                A multilingual AI assistant designed to connect
                people with tribal knowledge, culture, languages,
                traditions and modern information.
            </div>
            <div class="hero-language">
                🌐 &nbsp; {language_name} Mode
            </div>
        </div>
        """
    )
    html_block(
        """
        <div class="section-heading">
            <div class="section-eyebrow">
                WHAT YOU CAN DO
            </div>
            <div class="section-title">
                One assistant. Many possibilities.
            </div>
            <div class="section-description">
                Explore knowledge, ask questions, work with documents
                and communicate naturally with Tribal AI.
            </div>

        </div>
        """
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        feature_card(
            "01",
            "🌿",
            "Explore Knowledge",
            "Discover tribal culture, traditions, languages "
            "and community knowledge."
        )
    with col2:
        feature_card(
            "02",
            "💬",
            "Ask Anything",
            "Ask questions naturally and receive clear "
            "AI-powered answers."
        )
    with col3:
        feature_card(
            "03",
            "🎤",
            "Use Your Voice",
            "Speak naturally using voice interaction "
            "with the AI assistant."
        )
    col4, col5, col6 = st.columns(3)
    with col4:
        feature_card(
            "04",
            "📄",
            "Upload Documents",
            "Add your own knowledge documents and use "
            "them during conversations."
        )
    with col5:
        feature_card(
            "05",
            "🌐",
            "Multiple Languages",
            "Switch between supported languages while "
            "keeping the conversation natural."
        )
    with col6:
        feature_card(
            "06",
            "🖼️",
            "Visual Discovery",
            "Find relevant images to better understand "
            "places, people, culture and topics."
        )
    html_block(
        """
        <div class="home-cta">
            <div class="home-cta-icon">
                🌱
            </div>
            <div class="home-cta-content">
                <div class="home-cta-title">
                    Ready to explore?
                </div>
                <div class="home-cta-text">
                    Start a conversation and discover
                    knowledge with Tribal AI.
                </div>
            </div>
            <div class="home-cta-arrow">
                →
            </div>
        </div>
        """
    )
    html_block(
        """
        <div class="home-footer">
            <div>
                🌿 Tribal AI
            </div>
            <div>
                Preserving Knowledge • Connecting Cultures
            </div>
            <div>
                v1.0.0
            </div>
        </div>
        """
    )