"""Polished Tribal LearnAI page with downloadable lesson formats."""
import io
import os
import re
from datetime import datetime
import requests
import streamlit as st

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
LESSON_ENDPOINT = f"{BASE_URL}/api/v1/video-learning/lesson"
LANGUAGE_LABELS = {
    "english": "English",
    "hindi": "Hindi",
    "manipuri": "Manipuri (Bengali script)",
    "manipuri_mtei": "Manipuri (Meitei Mayek)",
    "assamese": "Assamese",
    "bengali": "Bengali",
    "bodo": "Bodo",
    "dogri": "Dogri",
    "gujarati": "Gujarati",
    "kannada": "Kannada",
    "kashmiri": "Kashmiri",
    "kashmiri_deva": "Kashmiri (Devanagari)",
    "konkani": "Konkani",
    "maithili": "Maithili",
    "malayalam": "Malayalam",
    "marathi": "Marathi",
    "nepali": "Nepali",
    "odia": "Odia",
    "punjabi": "Punjabi",
    "sanskrit": "Sanskrit",
    "santali": "Santali",
    "sindhi": "Sindhi",
    "sindhi_deva": "Sindhi (Devanagari)",
    "tamil": "Tamil",
    "telugu": "Telugu",
    "urdu": "Urdu",
}
LEVEL_LABELS = {
    "beginner": "Beginner — simple explanations",
    "college": "College — technical detail and examples",
    "advanced": "Advanced — deeper theory",
}


def _plain_text(markdown_text: str) -> str:
    """Make a readable plain-text version for TXT export."""
    text = markdown_text or ""
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text, flags=re.S)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = re.sub(r"[*_~`]+", "", text)
    return text.strip() + "\n"


