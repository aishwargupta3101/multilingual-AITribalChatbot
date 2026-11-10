import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
GENERATE_URL = f"{BACKEND_URL}/api/v1/presentations/generate"



def _generate(topic, slide_count, source_text):
    payload = {
        "topic": topic.strip(),
        "slide_count": int(slide_count),
        "source_text": source_text.strip(),
    }
    try:
        with st.spinner("Generating your presentation…"):
            response = requests.post(GENERATE_URL, json=payload, timeout=(15, 300))
        if response.status_code != 200:
            detail = response.text
            try:
                error_data = response.json()
                detail = error_data.get("detail", detail)
            except ValueError:
                pass
            st.error(f"Presentation generation failed: {detail}")
            return
        content_type = response.headers.get("content-type", "")
        if "presentation" not in content_type and not response.content:
            st.error("The backend returned an empty presentation.")
            return
        st.success("Your PowerPoint is ready.")
        st.download_button(
            label="⬇️ Download presentation (.pptx)",
            data=response.content,
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
    except requests.exceptions.Timeout:
        st.error("The request timed out. Try fewer slides or shorter source material.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend. Make sure FastAPI is running and BACKEND_URL points to it.")
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")


def _shared_css():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #f1faf5; }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        background: transparent !important;
    }
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] { background: transparent !important; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px; }
    .pres-hero {
        border: 1px solid #d5eadc; border-radius: 24px; padding: 1.6rem 1.8rem;
        background: linear-gradient(120deg, #ffffff 0%, #e6f6ed 100%);
        box-shadow: 0 8px 28px rgba(34, 93, 60, .06); margin-bottom: 1.2rem;
    }
    .pres-eyebrow { color: #278354; text-transform: uppercase; letter-spacing: .13em;
        font-size: .72rem; font-weight: 800; margin-bottom: .45rem; }
    .pres-hero h1 { color: #173d2b; margin: 0; font-size: clamp(1.8rem, 4vw, 2.65rem); }
    .pres-hero p { color: #557263; margin: .55rem 0 0; max-width: 760px; }
    [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #d7e9de !important; border-radius: 18px !important;
    }
    [data-testid="stFileUploader"], textarea, input { border-radius: 12px !important; }
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
        background: #fff !important; border-color: #d3e6da !important;
    }
    div[data-testid="stSlider"] [role="slider"] { accent-color: #278354; }
    div.stButton > button, div.stFormSubmitButton > button {
        border-radius: 12px; font-weight: 700; min-height: 2.8rem;
    }
    .pres-note { color: #5b7667; font-size: .9rem; }
    </style>
    """, unsafe_allow_html=True)


def show_presentation_generator_page():
    _shared_css()
    st.markdown("""
    <div class="pres-hero">
      <div class="pres-eyebrow">Tribal AI · Quick start</div>
      <h1>📊 Create a presentation</h1>
      <p>Start with a clear topic. Add source notes when you want the slides grounded in your material.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("presentation_generator_form"):
        left, right = st.columns([1.25, 1])
        with left:
            st.subheader("Your content")
            topic = st.text_input("Topic", max_chars=500, placeholder="e.g., Generative AI in education")
            source_text = st.text_area("Source material (optional)", max_chars=12000, height=260,
                placeholder="Paste notes, an outline, or relevant text.")
        with right:
            st.subheader("Presentation settings")
            slide_count = st.slider("Slides", 3, 15, 8)
            st.markdown(f"""
            <div style="background:#e7f5ec;border:1px solid #d0e7d9;border-radius:16px;padding:1rem;margin-top:.6rem">
              <div style="font-size:.75rem;color:#47745b;font-weight:700;text-transform:uppercase">Output</div>
              <div style="font-size:1.35rem;font-weight:800;color:#1b5437">{slide_count} slides</div>
              <div style="color:#5b7667;font-size:.88rem">Editable PowerPoint (.pptx)</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            submitted = st.form_submit_button("✨ Generate PowerPoint", type="primary", use_container_width=True)
    if submitted:
        if len(topic.strip()) < 3:
            st.warning("Please enter a topic with at least 3 characters.")
            return
        _generate(topic, slide_count, source_text)
