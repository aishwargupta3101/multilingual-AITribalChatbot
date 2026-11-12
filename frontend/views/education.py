import requests
import streamlit as st

from api.endpoints import (
    BASE_URL,
    EDUCATION_UPLOAD_ENDPOINT,
    EDUCATION_LESSON_ENDPOINT,
    EDUCATION_ASSESSMENT_ENDPOINT,
)
from dotenv import load_dotenv
load_dotenv()

def _extract_text(payload):
    if not isinstance(payload, dict):
        return ""

    for key in ("extracted_text", "text", "full_text", "content"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value

    for key in ("data", "result", "extraction"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            text = _extract_text(nested)
            if text:
                return text

    pages = payload.get("pages")
    if isinstance(pages, list):
        chunks = []
        for page in pages:
            if isinstance(page, dict):
                text = page.get("text") or page.get("content") or ""
                if text:
                    chunks.append(str(text))
            elif isinstance(page, str):
                chunks.append(page)
        return "\n\n".join(chunks)

    return ""


def _post_json(endpoint, body):
    response = requests.post(
        f"{BASE_URL.rstrip('/')}{endpoint}",
        json=body,
        timeout=300,
    )
    response.raise_for_status()
    return response.json()


def _inject_education_css():
    st.markdown(
        """
        <style>
        /* Shared light mint workspace theme */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background: #eef8f3 !important;
            color: #18352a !important;
        }
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            background: #eef8f3 !important;
            color: #18352a !important;
        }
        [data-testid="stHeader"] { border-bottom: 1px solid rgba(48, 112, 78, .10); }
        [data-testid="stMainBlockContainer"] { padding-top: 2rem; }
        .edu-hero {
            padding: 1.55rem 1.8rem;
            border: 1px solid rgba(90, 190, 130, .25);
            border-radius: 22px;
            background: linear-gradient(125deg, #ffffff 0%, #e2f4e9 100%);
            margin-bottom: 1.2rem;
        }
        .edu-eyebrow {
            text-transform: uppercase;
            letter-spacing: .12em;
            font-size: .72rem;
            font-weight: 700;
            color: #26784d;
            margin-bottom: .45rem;
        }
        .edu-hero h1 {
            margin: 0;
            font-size: clamp(1.8rem, 4vw, 2.7rem);
            line-height: 1.15;
        }
        .edu-hero p {
            color: #4d685a;
            margin: .65rem 0 0;
            max-width: 760px;
        }
        .edu-step {
            border: 1px solid rgba(63, 126, 91, .20);
            border-radius: 14px;
            padding: .9rem 1rem;
            background: rgba(255, 255, 255, .72);
            min-height: 84px;
        }
        .edu-step strong { display: block; margin-bottom: .25rem; }
        .edu-step span { color: #5d7567; font-size: .85rem; }
        div[data-testid="stFileUploader"] {
            border: 1px dashed rgba(53, 145, 91, .48);
            border-radius: 16px;
            padding: .6rem;
            background: rgba(255, 255, 255, .78);
        }
        div[data-testid="stTabs"] button { font-weight: 600; color: #28523d !important; }
        div[data-testid="stFileUploader"] section { background: transparent !important; }
        div[data-testid="stForm"] { background: rgba(255, 255, 255, .58); border-radius: 18px; }
        div[data-testid="stMetric"] { background: rgba(255, 255, 255, .72); border: 1px solid rgba(63, 126, 91, .16); padding: .8rem; border-radius: 14px; }
        .edu-muted { color: #5d7567; font-size: .88rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _show_education_generation_page():
    _inject_education_css()

    st.markdown(
        """
        <div class="edu-hero">
            <div class="edu-eyebrow">Tribal AI · Learning Studio</div>
            <h1>🎓 Tribal Education Assistant</h1>
            <p>Turn textbook chapters into accessible lessons, quizzes, and worksheets.
            Upload a PDF, choose your class and language, then generate learning materials.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    step1, step2, step3 = st.columns(3)
    with step1:
        st.markdown(
            '<div class="edu-step"><strong>① Upload a chapter</strong><span>PDF textbook or learning material</span></div>',
            unsafe_allow_html=True,
        )
    with step2:
        st.markdown(
            '<div class="edu-step"><strong>② Customize learning</strong><span>Grade, subject, language, objectives</span></div>',
            unsafe_allow_html=True,
        )
    with step3:
        st.markdown(
            '<div class="edu-step"><strong>③ Generate resources</strong><span>Lesson, quiz, and worksheet</span></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    with st.container(border=True):
        st.subheader("Build learning resources")
        st.caption("Choose the source PDF and set the learning level.")

        with st.form("education_generation_form", clear_on_submit=False):
            pdf = st.file_uploader(
                "Textbook PDF",
                type=["pdf"],
                accept_multiple_files=False,
                help="Use a text-based PDF for best extraction results.",
            )

            col1, col2, col3 = st.columns([1, 1, 1.2])
            with col1:
                grade = st.selectbox(
                    "Grade",
                    [str(n) for n in range(1, 13)],
                    index=5,
                )
            with col2:
                subject = st.selectbox(
                    "Subject",
                    ["English", "Science", "Mathematics", "Social Studies", "Environmental Studies", "Other"],
                    index=0,
                )
            with col3:
                language_labels = {
                    "english": "English",
                    "hindi": "Hindi",
                    "assamese": "Assamese",
                    "bengali": "Bengali",
                    "bodo": "Bodo",
                    "dogri": "Dogri",
                    "gujarati": "Gujarati",
                    "kannada": "Kannada",
                    "kashmiri": "Kashmiri (Perso-Arabic)",
                    "kashmiri_deva": "Kashmiri (Devanagari)",
                    "konkani": "Konkani",
                    "maithili": "Maithili",
                    "malayalam": "Malayalam",
                    "marathi": "Marathi",
                    "nepali": "Nepali",
                    "odia": "Odia",
                    "punjabi": "Punjabi",
                    "sanskrit": "Sanskrit",
                    "santali": "Santali (Ol Chiki)",
                    "sindhi": "Sindhi (Arabic script)",
                    "sindhi_deva": "Sindhi (Devanagari)",
                    "tamil": "Tamil",
                    "telugu": "Telugu",
                    "urdu": "Urdu",
                    "manipuri": "Manipuri (Bengali script)",
                    "manipuri_mtei": "Manipuri (Meitei Mayek)",
                }
                language = st.selectbox(
                    "Output language",
                    options=list(language_labels.keys()),
                    format_func=lambda code: language_labels[code],
                    index=0,
                    help="Languages and scripts registered in the project's translation service.",
                )

            col4, col5 = st.columns([1, 2])
            with col4:
                question_count = st.slider(
                    "Quiz questions",
                    min_value=5,
                    max_value=20,
                    value=10,
                )
            with col5:
                objectives = st.text_input(
                    "Learning objectives (optional)",
                    placeholder="e.g. Explain the story's main idea and vocabulary",
                )

            submitted = st.form_submit_button(
                "✨ Generate lesson, quiz & worksheet",
                type="primary",
                width="stretch",
            )

    if not submitted:
        if "education_result" in st.session_state:
            _render_results(st.session_state.education_result)
        return

    if pdf is None:
        st.warning("Upload a textbook PDF to continue.")
        return

    uploaded_bytes = pdf.getvalue()
    if not uploaded_bytes:
        st.error("The selected PDF is empty.")
        return

    try:
        with st.status("Preparing your learning materials…", expanded=True) as status:
            st.write("Extracting text from the PDF")
            upload_response = requests.post(
                f"{BASE_URL.rstrip('/')}{EDUCATION_UPLOAD_ENDPOINT}",
                files={"file": (pdf.name, uploaded_bytes, "application/pdf")},
                timeout=180,
            )
            upload_response.raise_for_status()
            extraction_payload = upload_response.json()

            extracted_text = _extract_text(extraction_payload)
            if len(extracted_text.strip()) < 50:
                status.update(label="Could not extract enough text", state="error")
                st.error("The PDF response did not contain enough extracted text.")
                with st.expander("Show upload response"):
                    st.json(extraction_payload)
                return

            lesson_body = {
                "extracted_text": extracted_text,
                "grade": grade,
                "subject": subject,
                "language": language,
                "learning_objectives": objectives,
            }
            assessment_body = {
                "extracted_text": extracted_text,
                "grade": grade,
                "subject": subject,
                "language": language,
                "question_count": question_count,
            }

            st.write("Generating the lesson")
            lesson_payload = _post_json(EDUCATION_LESSON_ENDPOINT, lesson_body)

            st.write("Creating quiz and worksheet")
            assessment_payload = _post_json(EDUCATION_ASSESSMENT_ENDPOINT, assessment_body)

            result = {
                "lesson_payload": lesson_payload,
                "assessment_payload": assessment_payload,
                "filename": pdf.name,
                "page_count": extraction_payload.get("page_count"),
                "extracted_text": extracted_text,
                "grade": grade,
                "subject": subject,
                "language": language,
            }
            st.session_state.education_result = result
            status.update(label="Learning materials ready", state="complete")

        _render_results(result)

    except requests.exceptions.HTTPError as exc:
        response = getattr(exc, "response", None)
        detail = ""
        if response is not None:
            try:
                detail = response.json().get("detail", "")
            except ValueError:
                detail = response.text
        st.error(f"Backend request failed: {detail or exc}")
        if response is not None and response.status_code == 429:
            st.info("The provider is rate-limited. Wait briefly and retry; Ollama fallback may handle the request.")
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not connect to the backend. Check BACKEND_URL and FastAPI. Details: {exc}")
    except Exception as exc:
        st.exception(exc)


def _render_results(result):
    lesson_payload = result.get("lesson_payload", {})
    assessment_payload = result.get("assessment_payload", {})
    lesson = lesson_payload.get("lesson", "")
    english_lesson = lesson_payload.get("lesson_english", "")
    assessment = assessment_payload.get("assessment", "")

    st.divider()
    st.subheader("Generated learning materials")
    meta1, meta2, meta3 = st.columns(3)
    meta1.metric("Grade", result.get("grade", "—"))
    meta2.metric("Language", result.get("language", "—"))
    meta3.metric("PDF pages", result.get("page_count") or "—")
    st.caption(f"Source: {result.get('filename', 'Textbook PDF')}")

    lesson_tab, assessment_tab, source_tab = st.tabs(
        ["📘 Lesson", "📝 Quiz & Worksheet", "📄 Source text"]
    )
    with lesson_tab:
        if lesson:
            if english_lesson and str(result.get("language", "")).lower() != "english":
                lesson_view = st.radio(
                    "Lesson display",
                    ["Selected language", "English", "Side by side"],
                    horizontal=True,
                    key="education_lesson_display",
                )
                if lesson_view == "English":
                    st.markdown(english_lesson)
                elif lesson_view == "Side by side":
                    left, right = st.columns(2)
                    with left:
                        st.markdown(f"**{result.get('language', 'Selected language')}**")
                        st.markdown(lesson)
                    with right:
                        st.markdown("**English**")
                        st.markdown(english_lesson)
                else:
                    st.markdown(lesson)
            else:
                st.markdown(lesson)
        else:
            st.warning("No lesson content was returned.")
        if lesson:
            st.download_button(
                "Download lesson",
                data=lesson,
                file_name="lesson.md",
                mime="text/markdown",
            )

    with assessment_tab:
        if assessment:
            quiz_content = assessment_payload.get("quiz", "")
            worksheet_content = assessment_payload.get("worksheet", "")
            if quiz_content and worksheet_content:
                quiz_tab, worksheet_tab = st.tabs(["📝 Quiz & answer key", "📄 Worksheet"])
                with quiz_tab:
                    st.markdown(quiz_content)
                with worksheet_tab:
                    st.markdown(worksheet_content)
            else:
                # Backward-compatible display for older backend responses.
                st.markdown(assessment)

            st.download_button(
                "Download quiz & worksheet",
                data=assessment,
                file_name="quiz_worksheet.md",
                mime="text/markdown",
            )
        else:
            st.warning("No assessment content was returned.")

    with source_tab:
        source = result.get("extracted_text", "")
        st.caption(f"{len(source):,} extracted characters")
        st.text_area("Extracted textbook text", value=source, height=360)
        st.download_button(
            "Download extracted text",
            data=source,
            file_name="extracted_text.txt",
            mime="text/plain",
        )


def _show_text_to_image_generator():
    """Generate educational illustrations from a text prompt using Pollinations."""
    import os
    from urllib.parse import quote

    st.subheader("Generate an image from a prompt")
    st.caption(
        "Describe the educational illustration you need, then download the generated image."
    )

    prompt = st.text_area(
        "Image description",
        placeholder="Example: A clear, colorful Grade 5 science diagram showing the water cycle, with clouds, rain, rivers, and evaporation arrows.",
        height=110,
        key="edu_image_prompt",
    )
    api_key = os.getenv("POLLINATIONS_API_KEY", "").strip()

    if not api_key:
        st.warning(
            "Set POLLINATIONS_API_KEY in your backend environment or .env file. "
            "Get a key from https://enter.pollinations.ai and restart the app."
        )

    if st.button(
        "✨ Generate image",
        type="primary",
        disabled=not prompt.strip() or not api_key,
        width="stretch",
    ):
        try:
            with st.spinner("Generating your image… this may take a little while."):
                endpoint = "https://gen.pollinations.ai/image/" + quote(prompt.strip(), safe="")
                response = requests.get(
                    endpoint,
                    params={"model": "black-forest-labs/flux.1-schnell"},
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=180,
                )
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                if not content_type.startswith("image/"):
                    raise ValueError("The image service did not return an image.")
                st.session_state["edu_generated_image_bytes"] = response.content
                st.session_state["edu_generated_image_type"] = content_type
                st.session_state["edu_generated_image_prompt"] = prompt.strip()
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 402:
                st.warning(
                    "Image generation is currently unavailable because the image provider "
                    "requires payment (HTTP 402). Your lesson, quiz, and worksheet features "
                    "remain available; you can continue without an illustration."
                )
            else:
                st.warning(
                    f"The optional image could not be generated (HTTP {status_code or 'unknown'}). "
                    "You can continue using the Education Assistant without an image."
                )
        except requests.RequestException:
            st.warning(
                "The optional image service could not be reached. "
                "You can continue using the Education Assistant without an image."
            )
        except Exception as exc:
            st.warning(
                f"The optional image could not be generated: {exc}. "
                "You can continue using the Education Assistant without an image."
            )

        image_bytes = st.session_state.get("edu_generated_image_bytes")

        if image_bytes:
            import base64

            image_type = st.session_state.get(
                "edu_generated_image_type", "image/jpeg"
            )
            image_prompt = st.session_state.get(
                "edu_generated_image_prompt", "Generated image"
            )
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            st.markdown(
                f"""
                <div style="text-align:center; margin-top:20px;">
                    <img
                        src="data:{image_type};base64,{encoded_image}"
                        alt="Generated educational image"
                        style="max-width:100%; height:auto; border-radius:12px;"
                    />
                    <p style="color:#5d7567; margin-top:12px;">
                        {image_prompt}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        extension = "png" if "png" in st.session_state.get("edu_generated_image_type", "") else "jpg"
        st.download_button(
            "Download generated image",
            data=image_bytes,
            file_name=f"generated_education_image.{extension}",
            mime=st.session_state.get("edu_generated_image_type", "image/jpeg"),
            width="stretch",
        )


def show_education_page():
    """Education workspace with lesson generation and prompt-based image generation."""
    _inject_education_css()
    generation_tab, create_tab = st.tabs(["📚 Lesson Studio", "✨ Generate Image"])
    with generation_tab:
        _show_education_generation_page()
    with create_tab:
        _show_text_to_image_generator()