def _make_docx(markdown_text: str) -> bytes:
    """Create a DOCX with readable headings and paragraphs."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(45, 55, 72)

    in_code = False
    for raw_line in (markdown_text or "").splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not line.strip():
            continue
        if in_code:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif re.match(r"^\s*[-*+]\s+", line):
            doc.add_paragraph(re.sub(r"^\s*[-*+]\s+", "", line), style="List Bullet")
        elif re.match(r"^\s*\d+[.)]\s+", line):
            doc.add_paragraph(re.sub(r"^\s*\d+[.)]\s+", "", line), style="List Number")
        else:
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
            clean = re.sub(r"[*_`]+", "", clean)
            doc.add_paragraph(clean)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _make_pdf(markdown_text: str) -> bytes:
    """Create a clean PDF with ReportLab; retain Unicode where the chosen font supports it."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, HRFlowable
    from xml.sax.saxutils import escape

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm,
        title="Tribal LearnAI — Study Notes", author="Tribal LearnAI",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="LessonTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=colors.HexColor("#174C45"), spaceAfter=14, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="LessonH2", parent=styles["Heading2"], fontSize=14, leading=18, textColor=colors.HexColor("#176B63"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="LessonH3", parent=styles["Heading3"], fontSize=11.5, leading=15, textColor=colors.HexColor("#344054"), spaceBefore=9, spaceAfter=4))
    styles.add(ParagraphStyle(name="LessonBody", parent=styles["BodyText"], fontSize=9.5, leading=14, textColor=colors.HexColor("#303846"), spaceAfter=6, wordWrap="CJK"))
    styles.add(ParagraphStyle(name="LessonCode", parent=styles["Code"], fontName="Courier", fontSize=8, leading=10, backColor=colors.HexColor("#F2F4F7"), borderPadding=6, spaceBefore=4, spaceAfter=8))

    story = []
    in_code = False
    code_lines = []
    for raw_line in (markdown_text or "").splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["LessonCode"]))
                code_lines = []
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            story.append(Spacer(1, 3))
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), styles["LessonTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]), styles["LessonH2"]))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:]), styles["LessonH3"]))
        elif line.strip() in {"---", "***", "___"}:
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#D0D5DD"), spaceBefore=5, spaceAfter=8))
        elif re.match(r"^\s*[-*+]\s+", line):
            item = re.sub(r"^\s*[-*+]\s+", "", line)
            story.append(Paragraph("&#8226;&nbsp; " + escape(re.sub(r"[*_`]+", "", item)), styles["LessonBody"]))
        elif re.match(r"^\s*\d+[.)]\s+", line):
            item = re.sub(r"^\s*\d+[.)]\s+", "", line)
            number = re.match(r"^\s*(\d+)[.)]", line).group(1)
            story.append(Paragraph(f"{number}.&nbsp; " + escape(re.sub(r"[*_`]+", "", item)), styles["LessonBody"]))
        else:
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
            clean = re.sub(r"[*_`]+", "", clean)
            clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", clean)
            story.append(Paragraph(escape(clean), styles["LessonBody"]))
    if in_code and code_lines:
        story.append(Preformatted("\n".join(code_lines), styles["LessonCode"]))
    doc.build(story)
    return buffer.getvalue()


def _inject_styles():
    st.markdown("""
    <style>
    /* Video Learning page: light study-workspace theme, matching Documents. */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] [data-testid="stMain"] {
        background: #F3F8F5 !important;
        color: #173A2B !important;
    }
    /* Streamlit's top header and toolbar have independent theme backgrounds. */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background: #F3F8F5 !important;
        color: #173A2B !important;
    }
    [data-testid="stHeader"] *,
    [data-testid="stToolbar"] *,
    [data-testid="stDecoration"] * {
        color: #173A2B !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMain"] .block-container {
        color: #173A2B !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMain"] h1,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] h2,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] h3,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] h4,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] p,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] label,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] [data-testid="stCaptionContainer"] {
        color: #173A2B;
    }
    .learnai-hero {
        padding: 2rem 2.2rem; border-radius: 24px;
        background: linear-gradient(120deg, #FFFFFF 0%, #E3F5E9 100%);
        border: 1px solid #CBE7D3; margin-bottom: 1.25rem;
        box-shadow: 0 12px 30px rgba(23, 58, 43, .06);
    }
    .learnai-hero h1 {
        color: #173A2B !important; font-size: clamp(1.8rem, 3vw, 2.6rem);
        letter-spacing: -0.035em; line-height: 1.2; margin: 0 0 .65rem 0;
    }
    .learnai-hero p { color: #355B49 !important; font-size: 1rem; line-height: 1.7; margin: 0; }
    [data-testid="stAppViewContainer"] [data-testid="stMain"] input,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] textarea,
    [data-testid="stAppViewContainer"] [data-testid="stMain"] [data-baseweb="select"] > div {
        background: #FFFFFF !important; color: #173A2B !important;
        border-color: #B8DCC5 !important; border-radius: 12px !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMain"] button[kind="primary"] {
        background: #16834A !important; color: #FFFFFF !important;
        border: 1px solid #16834A !important; border-radius: 12px !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMain"] button[kind="secondary"],
    [data-testid="stAppViewContainer"] [data-testid="stMain"] [data-testid="stDownloadButton"] button {
        background: #FFFFFF !important; color: #176B43 !important;
        border: 1px solid #B8DCC5 !important; border-radius: 12px !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMain"] [data-testid="stForm"],
    [data-testid="stAppViewContainer"] [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #CBE7D3 !important; border-radius: 18px !important;
    }
    .learnai-lesson { font-family: Inter, 'Segoe UI', 'Noto Sans', sans-serif; font-size: 1.02rem;
        line-height: 1.85; letter-spacing: .005em; color: #243B2E; }
    .learnai-lesson h1 { color: #173A2B; font-size: 2rem; line-height: 1.3; letter-spacing: -.025em; margin-top: 1.2rem; }
    .learnai-lesson h2 { color: #176B43; font-size: 1.5rem; line-height: 1.4; margin-top: 1.7rem; padding-bottom: .35rem;
        border-bottom: 1px solid #D5E8DA; }
    .learnai-lesson h3 { color: #245A3E; font-size: 1.2rem; line-height: 1.5; margin-top: 1.3rem; }
    .learnai-lesson p, .learnai-lesson li { color: #243B2E; line-height: 1.85; }
    .learnai-lesson li { margin-bottom: .35rem; }
    .learnai-lesson code { border-radius: 5px; padding: .12rem .3rem; }
    .learnai-lesson pre { border-radius: 10px; padding: .9rem; }
    </style>
    """, unsafe_allow_html=True)


def _record_learning_result(result):
    """Keep generated video lessons available to the History page for this session."""
    history = st.session_state.setdefault("learning_history", [])
    video_id = result.get("video_id", "")
    # Avoid duplicate history entries when Streamlit reruns the page.
    if not any(item.get("video_id") == video_id and item.get("lesson") == result.get("lesson") for item in history):
        history.append({
            "kind": "video",
            "title": result.get("title") or f"Video lesson {video_id}" if video_id else "Video lesson",
            "video_id": video_id,
            "video_url": result.get("video_url", ""),
            "language": result.get("language", "english"),
            "lesson": result.get("lesson", ""),
            "created_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        })


def _record_download(filename, file_format):
    """Record an export event in the current session for display in History."""
    downloads = st.session_state.setdefault("download_history", [])
    downloads.append({
        "filename": filename,
        "format": file_format,
        "created_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
    })


def show_video_learning_page():
    _inject_styles()
    st.markdown("""
    <div class="learnai-hero">
      <h1>🎓 Tribal LearnAI</h1>
      <p>Turn a technical video into structured study notes, clear explanations, examples, timestamps, and self-check questions.</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("The lesson is built from available YouTube captions/transcripts. Videos without accessible captions may not work; visual-only details that are not described in speech are not analyzed by this caption-based pipeline.")

    with st.form("video_learning_form"):
        url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")
        left, right = st.columns(2)
        with left:
            level = st.selectbox("Explanation level", options=list(LEVEL_LABELS), format_func=lambda x: LEVEL_LABELS[x])
        with right:
            language = st.selectbox("Lesson language", options=list(LANGUAGE_LABELS), format_func=lambda x: LANGUAGE_LABELS[x])
        submitted = st.form_submit_button("✨ Generate complete lesson", type="primary", use_container_width=True)

    if submitted:
        if not url.strip():
            st.warning("Please paste a YouTube video URL.")
            return
        with st.spinner("Retrieving captions and preparing your lesson. Longer videos may take a few minutes..."):
            try:
                response = requests.post(LESSON_ENDPOINT, json={"url": url.strip(), "level": level, "output_language": language}, timeout=(15, 900))
                if not response.ok:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"Video learning request failed (HTTP {response.status_code}): {detail}")
                    return
                payload = response.json()
                if not payload.get("success") or not payload.get("data"):
                    st.error("The backend returned no lesson. Please try again.")
                    return
                st.session_state.video_learning_result = payload["data"]
            except requests.Timeout:
                st.error("This request took too long. Try a shorter video or try again later.")
                return
            except requests.RequestException as exc:
                st.error(f"Could not reach the backend: {exc}")
                return

    result = st.session_state.get("video_learning_result")
    if not result:
        return
    _record_learning_result(result)

    st.divider()
    st.subheader("📘 Your learning material")
    st.caption(f"Language: {LANGUAGE_LABELS.get(result.get('language', 'english'), result.get('language', 'English'))} · Comprehensive notes from available captions/transcript")
    video_url = result.get("video_url", "")
    if video_url:
        st.markdown(f"[▶ Open original video]({video_url})")

    lesson = str(result.get("lesson", ""))
    with st.container(border=True):
        st.markdown('<div class="learnai-lesson">', unsafe_allow_html=True)
        st.markdown(lesson)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### Download your lesson")
    st.caption("Choose the format that suits your study workflow. The original detailed lesson is preserved in each export.")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("📄 Markdown", data=lesson.encode("utf-8"), file_name="tribal_learnai_lesson.md", mime="text/markdown", use_container_width=True, on_click=_record_download, args=("tribal_learnai_lesson.md", "md"))
    with col2:
        st.download_button("📝 Text (.txt)", data=_plain_text(lesson).encode("utf-8"), file_name="tribal_learnai_lesson.txt", mime="text/plain; charset=utf-8", use_container_width=True, on_click=_record_download, args=("tribal_learnai_lesson.txt", "txt"))
    with col3:
        try:
            docx_data = _make_docx(lesson)
            st.download_button("📘 Word (.docx)", data=docx_data, file_name="tribal_learnai_lesson.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, on_click=_record_download, args=("tribal_learnai_lesson.docx", "docx"))
        except ImportError:
            st.button("📘 Word (.docx)", disabled=True, use_container_width=True, help="Install python-docx in the frontend environment to enable Word export.")
    with col4:
        try:
            pdf_data = _make_pdf(lesson)
            st.download_button("📕 PDF", data=pdf_data, file_name="tribal_learnai_lesson.pdf", mime="application/pdf", use_container_width=True, on_click=_record_download, args=("tribal_learnai_lesson.pdf", "pdf"))
        except ImportError:
            st.button("📕 PDF", disabled=True, use_container_width=True, help="Install reportlab in the frontend environment to enable PDF export.")

