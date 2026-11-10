import html
import streamlit as st

from api.client import APIClient
from api.endpoints import UPLOAD_ENDPOINT

LANGUAGE_OPTIONS = {
    "English": "english",
    "Hindi": "hindi",
    "Manipuri (Bengali script)": "manipuri",
    "Manipuri (Meitei Mayek)": "manipuri_mtei",
    "Assamese": "assamese",
    "Bengali": "bengali",
    "Bodo": "bodo",
    "Dogri": "dogri",
    "Gujarati": "gujarati",
    "Kannada": "kannada",
    "Kashmiri": "kashmiri",
    "Kashmiri (Devanagari)": "kashmiri_deva",
    "Konkani": "konkani",
    "Maithili": "maithili",
    "Malayalam": "malayalam",
    "Marathi": "marathi",
    "Nepali": "nepali",
    "Odia": "odia",
    "Punjabi": "punjabi",
    "Sanskrit": "sanskrit",
    "Santali": "santali",
    "Sindhi": "sindhi",
    "Sindhi (Devanagari)": "sindhi_deva",
    "Tamil": "tamil",
    "Telugu": "telugu",
    "Urdu": "urdu",
}


def _html(content: str) -> None:
    """Render HTML snippets without allowing filenames to inject markup."""
    st.markdown(content, unsafe_allow_html=True)


def _render_document_styles() -> None:
    """High-contrast, theme-aware styles scoped to the document workspace."""
    theme_base = (st.get_option("theme.base") or "dark").lower()
    if theme_base == "light":
        text = "#17231b"
        muted = "#526258"
        border = "#d7e3da"
        panel = "#ffffff"
        panel_soft = "#f3f8f4"
        tab_text = "#24352a"
        upload_text = "#24352a"
    else:
        text = "#f4f8f5"
        muted = "#c0ccc3"
        border = "#34483b"
        panel = "#151d17"
        panel_soft = "#101712"
        tab_text = "#e8f1eb"
        upload_text = "#f4f8f5"

    st.markdown(f"""
    <style>
    /* Document workspace palette: colors are explicit so Streamlit's default
       widget styles cannot turn labels/tabs black on the dark page. */
    .main {{
      --doc-text: {text}; --doc-muted: {muted}; --doc-border: {border};
      --doc-panel: {panel}; --doc-panel-soft: {panel_soft};
      --doc-accent: #28a65b; --doc-accent-bright: #55d982;
    }}
    /* Light workspace canvas and Streamlit chrome, matching the other pages. */
    [data-testid="stAppViewContainer"]:has(.doc-page) {{
      background: linear-gradient(145deg, #f7fbf8 0%, #eef7f1 55%, #e8f4ec 100%) !important;
      background-color: #f7fbf8 !important;
    }}
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stHeader"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stToolbar"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stDecoration"] {{
      background: #f7fbf8 !important;
      color: #17231b !important;
    }}
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stHeader"] {{
      border-bottom: 1px solid #dce7df !important;
    }}
    [data-testid="stAppViewContainer"]:has(.doc-page) .main,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMain"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMainBlockContainer"] {{
      background: transparent !important;
      background-color: transparent !important;
    }}
    /* Change the background only while the document workspace is present.
       Other Streamlit pages keep the application's existing theme. */
    [data-testid="stAppViewContainer"]:has(.doc-page) {{
      background:
        radial-gradient(ellipse at 12% 0%, rgba(34, 197, 94, .12), transparent 38%),
        radial-gradient(ellipse at 92% 18%, rgba(16, 185, 129, .08), transparent 34%),
        linear-gradient(145deg, #07110c 0%, #0b1b12 52%, #0d2117 100%) !important;
      background-color: #09160f !important;
    }}
    [data-testid="stAppViewContainer"]:has(.doc-page) .main,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMain"] {{
      background: transparent !important;
      background-color: transparent !important;
    }}
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMainBlockContainer"] {{
      background: transparent !important;
    }}
    .doc-page {{max-width:1240px;margin:0 auto;}}
    .doc-hero {{position:relative;overflow:hidden;padding:34px 34px;border:1px solid var(--doc-border);
      border-radius:22px;background:radial-gradient(ellipse at top right,rgba(40,166,91,.16),transparent 48%),
      linear-gradient(130deg,var(--doc-panel),var(--doc-panel-soft));margin-bottom:22px;}}
    .doc-eyebrow {{font-size:11px;font-weight:850;letter-spacing:1.8px;text-transform:uppercase;color:var(--doc-accent-bright);}}
    .doc-hero h1 {{font-size:clamp(28px,3vw,40px);line-height:1.12;margin:12px 0 12px;color:var(--doc-text)!important;letter-spacing:-.8px;}}
    .doc-hero p {{font-size:15px;line-height:1.75;color:var(--doc-muted)!important;margin:0;max-width:780px;}}
    .doc-pills {{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;}}
    .doc-pill {{padding:7px 11px;border-radius:999px;border:1px solid var(--doc-border);background:rgba(127,150,133,.08);color:var(--doc-text)!important;font-size:12px;}}
    .doc-section-heading {{color:var(--doc-text)!important;font-size:21px;font-weight:800;margin:8px 0 5px;letter-spacing:-.25px;}}
    .doc-section-sub,.doc-muted {{color:var(--doc-muted)!important;font-size:14px;line-height:1.7;}}
    .doc-section-sub {{margin-bottom:15px;}}
    .doc-panel {{border:1px solid var(--doc-border);background:var(--doc-panel);border-radius:16px;padding:18px;}}
    .doc-file-card {{display:flex;align-items:center;gap:12px;padding:13px 15px;border:1px solid var(--doc-border);border-radius:13px;background:var(--doc-panel);margin:12px 0 15px;}}
    .doc-file-icon {{width:42px;height:42px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:rgba(40,166,91,.16);color:var(--doc-accent-bright);font-size:20px;flex-shrink:0;}}
    .doc-file-name {{font-weight:750;font-size:14px;color:var(--doc-text)!important;overflow-wrap:anywhere;}}
    .doc-file-size {{color:var(--doc-muted)!important;font-size:12px;margin-top:4px;}}
    .doc-callout {{border:1px solid rgba(40,166,91,.32);border-radius:14px;padding:15px 17px;background:rgba(40,166,91,.09);color:var(--doc-text)!important;line-height:1.65;margin:10px 0 16px;}}
    .doc-answer {{border:1px solid var(--doc-border);background:var(--doc-panel);border-radius:14px;padding:15px;margin:8px 0;color:var(--doc-text)!important;}}

    /* Make every native Streamlit label, hint and tab readable. */
    [data-testid="stAppViewContainer"] .main label,
    [data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"],
    [data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"] *,
    [data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"] p,
    [data-testid="stAppViewContainer"] .main [data-testid="stCaptionContainer"],
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] small,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] span,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] p,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] small,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] [data-testid] {{
      color:var(--doc-text)!important; -webkit-text-fill-color:var(--doc-text)!important; opacity:1!important;
    }}
    [data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"] p,
    [data-testid="stAppViewContainer"] .main label p {{
      color:var(--doc-text)!important; -webkit-text-fill-color:var(--doc-text)!important; opacity:1!important;
    }}
    /* Streamlit versions place tab labels in different nested elements.
       Target all of them so inactive tabs never inherit black text. */
    [data-testid="stTabs"] [data-baseweb="tab-list"],
    [data-testid="stTabs"] [role="tablist"] {{
      gap:10px!important; border-bottom:1px solid var(--doc-border)!important;
      flex-wrap:wrap!important; overflow:visible!important;
    }}
    [data-testid="stTabs"] button[role="tab"],
    [data-testid="stTabs"] [data-baseweb="tab"],
    [data-testid="stTabs"] button[data-baseweb="tab"],
    [data-testid="stTabs"] button[role="tab"] *,
    [data-testid="stTabs"] [data-baseweb="tab"] *,
    [data-testid="stTabs"] button[data-baseweb="tab"] * {{
      color:{tab_text}!important; -webkit-text-fill-color:{tab_text}!important;
      opacity:1!important; visibility:visible!important; font-weight:700!important;
    }}
    [data-testid="stTabs"] button[role="tab"],
    [data-testid="stTabs"] [data-baseweb="tab"] {{
      background:var(--doc-panel)!important; border:1px solid var(--doc-border)!important;
      border-radius:12px 12px 0 0!important; padding:10px 14px!important;
      min-height:46px!important; white-space:nowrap!important;
    }}
    [data-testid="stTabs"] button[aria-selected="true"],
    [data-testid="stTabs"] [aria-selected="true"] {{
      background:rgba(40,166,91,.16)!important; border-color:#28a65b!important;
      box-shadow:inset 0 -3px 0 #28a65b!important;
    }}
    [data-testid="stTabs"] button[aria-selected="false"]:hover,
    [data-testid="stTabs"] [aria-selected="false"]:hover {{
      background:rgba(40,166,91,.09)!important; border-color:var(--doc-accent-bright)!important;
    }}
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] > div,
    [data-testid="stAppViewContainer"] .main [data-baseweb="input"] > div {{
      background:var(--doc-panel)!important;border-color:var(--doc-border)!important;color:var(--doc-text)!important;
    }}
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] input,
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] span,
    [data-testid="stAppViewContainer"] .main input,
    [data-testid="stAppViewContainer"] .main textarea {{
      color:var(--doc-text)!important;-webkit-text-fill-color:var(--doc-text)!important;background:var(--doc-panel)!important;
    }}
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] {{
      background:var(--doc-panel-soft)!important;border:1px dashed var(--doc-border)!important;border-radius:15px!important;color:{upload_text}!important;padding:12px!important;
    }}
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] section,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] section > div {{background:transparent!important;color:{upload_text}!important;}}
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploader"] button {{
      background:var(--doc-panel)!important;color:var(--doc-text)!important;border:1px solid var(--doc-border)!important;border-radius:10px!important;
    }}
    [data-testid="stAppViewContainer"] .main .stButton button,
    [data-testid="stAppViewContainer"] .main .stDownloadButton button {{border-radius:11px;min-height:43px;font-weight:700;transition:all .15s ease;}}
    [data-testid="stAppViewContainer"] .main .stButton button[kind="primary"],
    [data-testid="stAppViewContainer"] .main .stDownloadButton button {{background:#218c4d!important;color:#fff!important;border-color:#218c4d!important;}}
    [data-testid="stAppViewContainer"] .main .stButton button:hover,
    [data-testid="stAppViewContainer"] .main .stDownloadButton button:hover {{border-color:#55d982!important;filter:brightness(1.08);}}
    [data-testid="stAppViewContainer"] .main [data-testid="stAlert"] p {{color:inherit!important;}}
    [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] [data-baseweb="tab-list"] {{gap:10px;border-bottom:1px solid var(--doc-border);}}
    @media(max-width:700px) {{.doc-hero{{padding:23px 20px;}}.doc-hero h1{{font-size:29px;}}}}
    /* FINAL VISIBILITY OVERRIDES: target Streamlit/BaseWeb DOM variants. */
    [data-testid="stAppViewContainer"] .main,
    [data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"],
    [data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"] p,
    [data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"] li,
    [data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"],
    [data-testid="stAppViewContainer"] .main [data-testid="stWidgetLabel"] *,
    [data-testid="stAppViewContainer"] .main label,
    [data-testid="stAppViewContainer"] .main label *,
    [data-testid="stAppViewContainer"] .main .stCaption,
    [data-testid="stAppViewContainer"] .main small,
    [data-testid="stAppViewContainer"] .main [data-testid="stCaptionContainer"] * {{
      color: #F4F8F5 !important;
      -webkit-text-fill-color: #F4F8F5 !important;
      opacity: 1 !important;
    }}
    [data-testid="stAppViewContainer"] .main .doc-muted,
    [data-testid="stAppViewContainer"] .main .doc-section-sub,
    [data-testid="stAppViewContainer"] .main .doc-file-size,
    [data-testid="stAppViewContainer"] .main .doc-hero p {{
      color: #D0DDD4 !important;
      -webkit-text-fill-color: #D0DDD4 !important;
    }}
    /* Tabs: explicitly set text on the tab button, its label container and every child. */
    [data-testid="stTabs"] button,
    [data-testid="stTabs"] button *,
    [data-testid="stTabs"] [role="tab"],
    [data-testid="stTabs"] [role="tab"] *,
    [data-testid="stTabs"] [data-baseweb="tab"],
    [data-testid="stTabs"] [data-baseweb="tab"] *,
    [data-testid="stTabs"] [data-testid="stMarkdownContainer"],
    [data-testid="stTabs"] [data-testid="stMarkdownContainer"] * {{
      color: #F4F8F5 !important;
      -webkit-text-fill-color: #F4F8F5 !important;
      opacity: 1 !important;
      visibility: visible !important;
      text-shadow: none !important;
    }}
    [data-testid="stTabs"] button[aria-selected="true"],
    [data-testid="stTabs"] button[aria-selected="true"] * {{
      color: #FFFFFF !important;
      -webkit-text-fill-color: #FFFFFF !important;
    }}
    /* Keep uploader panel and all of its nested text high contrast too. */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section > div,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] * {{
      background-color: #111B14 !important;
      color: #F4F8F5 !important;
      -webkit-text-fill-color: #F4F8F5 !important;
      opacity: 1 !important;
    }}
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {{
      border: 1px dashed #5A7963 !important;
      border-radius: 13px !important;
    }}
    [data-testid="stFileUploader"] button {{
      background: #F4F8F5 !important;
      color: #153321 !important;
      -webkit-text-fill-color: #153321 !important;
      border: 1px solid #B8D0BF !important;
    }}
    [data-testid="stFileUploader"] button * {{
      color: #153321 !important;
      -webkit-text-fill-color: #153321 !important;
    }}
    [data-testid="stAppViewContainer"] .main input,
    [data-testid="stAppViewContainer"] .main textarea,
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] span {{
      color: #F4F8F5 !important;
      -webkit-text-fill-color: #F4F8F5 !important;
      opacity: 1 !important;
    }}

    /* Example-question buttons: high contrast in both themes. */
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button {{
      background: #142c20 !important;
      background-color: #142c20 !important;
      color: #f4f8f5 !important;
      -webkit-text-fill-color: #f4f8f5 !important;
      border: 1px solid #2d6041 !important;
      border-radius: 12px !important;
      min-height: 48px !important;
      text-align: left !important;
      box-shadow: 0 2px 8px rgba(0,0,0,.18) !important;
    }}
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button *,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button *,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button *,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button *,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button * {{
      color: #f4f8f5 !important;
      -webkit-text-fill-color: #f4f8f5 !important;
      opacity: 1 !important;
    }}
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button:hover,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button:hover,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button:hover,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button:hover,
    [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button:hover {{
      background: #1b4530 !important;
      background-color: #1b4530 !important;
      border-color: #55d982 !important;
    }}


    /* FINAL: Streamlit fades disabled buttons and can restore its white
       secondary-button surface. Keep the five sample prompts readable before
       a file is selected, while preserving their disabled behavior. */
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button,
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] [data-testid^="stBaseButton"] {{
      background: #153a28 !important;
      background-color: #153a28 !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      border: 1px solid #36865a !important;
      opacity: 1 !important;
      filter: none !important;
    }}
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button:disabled,
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button[disabled],
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] [data-testid^="stBaseButton"]:disabled {{
      background: #153a28 !important;
      background-color: #153a28 !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      opacity: 1 !important;
      cursor: not-allowed !important;
    }}
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button *,
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button:disabled *,
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] [data-testid^="stBaseButton"] * {{
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      opacity: 1 !important;
    }}
    [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button:not(:disabled):hover {{
      background: #1d5638 !important;
      background-color: #1d5638 !important;
      border-color: #65e795 !important;
    }}

    /* Dropdowns: dark surface with clear selected text and arrow. */
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] > div {{
      background: #151d17 !important;
      border: 1px solid #526b59 !important;
      color: #f4f8f5 !important;
      box-shadow: none !important;
    }}
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] input,
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] span,
    [data-testid="stAppViewContainer"] .main [data-baseweb="select"] svg {{
      color: #f4f8f5 !important;
      fill: #f4f8f5 !important;
      -webkit-text-fill-color: #f4f8f5 !important;
      opacity: 1 !important;
    }}
    [data-testid="stAppViewContainer"] .main [data-baseweb="popover"],
    [data-testid="stAppViewContainer"] .main [role="listbox"],
    [data-testid="stAppViewContainer"] .main [role="option"] {{
      background: #151d17 !important;
      color: #f4f8f5 !important;
    }}
    [data-testid="stAppViewContainer"] .main [role="option"] * {{
      color: #f4f8f5 !important;
      -webkit-text-fill-color: #f4f8f5 !important;
    }}

    /* Primary and disabled buttons must both keep readable labels. */
    [data-testid="stAppViewContainer"] .main .stButton button,
    [data-testid="stAppViewContainer"] .main .stDownloadButton button {{
      border-radius: 11px !important;
      min-height: 43px !important;
      font-weight: 700 !important;
      transition: all .15s ease;
    }}
    [data-testid="stAppViewContainer"] .main .stButton button[kind="primary"],
    [data-testid="stAppViewContainer"] .main .stDownloadButton button {{
      background: #218c4d !important;
      background-color: #218c4d !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      border-color: #218c4d !important;
    }}
    [data-testid="stAppViewContainer"] .main .stButton button:disabled,
    [data-testid="stAppViewContainer"] .main .stButton button[disabled] {{
      background: #26372c !important;
      background-color: #26372c !important;
      color: #e4eee7 !important;
      -webkit-text-fill-color: #e4eee7 !important;
      border: 1px solid #405b48 !important;
      opacity: 1 !important;
      cursor: not-allowed !important;
    }}
    [data-testid="stAppViewContainer"] .main .stButton button:disabled *,
    [data-testid="stAppViewContainer"] .main .stButton button[disabled] * {{
      color: #e4eee7 !important;
      -webkit-text-fill-color: #e4eee7 !important;
      opacity: 1 !important;
    }}
    [data-testid="stAppViewContainer"] .main .stButton button:hover,
    [data-testid="stAppViewContainer"] .main .stDownloadButton button:hover {{
      border-color: #55d982 !important;
      filter: brightness(1.08);
    }}

    /* File uploader: dark panel and readable helper text. */
    [data-testid="stFileUploaderDropzone"] {{
      background: #101b14 !important;
      background-color: #101b14 !important;
      border: 1px dashed #4b7658 !important;
      border-radius: 14px !important;
    }}
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stFileUploaderDropzone"] small {{
      color: #eaf4ed !important;
      -webkit-text-fill-color: #eaf4ed !important;
      opacity: 1 !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
      background: #f4f8f5 !important;
      background-color: #f4f8f5 !important;
      color: #173522 !important;
      -webkit-text-fill-color: #173522 !important;
      border: 1px solid #b8d0bf !important;
    }}
    [data-testid="stFileUploaderDropzone"] button * {{
      color: #173522 !important;
      -webkit-text-fill-color: #173522 !important;
    }}

    /* Student-focused workspace layout */
    .doc-hero-wide {{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(280px,.8fr);gap:26px;align-items:center;min-height:245px;}}
    .doc-hero-copy {{position:relative;z-index:1;}}
    .doc-dot {{color:#55d982!important;}}
    .doc-hero-highlights {{display:flex;flex-direction:column;gap:10px;max-width:360px;justify-self:end;width:100%;}}
    .doc-highlight {{display:flex;align-items:center;gap:13px;padding:13px 16px;border-radius:16px;border:1px solid var(--doc-border);background:rgba(12,35,24,.78);}}
    .doc-highlight>span {{font-size:27px;}}
    .doc-highlight strong {{display:block;color:#f4f8f5!important;font-size:15px;}}
    .doc-highlight small {{display:block;color:#c0d2c6!important;font-size:12px;margin-top:3px;}}
    .doc-highlight.green {{border-color:#176d47;background:rgba(15,100,61,.22);}}
    .doc-highlight.blue {{border-color:#155c91;background:rgba(18,93,151,.19);}}
    .doc-highlight.gold {{border-color:#79611b;background:rgba(121,97,27,.17);}}
    .doc-chat-title {{display:flex;align-items:center;gap:14px;margin:6px 0 18px;}}
    .doc-chat-title .doc-section-heading {{font-size:25px;margin:0 0 4px;}}
    .doc-chat-title .doc-section-sub {{margin:0;}}
    .doc-chat-icon {{display:flex;align-items:center;justify-content:center;width:58px;height:58px;border-radius:15px;background:linear-gradient(135deg,#22d879,#0f9d58);font-size:28px;flex-shrink:0;}}
    .doc-upload-heading {{min-height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border:1px dashed #32875a;border-radius:15px;background:linear-gradient(135deg,rgba(15,91,54,.18),rgba(10,30,20,.55));padding:18px 12px 4px;}}
    .doc-upload-symbol {{font-size:44px;color:#6ee7a0!important;line-height:1.2;}}
    .doc-upload-heading h3 {{color:#f4f8f5!important;font-size:20px;margin:8px 0 4px;}}
    .doc-upload-heading p {{color:#c8d8ce!important;font-size:14px;margin:0 0 12px;}}
    .doc-examples-heading {{color:#f4f8f5!important;font-weight:800;font-size:18px;padding:14px 14px 8px;border:1px solid var(--doc-border);border-bottom:0;border-radius:15px 15px 0 0;background:var(--doc-panel);}}
    [data-testid="stAppViewContainer"] .main [data-testid="stVerticalBlock"] .stButton button {{text-align:left!important;}}
    .doc-first-use {{margin-top:18px;}}
    .doc-benefit-grid {{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:22px;}}
    .doc-benefit {{display:flex;gap:11px;align-items:flex-start;padding:16px 14px;border:1px solid var(--doc-border);border-radius:15px;background:var(--doc-panel);min-height:105px;}}
    .doc-benefit strong {{display:block;color:var(--doc-text)!important;font-size:14px;margin:1px 0 5px;}}
    .doc-benefit p {{color:var(--doc-muted)!important;font-size:12px;line-height:1.5;margin:0;}}
    .benefit-icon {{display:flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:11px;font-size:22px;flex-shrink:0;color:#fff!important;}}
    .benefit-icon.purple {{background:#8b5cf6;}} .benefit-icon.green {{background:#0f9d68;}} .benefit-icon.blue {{background:#0891b2;}} .benefit-icon.pink {{background:#db477e;}}
    .doc-footer {{color:#b8c9be!important;border-top:1px solid var(--doc-border);padding-top:15px;margin-top:25px;font-size:12px;}}
    @media(max-width:850px) {{.doc-hero-wide{{grid-template-columns:1fr;}}.doc-hero-highlights{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));max-width:none;}}.doc-benefit-grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}
    @media(max-width:560px) {{.doc-hero-highlights{{grid-template-columns:1fr;}}.doc-benefit-grid{{grid-template-columns:1fr;}}.doc-chat-title{{align-items:flex-start;}}}}
    </style>
    """, unsafe_allow_html=True)

    # Quick prompts use Streamlit primary buttons (not disabled secondary
    # buttons), so the green surface and white text remain visible in all themes.
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container button[kind="primary"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container [data-testid="stBaseButton-primary"] {
            background: #159957 !important;
            background-color: #159957 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: 1px solid #37c978 !important;
            border-radius: 12px !important;
            min-height: 48px !important;
            opacity: 1 !important;
            box-shadow: 0 3px 10px rgba(0,0,0,.16) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container button[kind="primary"] *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container [data-testid="stBaseButton-primary"] * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container button[kind="primary"]:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container [data-testid="stBaseButton-primary"]:hover {
            background: #087a43 !important;
            background-color: #087a43 !important;
            border-color: #72efa0 !important;
        }

    /* FINAL DOCUMENT CHAT CONTROL FIX:
       Keep the reset action dark-green with readable white text, and prevent
       the native file-picker button from flashing to a white surface on click. */
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat button,
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat button:hover,
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat button:focus,
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat button:active,
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat [data-testid^="stBaseButton"] {
        background: linear-gradient(100deg,#20c978,#0e9c5b) !important;
        background-color: #159e5b !important;
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        border: 1px solid #25c879 !important;
        border-radius: 12px !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat button *,
    [data-testid="stAppViewContainer"] .main .st-key-reset_document_chat [data-testid^="stBaseButton"] * {
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        opacity: 1 !important;
    }
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:focus,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:active,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:focus-visible {
        background: #176b3c !important;
        background-color: #176b3c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #35c978 !important;
        box-shadow: 0 0 0 2px rgba(53,201,120,.18) !important;
        opacity: 1 !important;
        outline: none !important;
    }
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:hover *,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:focus *,
    [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button:active * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # Keep this as a plain string (not an f-string): CSS braces must not be
    # interpreted by Python. Target each quick-question button explicitly so
    # Streamlit's default white secondary-button style cannot override it.
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button {
          background: #142c20 !important;
          background-color: #142c20 !important;
          color: #f4f8f5 !important;
          -webkit-text-fill-color: #f4f8f5 !important;
          border: 1px solid #2d6041 !important;
          border-radius: 12px !important;
          min-height: 48px !important;
          text-align: left !important;
          box-shadow: 0 2px 8px rgba(0,0,0,.18) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button * {
          color: #f4f8f5 !important;
          -webkit-text-fill-color: #f4f8f5 !important;
          opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button:hover {
          background: #1b4530 !important;
          background-color: #1b4530 !important;
          border-color: #55d982 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # Final override: Streamlit may render disabled buttons with its own white
    # surface. These selectors deliberately target the actual BaseWeb buttons.
    st.markdown(
        """
        <style>
        /* Example question buttons, including disabled-before-upload state. */
        [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button,
        [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button:disabled,
        [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] [data-testid^="stBaseButton"] {
          background: #143522 !important;
          background-color: #143522 !important;
          color: #ffffff !important;
          -webkit-text-fill-color: #ffffff !important;
          border: 1px solid #34794d !important;
          border-radius: 12px !important;
          opacity: 1 !important;
          min-height: 48px !important;
          box-shadow: none !important;
        }
        [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button *,
        [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button:disabled * {
          color: #ffffff !important;
          -webkit-text-fill-color: #ffffff !important;
          opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main [class*="st-key-doc_quick_"] button:hover:not(:disabled) {
          background: #1d5734 !important;
          background-color: #1d5734 !important;
          border-color: #6ee79a !important;
        }
        /* Primary actions stay readable when enabled or disabled. */
        [data-testid="stAppViewContainer"] .main button[kind="primary"],
        [data-testid="stAppViewContainer"] .main button[kind="primary"]:disabled,
        [data-testid="stAppViewContainer"] .main [data-testid="stBaseButton-primary"],
        [data-testid="stAppViewContainer"] .main [data-testid="stBaseButton-primary"]:disabled {
          background: #168447 !important;
          background-color: #168447 !important;
          color: #ffffff !important;
          -webkit-text-fill-color: #ffffff !important;
          border: 1px solid #168447 !important;
          opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main button[kind="primary"] *,
        [data-testid="stAppViewContainer"] .main [data-testid="stBaseButton-primary"] * {
          color: #ffffff !important;
          -webkit-text-fill-color: #ffffff !important;
          opacity: 1 !important;
        }
        /* Select controls are white, so their text and arrows must be dark. */
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] > div {
          background: #ffffff !important;
          background-color: #ffffff !important;
          border-color: #b9cbbf !important;
        }
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] input,
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] span,
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] svg {
          color: #183523 !important;
          fill: #183523 !important;
          -webkit-text-fill-color: #183523 !important;
          opacity: 1 !important;
        }
        [data-baseweb="popover"] [role="listbox"],
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="popover"] [role="option"] * {
          background-color: #ffffff !important;
          color: #183523 !important;
          -webkit-text-fill-color: #183523 !important;
          opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # Design 1 finishing layer: polished card surfaces and high-contrast controls.
    # This is a plain CSS string (not an f-string), so CSS braces stay literal.
    st.markdown(
        """
        <style>
        /* Give the document workspace a consistent, premium forest-green look. */
        [data-testid="stAppViewContainer"] .main .doc-hero {
            padding: 30px 32px !important;
            border: 1px solid #24583a !important;
            border-radius: 22px !important;
            background: radial-gradient(circle at 85% 15%, rgba(27,180,100,.17), transparent 34%),
                        linear-gradient(135deg, #0d1b13 0%, #101d16 55%, #09130e 100%) !important;
            box-shadow: 0 14px 36px rgba(0,0,0,.18) !important;
        }
        [data-testid="stAppViewContainer"] .main .doc-section-heading,
        [data-testid="stAppViewContainer"] .main .doc-examples-heading {
            color: #f7fbf8 !important;
            -webkit-text-fill-color: #f7fbf8 !important;
        }
        [data-testid="stAppViewContainer"] .main .doc-section-sub,
        [data-testid="stAppViewContainer"] .main .doc-hero p {
            color: #c9d9ce !important;
            -webkit-text-fill-color: #c9d9ce !important;
        }
        /* Native tabs become three clear navigation cards. */
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] [role="tablist"] {
            gap: 8px !important;
            border-bottom: 1px solid #244b34 !important;
            padding: 5px 0 9px !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] button[role="tab"] {
            background: #101e16 !important;
            border: 1px solid #294b36 !important;
            border-radius: 12px !important;
            padding: 11px 16px !important;
            min-height: 48px !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] button[role="tab"] *,
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] button[role="tab"] {
            color: #eaf4ed !important;
            -webkit-text-fill-color: #eaf4ed !important;
            opacity: 1 !important;
            font-weight: 700 !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] button[aria-selected="true"] {
            background: linear-gradient(135deg,#20c978,#11965a) !important;
            border-color: #35db8b !important;
            box-shadow: 0 5px 16px rgba(24,190,111,.2) !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] button[aria-selected="true"],
        [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] button[aria-selected="true"] * {
            color: #062414 !important;
            -webkit-text-fill-color: #062414 !important;
        }
        /* Upload zone: dark green card; native browse button stays light and readable. */
        [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(145deg,#10271a,#0d1c13) !important;
            border: 1px dashed #3e9a62 !important;
            border-radius: 16px !important;
            min-height: 118px !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzoneInstructions"] * {
            color: #eaf5ee !important;
            -webkit-text-fill-color: #eaf5ee !important;
            opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button {
            background: #eaf8ef !important;
            border: 1px solid #b8dfc5 !important;
            border-radius: 10px !important;
        }
        [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stAppViewContainer"] .main [data-testid="stFileUploaderDropzone"] button * {
            color: #123b24 !important;
            -webkit-text-fill-color: #123b24 !important;
            opacity: 1 !important;
        }
        /* Left upload card and right question card, matching Design 1. */
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel,
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container {
            background: linear-gradient(145deg,rgba(13,39,25,.92),rgba(10,25,17,.96)) !important;
            border: 1px solid #245b3a !important;
            border-radius: 16px !important;
            padding: 16px !important;
            box-shadow: 0 8px 22px rgba(0,0,0,.13) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_examples_container {
            padding-top: 8px !important;
        }
        /* Quick question cards: explicitly cover Streamlit secondary + disabled states. */
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 [data-testid^="stBaseButton"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 [data-testid^="stBaseButton"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 [data-testid^="stBaseButton"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 [data-testid^="stBaseButton"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 [data-testid^="stBaseButton"] {
            background: linear-gradient(110deg,#102b1d,#142f22) !important;
            background-color: #123021 !important;
            color: #f5fff8 !important;
            -webkit-text-fill-color: #f5fff8 !important;
            border: 1px solid #2d7048 !important;
            border-radius: 13px !important;
            min-height: 54px !important;
            opacity: 1 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,.14) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button * {
            color: #f5fff8 !important;
            -webkit-text-fill-color: #f5fff8 !important;
            opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_0 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_1 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_2 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_3 button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_quick_4 button:hover {
            background: #1a5032 !important;
            border-color: #65e79a !important;
            transform: translateY(-1px);
        }
        /* Language selectors: white surface means dark text and dark arrow. */
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] > div {
            background: #f8fcf9 !important;
            border: 1px solid #b8d4c1 !important;
            border-radius: 11px !important;
            min-height: 46px !important;
        }
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] input,
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] span,
        [data-testid="stAppViewContainer"] .main [data-baseweb="select"] svg {
            color: #173b25 !important;
            fill: #173b25 !important;
            -webkit-text-fill-color: #173b25 !important;
            opacity: 1 !important;
        }
        /* Translate/upload primary action, including disabled state. */
        [data-testid="stAppViewContainer"] .main button[kind="primary"],
        [data-testid="stAppViewContainer"] .main button[kind="primary"]:disabled,
        [data-testid="stAppViewContainer"] .main [data-testid="stBaseButton-primary"] {
            background: linear-gradient(100deg,#20c978,#0e9c5b) !important;
            border: 1px solid #25c879 !important;
            border-radius: 12px !important;
            color: #062414 !important;
            -webkit-text-fill-color: #062414 !important;
            opacity: 1 !important;
            min-height: 50px !important;
            font-weight: 800 !important;
        }
        [data-testid="stAppViewContainer"] .main button[kind="primary"] *,
        [data-testid="stAppViewContainer"] .main [data-testid="stBaseButton-primary"] * {
            color: #062414 !important;
            -webkit-text-fill-color: #062414 !important;
            opacity: 1 !important;
        }
        .doc-benefit-grid { margin-top: 22px !important; }
        @media(max-width:760px) {
            [data-testid="stAppViewContainer"] .main .doc-hero {padding:22px 18px !important;}
            [data-testid="stAppViewContainer"] .main [data-testid="stTabs"] [role="tablist"] {flex-wrap:wrap !important;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_upload_success(response) -> None:
    _html(
        """
        <div class="doc-callout">
          <strong style="color:#75e49a;">✓ Upload completed</strong><br>
          Your document was sent to the selected language knowledge base.
        </div>
        """
    )
    if isinstance(response, dict):
        with st.expander("View upload details"):
            st.json(response)


def _render_translation() -> None:
    """Student-friendly translation workspace; keeps the existing translation API."""
    st.markdown(
        """
        <div class="doc-translate-heading">
          <div class="doc-translate-icon">🌐</div>
          <div>
            <div class="doc-section-heading">Translate your document</div>
            <div class="doc-section-sub">
              Convert lecture notes, assignments and study material into your preferred language.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Scoped styles: only affect the translation panel on this page.
    st.markdown("""
    <style>
    .st-key-doc_translation_panel {
        background: linear-gradient(145deg, #0d2117, #10291c);
        border: 1px solid #28583a;
        border-radius: 18px;
        padding: 22px;
        margin: 12px 0 18px 0;
    }
    .st-key-doc_translation_panel [data-testid="stWidgetLabel"] *,
    .st-key-doc_translation_panel label,
    .st-key-doc_translation_panel label p {
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
        opacity: 1 !important;
        font-weight: 650 !important;
    }
    .st-key-doc_translation_panel [data-testid="stFileUploader"] section {
        background: #14291d !important;
        border: 1px dashed #4a8c60 !important;
        border-radius: 14px !important;
    }
    .st-key-doc_translation_panel [data-testid="stFileUploader"] *,
    .st-key-doc_translation_panel [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
        opacity: 1 !important;
    }
    .st-key-doc_translation_panel [data-baseweb="select"] > div {
        background: #f7fbf8 !important;
        border: 1px solid #c8d8cc !important;
        border-radius: 10px !important;
        min-height: 48px !important;
    }
    .st-key-doc_translation_panel [data-baseweb="select"] *,
    .st-key-doc_translation_panel [data-baseweb="select"] input {
        color: #17231b !important;
        -webkit-text-fill-color: #17231b !important;
        opacity: 1 !important;
    }
    .st-key-doc_translation_panel [data-baseweb="select"] svg {
        fill: #245c38 !important;
    }
    .st-key-doc_translation_panel .st-key-translate_complete_document button {
        background: linear-gradient(90deg, #20bd70, #39d98a) !important;
        border: 1px solid #39d98a !important;
        color: #062515 !important;
        -webkit-text-fill-color: #062515 !important;
        font-weight: 800 !important;
        min-height: 48px !important;
        border-radius: 11px !important;
        opacity: 1 !important;
    }
    .st-key-doc_translation_panel .st-key-translate_complete_document button p,
    .st-key-doc_translation_panel .st-key-translate_complete_document button span {
        color: #062515 !important;
        -webkit-text-fill-color: #062515 !important;
        opacity: 1 !important;
    }
    .doc-translate-heading {
        display:flex; align-items:center; gap:14px; margin:8px 0 18px;
    }
    .doc-translate-icon {
        width:54px; height:54px; flex:0 0 54px; display:flex;
        align-items:center; justify-content:center; border-radius:15px;
        background:linear-gradient(135deg,#20bd70,#0d9f60); font-size:25px;
    }
    .doc-translate-panel-title {
        color:#f4fff7!important; font-size:17px; font-weight:800;
        margin:0 0 5px 0;
    }
    .doc-translate-help {
        color:#c4ddcc!important; font-size:13px; margin:0 0 16px 0;
    }

    /* FINAL FIX — translation page only: dark dropzone and readable dropdowns. */
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"],
    div.st-key-doc_translation_panel [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        background: #10251a !important;
        background-color: #10251a !important;
        border: 1px dashed #55a875 !important;
        border-radius: 14px !important;
        color: #f4fff7 !important;
        min-height: 118px !important;
    }
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] > div,
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] section,
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] p,
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] span,
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzoneInstructions"],
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzoneInstructions"] * {
        background: transparent !important;
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
        opacity: 1 !important;
    }
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] button {
        background: #176b3c !important;
        background-color: #176b3c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #45d889 !important;
        border-radius: 10px !important;
    }
    div.st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    /* White select surface requires dark selected text and a dark arrow. */
    div.st-key-doc_translation_panel div[data-baseweb="select"] > div {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: 1px solid #b8d4c1 !important;
        border-radius: 11px !important;
        min-height: 48px !important;
        box-shadow: none !important;
    }
    div.st-key-doc_translation_panel div[data-baseweb="select"] div,
    div.st-key-doc_translation_panel div[data-baseweb="select"] span,
    div.st-key-doc_translation_panel div[data-baseweb="select"] input {
        color: #173b25 !important;
        -webkit-text-fill-color: #173b25 !important;
        opacity: 1 !important;
    }
    div.st-key-doc_translation_panel div[data-baseweb="select"] svg {
        color: #173b25 !important;
        fill: #173b25 !important;
        opacity: 1 !important;
    }
    /* Dropdown menu rendered in a portal outside the translation container. */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li *,
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] [role="option"] * {
        background: #ffffff !important;
        color: #173b25 !important;
        -webkit-text-fill-color: #173b25 !important;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(key="doc_translation_panel"):
        _html(
            '<div class="doc-translate-panel-title">📄 1. Choose your document</div>'
            '<div class="doc-translate-help">PDF, DOCX or TXT · Upload once, then choose the languages.</div>'
        )
        translation_file = st.file_uploader(
            "Choose a document to translate",
            type=["pdf", "docx", "txt"],
            key="document_translation_uploader",
            help="Supported formats: PDF, DOCX, and TXT.",
        )

        if translation_file:
            st.markdown(
                f"""
                <div class="doc-file-card">
                  <div class="doc-file-icon">📄</div>
                  <div>
                    <div class="doc-file-name">{html.escape(translation_file.name)}</div>
                    <div class="doc-file-size">{translation_file.size / 1024:.1f} KB · Ready to translate</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="doc-translate-panel-title" style="margin-top:20px;">🌍 2. Select languages</div>'
            '<div class="doc-translate-help">Choose the language of your original file and the language you want.</div>',
            unsafe_allow_html=True,
        )
        source_col, target_col = st.columns(2, gap="medium")
        with source_col:
            source_label = st.selectbox(
                "Original language",
                list(LANGUAGE_OPTIONS.keys()),
                key="document_translation_source",
            )
        with target_col:
            target_label = st.selectbox(
                "Translate into",
                list(LANGUAGE_OPTIONS.keys()),
                index=1,
                key="document_translation_target",
            )

        if source_label == target_label:
            st.info("Choose different source and target languages to translate the document.")

        translate_clicked = st.button(
            "🌐  Translate my document",
            type="primary",
            use_container_width=True,
            key="translate_complete_document",
        )

        if translate_clicked:
            if translation_file is None:
                st.warning("Please upload a PDF, DOCX, or TXT file first.")
            elif source_label == target_label:
                st.warning("Please choose two different languages.")
            else:
                try:
                    with st.spinner("Translating your document. This may take a little time..."):
                        result = APIClient.translate_document(
                            uploaded_file=translation_file,
                            source_language=LANGUAGE_OPTIONS[source_label],
                            target_language=LANGUAGE_OPTIONS[target_label],
                        )

                    translated_text = result.get("translated_text", "")
                    if result.get("file_bytes"):
                        st.session_state["translated_document_file_bytes"] = result["file_bytes"]
                        st.session_state["translated_document_file_name"] = result["filename"]
                        st.session_state["translated_document_file_type"] = result["content_type"]
                        st.session_state["translated_document_text"] = ""
                        st.session_state.pop("translated_document_name", None)
                        st.success("Translated document is ready to download.")
                    elif not result.get("success") or not translated_text.strip():
                        st.error("Translation failed or returned empty text.")
                    else:
                        st.session_state["translated_document_text"] = translated_text
                        st.session_state["translated_document_name"] = translation_file.name
                        st.session_state["translated_document_language"] = LANGUAGE_OPTIONS[target_label]
                        st.session_state.pop("translated_document_file_bytes", None)
                        st.success("Document translation completed.")
                except Exception as exc:
                    st.error(f"Document translation failed: {exc}")

    if st.session_state.get("translated_document_file_bytes"):
        st.markdown("#### Your translated file")
        st.download_button(
            "⬇  Download translated document",
            data=st.session_state["translated_document_file_bytes"],
            file_name=st.session_state["translated_document_file_name"],
            mime=st.session_state["translated_document_file_type"],
            use_container_width=True,
            key="download_translated_document_file",
        )

    if st.session_state.get("translated_document_text"):
        st.markdown("#### Translation preview")
        st.text_area(
            "Translated text",
            value=st.session_state["translated_document_text"],
            height=320,
            key="translated_document_preview",
        )
        st.download_button(
            "⬇  Download translated text",
            data=st.session_state["translated_document_text"],
            file_name="translated_document.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_translated_document_text",
        )



def _render_matching_document_uploader_style() -> None:
    """Use one clean mint upload surface for document chat and knowledge base."""
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploader"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploader"] {
            background: transparent !important;
            background-color: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 8px 0 2px !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] {
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            min-height: 116px !important;
            padding: 20px 22px !important;
            background: linear-gradient(135deg, #f9fdf9 0%, #edf8f0 100%) !important;
            background-color: #f4fbf6 !important;
            border: 1.5px dashed #79bd91 !important;
            border-radius: 16px !important;
            box-shadow: inset 0 1px 3px rgba(28, 95, 52, .035) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] > div,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] > div,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzoneInstructions"] *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzoneInstructions"] *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] small {
            background: transparent !important;
            background-color: transparent !important;
            color: #365c43 !important;
            -webkit-text-fill-color: #365c43 !important;
            opacity: 1 !important;
            text-shadow: none !important;
            font-size: 13px !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] button {
            background: #176b3c !important;
            background-color: #176b3c !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: 1px solid #176b3c !important;
            border-radius: 10px !important;
            min-height: 42px !important;
            padding: 0 17px !important;
            box-shadow: 0 3px 9px rgba(23, 107, 60, .15) !important;
            opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] button * {
            background: transparent !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
            font-weight: 650 !important;
        }
        @media (max-width: 700px) {
            [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"],
            [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] {
                min-height: 100px !important;
                padding: 14px !important;
                flex-wrap: wrap !important;
            }
        }

        /* Remove inherited dark backgrounds from every uploader child. */
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] * {
            background-color: transparent !important;
            background-image: none !important;
            box-shadow: none !important;
            text-shadow: none !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] button {
            background: #17834b !important;
            background-color: #17834b !important;
            border: 1px solid #17834b !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            box-shadow: 0 3px 10px rgba(23, 131, 75, .16) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] button * {
            background: transparent !important;
            background-color: transparent !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] small *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] small * {
            background: transparent !important;
            background-color: transparent !important;
            color: #365c43 !important;
            -webkit-text-fill-color: #365c43 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _render_knowledge_upload(language: str, language_name: str) -> None:
    st.markdown(
        """
        <div class="doc-translate-heading">
          <div class="doc-translate-icon">📚</div>
          <div>
            <div class="doc-section-heading">Add to the knowledge base</div>
            <div class="doc-section-sub">
              Share trusted material with Tribal AI so it can retrieve relevant information when answering questions.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="doc_knowledge_panel"):
        st.markdown(
            '<div class="doc-workspace-step">📚 1. Choose a knowledge document</div>'
            '<div class="doc-workspace-help">PDF, DOCX or TXT · Select material you are allowed to share. '
            f'The selected knowledge language is <strong>{html.escape(language_name)}</strong>.</div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose a knowledge document",
            type=["pdf", "docx", "txt"],
            key="knowledge_document_uploader",
            help="PDF, DOCX and TXT files are supported.",
        )

        _render_matching_document_uploader_style()

        if uploaded_file:
            st.markdown(
                f"""
                <div class="doc-file-card">
                  <div class="doc-file-icon">📚</div>
                  <div>
                    <div class="doc-file-name">{html.escape(uploaded_file.name)}</div>
                    <div class="doc-file-size">{uploaded_file.size / 1024:.1f} KB · Knowledge base: {html.escape(language_name)}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="doc-workspace-step" style="margin-top:20px;">🌍 2. Confirm destination</div>'
            '<div class="doc-workspace-help">This document will be added to the selected language knowledge base.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="doc-callout"><strong>Destination:</strong> {html.escape(language_name)} knowledge base</div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "⬆  Upload to knowledge base",
            type="primary",
            use_container_width=True,
            key="upload_knowledge_document",
            disabled=uploaded_file is None,
        ):
            try:
                with st.spinner(f"Adding document to the {language_name} knowledge base..."):
                    response = APIClient.upload(
                        UPLOAD_ENDPOINT,
                        uploaded_file,
                        st.session_state.session_id,
                        language,
                    )
                _render_upload_success(response)
            except Exception as error:
                st.error(f"Upload failed: {error}")


def _render_document_chat() -> None:
    """Upload one document and chat with it using its saved document ID."""

    st.markdown("""
    <style>
    .st-key-doc_upload_panel,
    .st-key-doc_knowledge_panel {
        background: linear-gradient(145deg, #0d2117 0%, #10291c 100%) !important;
        border: 1px solid #28583a !important;
        border-radius: 18px !important;
        padding: 22px !important;
        margin: 12px 0 20px !important;
        box-shadow: 0 8px 24px rgba(20, 75, 43, .08) !important;
    }
    .st-key-doc_upload_panel [data-testid="stWidgetLabel"] *,
    .st-key-doc_upload_panel label,
    .st-key-doc_upload_panel label *,
    .st-key-doc_knowledge_panel [data-testid="stWidgetLabel"] *,
    .st-key-doc_knowledge_panel label,
    .st-key-doc_knowledge_panel label * {
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
        opacity: 1 !important;
        font-weight: 650 !important;
    }
    .st-key-doc_upload_panel [data-testid="stFileUploader"],
    .st-key-doc_knowledge_panel [data-testid="stFileUploader"] {
        background: transparent !important;
        border: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"],
    .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #142d1e, #10251a) !important;
        border: 1px dashed #55a875 !important;
        border-radius: 14px !important;
        min-height: 116px !important;
        padding: 18px 20px !important;
    }
    .st-key-doc_upload_panel [data-testid="stFileUploaderDropzoneInstructions"],
    .st-key-doc_upload_panel [data-testid="stFileUploaderDropzoneInstructions"] *,
    .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzoneInstructions"],
    .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzoneInstructions"] * {
        color: #e5f5e9 !important;
        -webkit-text-fill-color: #e5f5e9 !important;
        opacity: 1 !important;
    }
    .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button,
    .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] button {
        background: #176b3c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #45d889 !important;
        border-radius: 10px !important;
        min-height: 42px !important;
    }
    .st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button *,
    .st-key-doc_knowledge_panel [data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .st-key-doc_upload_panel .doc-section-heading,
    .st-key-doc_knowledge_panel .doc-section-heading,
    .st-key-doc_upload_panel .doc-translate-panel-title,
    .st-key-doc_knowledge_panel .doc-translate-panel-title {
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
    }
    .st-key-doc_upload_panel .doc-section-sub,
    .st-key-doc_knowledge_panel .doc-section-sub,
    .st-key-doc_upload_panel .doc-translate-help,
    .st-key-doc_knowledge_panel .doc-translate-help {
        color: #c4ddcc !important;
        -webkit-text-fill-color: #c4ddcc !important;
    }
    .st-key-doc_upload_panel .doc-file-card,
    .st-key-doc_knowledge_panel .doc-file-card {
        background: #173b29 !important;
        border: 1px solid #356c49 !important;
        border-radius: 13px !important;
    }
    .st-key-doc_upload_panel .doc-file-name,
    .st-key-doc_knowledge_panel .doc-file-name {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .st-key-doc_upload_panel .doc-file-size,
    .st-key-doc_knowledge_panel .doc-file-size {
        color: #c5ddcd !important;
        -webkit-text-fill-color: #c5ddcd !important;
    }
    .st-key-doc_upload_panel .st-key-doc_prepare_action button,
    .st-key-doc_upload_panel .st-key-doc_prepare_action button *,
    .st-key-doc_knowledge_panel .st-key-upload_knowledge_document button,
    .st-key-doc_knowledge_panel .st-key-upload_knowledge_document button * {
        background: linear-gradient(90deg, #20bd70, #39d98a) !important;
        color: #062515 !important;
        -webkit-text-fill-color: #062515 !important;
        border: 1px solid #39d98a !important;
        border-radius: 11px !important;
        min-height: 48px !important;
        font-weight: 750 !important;
        opacity: 1 !important;
    }
    .st-key-doc_upload_panel .st-key-doc_prepare_action button:hover,
    .st-key-doc_knowledge_panel .st-key-upload_knowledge_document button:hover {
        filter: brightness(1.06) !important;
        transform: translateY(-1px);
    }
    .doc-workspace-step {
        color: #f4fff7 !important;
        font-size: 16px;
        font-weight: 800;
        margin: 2px 0 5px;
    }
    .doc-workspace-help {
        color: #c4ddcc !important;
        font-size: 13px;
        line-height: 1.6;
        margin: 0 0 14px;
    }
    @media(max-width:700px) {
        .st-key-doc_upload_panel,
        .st-key-doc_knowledge_panel {padding:16px !important;}
    }
    </style>
    """, unsafe_allow_html=True)

    # This CSS is deliberately a normal string (not an f-string), so CSS
    # braces cannot be interpreted as Python expressions.
    st.markdown("""
    <style>
    /* Document-chat layout: full-width sections avoid clipped Streamlit columns. */
    .main .st-key-doc_upload_panel {
        background: linear-gradient(145deg,#0d2117,#12291d) !important;
        border: 1px solid #28583a !important;
        border-radius: 18px !important;
        padding: 20px !important;
    }
    .main [data-testid="stFileUploaderDropzone"] {
        background: #10251a !important;
        border: 1px dashed #4a9b69 !important;
        border-radius: 14px !important;
        min-height: 112px !important;
    }
    .main [data-testid="stFileUploaderDropzone"] * {
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
        opacity: 1 !important;
    }
    .main [data-testid="stFileUploaderDropzone"] button,
    .main [data-testid="stFileUploaderDropzone"] button:hover,
    .main [data-testid="stFileUploaderDropzone"] button:focus,
    .main [data-testid="stFileUploaderDropzone"] button:active {
        background: #176b3c !important;
        background-color: #176b3c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #39c978 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }
    .main [data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .main .st-key-doc_prepare_action button,
    .main .st-key-doc_prepare_action button:hover,
    .main .st-key-doc_prepare_action button:focus,
    .main .st-key-doc_prepare_action button:active,
    .main .st-key-reset_document_chat button,
    .main .st-key-reset_document_chat button:hover,
    .main .st-key-reset_document_chat button:focus,
    .main .st-key-reset_document_chat button:active {
        background: #24c875 !important;
        background-color: #24c875 !important;
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        border: 1px solid #45e092 !important;
        border-radius: 12px !important;
        font-weight: 750 !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }
    .main .st-key-doc_prepare_action button *,
    .main .st-key-reset_document_chat button * {
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        opacity: 1 !important;
    }

    /* Final high-specificity fix: target the keyed widget, not its parent
       container. Streamlit versions differ in their generated button markup. */
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] button,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] [data-testid^="stBaseButton"],
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] button,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] [data-testid^="stBaseButton"] {
        background: #20b96b !important;
        background-color: #20b96b !important;
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        border: 1px solid #55e394 !important;
        border-radius: 12px !important;
        opacity: 1 !important;
        filter: none !important;
        box-shadow: none !important;
        /* Match the typography of the Translate my document button only. */
        font-family: inherit !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        font-style: normal !important;
        line-height: 1.5 !important;
        letter-spacing: normal !important;
        min-height: 48px !important;
    }
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] button *,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] [data-testid^="stBaseButton"] *,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] button *,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] [data-testid^="stBaseButton"] * {
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        opacity: 1 !important;
        visibility: visible !important;
        font-family: inherit !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        font-style: normal !important;
        line-height: 1.5 !important;
        letter-spacing: normal !important;
    }
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] button:hover,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] button:hover {
        background: #35d982 !important;
        background-color: #35d982 !important;
        border-color: #8cf0b5 !important;
    }
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] button:disabled,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] button:disabled {
        background: #24583b !important;
        background-color: #24583b !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-prepare_document_chat"] button:disabled *,
    [data-testid="stAppViewContainer"] .main
    [class*="st-key-reset_document_chat"] button:disabled * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    /* Stable selector: keyed container wraps Streamlit's real button element. */
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action [data-testid="stButton"] button,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action [data-testid="stBaseButton-primary"],
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action button[kind="primary"] {
        background: linear-gradient(90deg,#20bd70,#35d98a) !important;
        background-color: #20bd70 !important;
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        border: 1px solid #55e394 !important;
        border-radius: 12px !important;
        opacity: 1 !important;
        filter: none !important;
        box-shadow: none !important;
        font-family: inherit !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
        min-height: 48px !important;
    }
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action [data-testid="stButton"] button *,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action [data-testid="stBaseButton-primary"] * {
        color: #062414 !important;
        -webkit-text-fill-color: #062414 !important;
        opacity: 1 !important;
        visibility: visible !important;
        font-family: inherit !important;
        font-size: 16px !important;
        font-weight: 400 !important;
    }
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action [data-testid="stButton"] button:hover,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_prepare_action [data-testid="stBaseButton-primary"]:hover {
        background: #42e393 !important;
        background-color: #42e393 !important;
    }
    /* Robust fallback scoped to this document-upload panel. */
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel [data-testid="stButton"] button,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel [data-testid="stButton"] button:hover,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel [data-testid="stButton"] button:focus,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel [data-testid="stButton"] button:active,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel button[kind="primary"] {
        background: #24c875 !important;
        background-color: #24c875 !important;
        color: #082416 !important;
        -webkit-text-fill-color: #082416 !important;
        border: 1px solid #55e394 !important;
        border-radius: 12px !important;
        opacity: 1 !important;
        filter: none !important;
        box-shadow: none !important;
        font-family: inherit !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        font-style: normal !important;
        line-height: 1.5 !important;
        letter-spacing: normal !important;
        min-height: 48px !important;
    }
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel [data-testid="stButton"] button *,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel button[kind="primary"] * {
        color: #082416 !important;
        -webkit-text-fill-color: #082416 !important;
        opacity: 1 !important;
        visibility: visible !important;
        font-family: inherit !important;
        font-size: 16px !important;
        font-weight: 400 !important;
    }
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel [data-testid="stButton"] button:disabled,
    [data-testid="stAppViewContainer"] .main
    .st-key-doc_upload_panel button[kind="primary"]:disabled {
        background: #24c875 !important;
        background-color: #24c875 !important;
        color: #082416 !important;
        -webkit-text-fill-color: #082416 !important;
        opacity: 1 !important;
    }
    .doc-prompt-panel {
        width:100%;box-sizing:border-box;
        background:linear-gradient(145deg,#0d2117,#10291c);
        border:1px solid #28583a;border-radius:18px;padding:20px;
        overflow:hidden;
    }
    .doc-prompt-panel h3 {
        color:#f4fff7!important;font-size:20px;margin:0 0 6px;font-weight:750;
    }
    .doc-prompt-panel .doc-prompt-intro {
        color:#c5ddcd!important;font-size:14px;margin:0 0 16px;line-height:1.5;
    }
    .doc-prompt-grid {
        display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;
    }
    .doc-prompt-card {
        display:flex;align-items:center;gap:12px;min-width:0;
        background:#173b29;border:1px solid #356c49;border-radius:12px;
        padding:14px;box-sizing:border-box;
    }
    .doc-prompt-number {
        display:flex;align-items:center;justify-content:center;flex:0 0 38px;
        width:38px;height:38px;border-radius:10px;background:#205a38;
        color:#b5f5c8!important;font-size:13px;font-weight:800;
    }
    .doc-prompt-copy {min-width:0;overflow-wrap:anywhere;}
    .doc-prompt-copy strong {
        display:block;color:#ffffff!important;font-size:14px;line-height:1.4;
    }
    .doc-prompt-copy small {
        display:block;color:#c5ddcd!important;font-size:12px;line-height:1.4;margin-top:4px;
    }
    .doc-file-card {
        display:flex;align-items:center;gap:12px;background:#173b29;
        border:1px solid #356c49;border-radius:12px;padding:12px 14px;margin-top:12px;
    }
    .doc-file-icon {font-size:24px;}
    .doc-file-name {color:#ffffff!important;font-weight:700;overflow-wrap:anywhere;}
    .doc-file-size {color:#c5ddcd!important;font-size:12px;margin-top:3px;}
    @media(max-width:760px) {
        .doc-prompt-grid {grid-template-columns:minmax(0,1fr);}
    }

    /* FINAL FIX — chat upload dropzone only. */
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] {
        background: #10251a !important;
        background-color: #10251a !important;
        border: 1px dashed #55a875 !important;
        border-radius: 14px !important;
        min-height: 118px !important;
        color: #f4fff7 !important;
    }
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] > div,
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] section,
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] p,
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] span,
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzoneInstructions"],
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzoneInstructions"] * {
        background: transparent !important;
        color: #f4fff7 !important;
        -webkit-text-fill-color: #f4fff7 !important;
        opacity: 1 !important;
    }
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button,
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button:hover,
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button:focus {
        background: #176b3c !important;
        background-color: #176b3c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #45d889 !important;
        border-radius: 10px !important;
        opacity: 1 !important;
    }
    div.st-key-doc_upload_panel [data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Final upload-zone refinement: one compact drop area, no nested dashed boxes.
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploader"] {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 10px 0 4px !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] {
            box-sizing: border-box !important;
            min-height: 112px !important;
            height: auto !important;
            padding: 20px 22px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 18px !important;
            background: linear-gradient(135deg, #f9fdf9 0%, #edf8f0 100%) !important;
            background-color: #f4fbf6 !important;
            border: 1.5px dashed #79bd91 !important;
            border-radius: 16px !important;
            box-shadow: inset 0 1px 3px rgba(28, 95, 52, .035) !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] > div {
            background: transparent !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzoneInstructions"] *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] small {
            color: #365c43 !important;
            -webkit-text-fill-color: #365c43 !important;
            opacity: 1 !important;
            font-size: 13px !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] button:hover,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] button:focus {
            background: #176b3c !important;
            background-color: #176b3c !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: 1px solid #176b3c !important;
            border-radius: 10px !important;
            min-height: 42px !important;
            padding: 0 17px !important;
            box-shadow: 0 3px 9px rgba(23, 107, 60, .15) !important;
            opacity: 1 !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] button *,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] button p,
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stFileUploaderDropzone"] button span {
            background: transparent !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
            font-weight: 650 !important;
        }
        [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
        [data-testid="stWidgetLabel"] p {
            color: #244b32 !important;
            -webkit-text-fill-color: #244b32 !important;
            font-weight: 650 !important;
            font-size: 13px !important;
        }
        @media (max-width: 700px) {
            [data-testid="stAppViewContainer"] .main .st-key-doc_upload_panel
            [data-testid="stFileUploaderDropzone"] {
                min-height: 100px !important;
                padding: 14px !important;
                flex-wrap: wrap !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="doc-chat-title"><span class="doc-chat-icon">💬</span>'
        '<div><div class="doc-section-heading">Chat with your document</div>'
        '<div class="doc-section-sub">Upload a file once, then ask questions about its content. No translation step required.</div></div></div>',
        unsafe_allow_html=True,
    )

    with st.container(key="doc_upload_panel"):
        st.markdown('<div class="doc-workspace-step">📄 1. Choose your document</div>', unsafe_allow_html=True)
        st.markdown('<div class="doc-workspace-help">PDF, DOCX or TXT · Maximum 200 MB · Upload once, then ask questions about its content.</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "txt"],
            key="document_chat_uploader",
            help="Supported formats: PDF, DOCX and TXT.",
        )

        _render_matching_document_uploader_style()

        signature = f"{uploaded.name}:{uploaded.size}" if uploaded else None
        if signature != st.session_state.get("document_chat_file_signature"):
            st.session_state["document_chat_file_signature"] = signature
            st.session_state.pop("document_chat_id", None)
            st.session_state.pop("document_chat_filename", None)
            st.session_state["document_chat_messages"] = []
            st.session_state.pop("document_chat_pending_question", None)

        if uploaded:
            st.markdown(
                f'<div class="doc-file-card"><div class="doc-file-icon">📄</div>'
                f'<div><div class="doc-file-name">{html.escape(uploaded.name)}</div>'
                f'<div class="doc-file-size">{uploaded.size / 1024:.1f} KB</div></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="doc-workspace-step" style="margin-top:20px;">💬 2. Prepare your document chat</div>'
            '<div class="doc-workspace-help">Upload and index the file to enable document-grounded questions.</div>',
            unsafe_allow_html=True,
        )

        session_id = st.session_state.get("session_id")
        if not session_id:
            st.error("Your chat session is not ready. Refresh the page and try again.")
            return

        document_id = st.session_state.get("document_chat_id")
        if uploaded and not document_id:
            with st.container(key="doc_prepare_action"):
                prepare_clicked = st.button(
                    "⬆  Upload and prepare document",
                    type="primary",
                    use_container_width=True,
                    key="prepare_document_chat",
                )
            if prepare_clicked:
                try:
                    uploaded.seek(0)
                    with st.spinner("Uploading and indexing your document..."):
                        response = APIClient.upload(
                            UPLOAD_ENDPOINT,
                            uploaded,
                            session_id,
                            st.session_state.get("language", "english"),
                        )
                    if not isinstance(response, dict):
                        raise RuntimeError("The upload API returned an invalid response.")

                    payload = response.get("data", response)
                    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
                        payload = payload["data"]
                    document_id = payload.get("document_id") if isinstance(payload, dict) else None

                    if response.get("success") is False or not document_id:
                        error = response.get("error") or response.get("detail")
                        if not error and isinstance(payload, dict):
                            error = payload.get("message")
                        st.error(f"Document upload failed: {error or 'The server did not return a document ID.'}")
                    else:
                        st.session_state["document_chat_id"] = str(document_id)
                        st.session_state["document_chat_filename"] = uploaded.name
                        st.session_state["document_chat_messages"] = []
                        st.success("Document uploaded and ready. You can now ask questions.")
                        st.rerun()
                except Exception as exc:
                    st.error(f"Document upload failed: {exc}")
        elif document_id:
            st.success(
                f"Ready to chat: {st.session_state.get('document_chat_filename', uploaded.name if uploaded else 'Document')}"
            )
            if st.button(
                "Remove document and upload another",
                key="reset_document_chat",
                use_container_width=True,
            ):
                st.session_state.pop("document_chat_id", None)
                st.session_state.pop("document_chat_filename", None)
                st.session_state["document_chat_messages"] = []
                st.session_state["document_chat_file_signature"] = None
                st.rerun()

    quick_questions = [
        ("01", "Give me a summary of this document", "Get the main idea in a few clear points."),
        ("02", "What are the key points discussed?", "Find the most important ideas and takeaways."),
        ("03", "Explain this topic in simple words", "Make difficult concepts easier to understand."),
        ("04", "List important definitions from this document", "Collect useful terms and their meanings."),
        ("05", "Create practice questions from this content", "Turn your study material into revision practice."),
    ]
    cards_html = "\n".join(
        f'<div class="doc-prompt-card"><span class="doc-prompt-number">{number}</span>'
        f'<div class="doc-prompt-copy"><strong>{html.escape(title)}</strong>'
        f'<small>{html.escape(description)}</small></div></div>'
        for number, title, description in quick_questions
    )
    st.markdown(
        '<section class="doc-prompt-panel"><h3>💡 Try these example questions</h3>'
        '<p class="doc-prompt-intro">Upload your file, then use one of these ideas as your question.</p>'
        '<div class="doc-prompt-grid">' + cards_html + '</div></section>',
        unsafe_allow_html=True,
    )

    document_id = st.session_state.get("document_chat_id")
    if not document_id:
        _html(
            '<div class="doc-callout doc-first-use"><strong>🎓 Made for students</strong><br>'
            'Upload your lecture notes, textbook chapters or assignments above. '
            'Once processing finishes, you can ask questions and get document-grounded answers.</div>'
        )
        return

    if "document_chat_messages" not in st.session_state:
        st.session_state["document_chat_messages"] = []
    for message in st.session_state["document_chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your document…", key="document_chat_input")
    pending = st.session_state.pop("document_chat_pending_question", None)
    question = question or pending
    if question:
        st.session_state["document_chat_messages"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching your document and preparing an answer..."):
                try:
                    result = APIClient.chat_with_document(
                        document_id=document_id,
                        question=question,
                        session_id=st.session_state.get("session_id"),
                        language=st.session_state.get("language", "english"),
                    )
                    if not isinstance(result, dict):
                        raise RuntimeError("The chat API returned an invalid response.")
                    payload = result.get("data", result)
                    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
                        payload = payload["data"]
                    answer = (
                        (payload.get("answer") or payload.get("response"))
                        if isinstance(payload, dict) else None
                    ) or result.get("detail") or "I couldn't generate an answer from this document."
                    failed = result.get("success") is False or (
                        isinstance(payload, dict) and payload.get("success") is False
                    )
                    if failed:
                        st.error(str(result.get("error") or answer))
                    else:
                        st.markdown(str(answer))
                    st.session_state["document_chat_messages"].append(
                        {"role": "assistant", "content": str(answer)}
                    )
                except Exception as exc:
                    error_message = f"Document chat failed: {exc}"
                    st.error(error_message)
                    st.session_state["document_chat_messages"].append(
                        {"role": "assistant", "content": error_message}
                    )

def show_upload() -> None:
    'Student-friendly document workspace; translation and knowledge upload stay separate.'
    _render_document_styles()
    language = st.session_state.get("language", "english")
    language_name = str(language).replace("_", " ").title()
    st.markdown(f'''<div class="doc-page">
      <section class="doc-hero doc-hero-wide doc-hero-redesign">
        <div class="doc-hero-copy">
          <div class="doc-eyebrow">🌿 TRIBAL AI · YOUR STUDY SPACE</div>
          <h1>Make every document<br><span class="doc-hero-accent">easier to understand.</span></h1>
          <p>Upload your notes, ask questions, create revision material, or translate your study content into a language you’re comfortable with.</p>
          <div class="doc-pills">
            <span class="doc-pill">PDF supported</span>
            <span class="doc-pill">DOCX supported</span>
            <span class="doc-pill">TXT supported</span>
            <span class="doc-pill">🌐 Multilingual</span>
          </div>
        </div>
        <div class="doc-hero-highlights">
          <div class="doc-highlight green"><span>💬</span><div><strong>Ask your document</strong><small>Get answers based on your file</small></div></div>
          <div class="doc-highlight blue"><span>🌐</span><div><strong>Learn in your language</strong><small>Translate study material</small></div></div>
          <div class="doc-highlight gold"><span>🎓</span><div><strong>Prepare with confidence</strong><small>Summaries, concepts and practice</small></div></div>
        </div>
      </section>
    </div>''', unsafe_allow_html=True)



    # New visual design, scoped to this page only.
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"]:has(.doc-page) {
      background:
        radial-gradient(ellipse at 8% 0%, rgba(16,185,129,.13), transparent 34%),
        linear-gradient(145deg,#f3f8f4 0%,#edf5ef 55%,#f7faf7 100%) !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .main,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMain"] {
      background:transparent !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMainBlockContainer"] {
      max-width:1440px !important; padding-top:2rem !important; padding-bottom:3rem !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-hero-redesign {
      background:linear-gradient(115deg,#ffffff 0%,#f0faf3 58%,#e2f6e9 100%) !important;
      border:1px solid #cce5d3 !important; border-radius:26px !important;
      box-shadow:0 18px 45px rgba(24,74,43,.09) !important;
      padding:38px !important; margin-bottom:26px !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-hero-redesign h1,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-hero-redesign strong {
      color:#142b1d !important; -webkit-text-fill-color:#142b1d !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-hero-redesign p {
      color:#52665a !important; -webkit-text-fill-color:#52665a !important;
      max-width:680px !important; font-size:16px !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-hero-accent,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-eyebrow {
      color:#16834b !important; -webkit-text-fill-color:#16834b !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-pill {
      color:#245239 !important; -webkit-text-fill-color:#245239 !important;
      background:#e7f5eb !important; border:1px solid #cce5d3 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-highlight {
      background:#ffffff !important; border:1px solid #d5e8da !important;
      box-shadow:0 5px 16px rgba(24,74,43,.05) !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-highlight strong {
      color:#173b26 !important; -webkit-text-fill-color:#173b26 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-highlight small {
      color:#63776a !important; -webkit-text-fill-color:#63776a !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stTabs"] button[role="tab"] {
      background:#ffffff !important; border:1px solid #d7e8dc !important;
      border-radius:13px 13px 0 0 !important; padding:12px 18px !important; min-height:48px !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stTabs"] button[role="tab"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stTabs"] button[role="tab"] * {
      color:#254a33 !important; -webkit-text-fill-color:#254a33 !important;
      opacity:1 !important; font-weight:700 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stTabs"] button[aria-selected="true"] {
      background:#e3f5e9 !important; border-color:#9ed5b0 !important;
      box-shadow:inset 0 -3px 0 #159957 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] {
      background:#f5fbf6 !important; border:1.5px dashed #82bd95 !important;
      border-radius:17px !important; padding:14px !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] section,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] section > div {
      background:transparent !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] small {
      color:#254a33 !important; -webkit-text-fill-color:#254a33 !important; opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] button {
      background:#176b3c !important; color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important; border:1px solid #176b3c !important;
      border-radius:10px !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploader"] button * {
      color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-baseweb="select"] > div,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-baseweb="input"] > div,
    [data-testid="stAppViewContainer"]:has(.doc-page) input,
    [data-testid="stAppViewContainer"]:has(.doc-page) textarea {
      background:#ffffff !important; color:#173b26 !important;
      -webkit-text-fill-color:#173b26 !important; border-color:#cbded0 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) label,
    [data-testid="stAppViewContainer"]:has(.doc-page) label *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stWidgetLabel"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stMarkdownContainer"] p {
      color:#203d2a !important; -webkit-text-fill-color:#203d2a !important; opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-panel,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-file-card,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-benefit {
      background:#ffffff !important; border-color:#d6e7da !important;
      box-shadow:0 6px 20px rgba(24,74,43,.045) !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-section-heading,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-file-name,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-benefit strong {
      color:#173b26 !important; -webkit-text-fill-color:#173b26 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-section-sub,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-muted,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-file-size,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-benefit p {
      color:#5b7062 !important; -webkit-text-fill-color:#5b7062 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .stButton button[kind="primary"],
    [data-testid="stAppViewContainer"]:has(.doc-page) .stDownloadButton button {
      background:linear-gradient(90deg,#16834b,#20ad65) !important;
      color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
      border:1px solid #16834b !important; border-radius:12px !important;
      font-weight:750 !important; min-height:46px !important; opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .stButton button[kind="primary"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page) .stDownloadButton button * {
      color:#ffffff !important; -webkit-text-fill-color:#ffffff !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-footer {
      color:#617568 !important; border-color:#d4e5d8 !important;
    }
    @media(max-width:850px) {
      [data-testid="stAppViewContainer"]:has(.doc-page) .doc-hero-redesign {padding:24px 20px !important;}
    }
    </style>
    """, unsafe_allow_html=True)

    chat_tab, translate_tab, knowledge_tab = st.tabs([
        "💬  Chat with document", "🌐  Translate document", "📚  Knowledge base"
    ])
    with chat_tab:
        _render_document_chat()
        _html('''
          <div class="doc-benefit-grid">
            <div class="doc-benefit"><span class="benefit-icon purple">▤</span><div><strong>Works with study material</strong><p>Lecture notes, textbooks, assignments and more</p></div></div>
            <div class="doc-benefit"><span class="benefit-icon green">◷</span><div><strong>Ask multiple questions</strong><p>Get detailed answers from your document</p></div></div>
            <div class="doc-benefit"><span class="benefit-icon blue">▥</span><div><strong>Understand better</strong><p>Summaries, explanations and key insights</p></div></div>
            <div class="doc-benefit"><span class="benefit-icon pink">🎓</span><div><strong>Designed for students</strong><p>Turn your notes into a personal study assistant</p></div></div>
          </div>
        ''')
    with translate_tab:
        _render_translation()
    with knowledge_tab:
        _render_knowledge_upload(language, language_name)
    st.markdown(
        '<div class="doc-footer">🌿 Tribal AI · Preserving knowledge · Connecting cultures · PDF · DOCX · TXT</div>',
        unsafe_allow_html=True,
    )


    # Contrast correction layer: appended last so it overrides legacy CSS.
    # It is scoped to this document workspace and does not alter its background.
    st.markdown("""
    <style>
    /* Chat upload: pale dropzone, strong green action, dark readable helper text. */
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] > div,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] section {
      background:#f4faf6 !important;
      background-color:#f4faf6 !important;
      border-color:#8fbea0 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] span {
      color:#244b32 !important;
      -webkit-text-fill-color:#244b32 !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button:focus,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button:active {
      background:#176b3c !important;
      background-color:#176b3c !important;
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      border:1px solid #176b3c !important;
      opacity:1 !important;
      box-shadow:none !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button p,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button span {
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      opacity:1 !important;
    }

    /* Example prompts: brighten supporting copy while retaining the dark-green cards. */
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-prompt-intro,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-prompt-card small {
      color:#d6e8dc !important;
      -webkit-text-fill-color:#d6e8dc !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-prompt-card strong,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-prompt-card .doc-prompt-number {
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-first-use,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-first-use *,
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-footer {
      color:#244b32 !important;
      -webkit-text-fill-color:#244b32 !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .doc-first-use {
      background:#e5f4e9 !important;
      border:1px solid #a9d5b6 !important;
    }

    /* Translation panel: keep the existing forest background, but use a
       consistent light upload surface and high-contrast white labels. */
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel {
      background:linear-gradient(145deg,#0d2117,#10291c) !important;
      border:1px solid #28583a !important;
      border-radius:18px !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel .doc-translate-panel-title,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel .doc-translate-help,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel label,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel label *,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stWidgetLabel"],
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stWidgetLabel"] * {
      color:#f4fff7 !important;
      -webkit-text-fill-color:#f4fff7 !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploader"],
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"],
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] > div,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] section {
      background:#f4faf6 !important;
      background-color:#f4faf6 !important;
      border-color:#8fbea0 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] small {
      color:#244b32 !important;
      -webkit-text-fill-color:#244b32 !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] button * {
      background:#176b3c !important;
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-baseweb="select"] > div {
      background:#ffffff !important;
      border:1px solid #b8d4c1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-baseweb="select"] input,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-baseweb="select"] span,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel [data-baseweb="select"] svg {
      color:#173b25 !important;
      fill:#173b25 !important;
      -webkit-text-fill-color:#173b25 !important;
      opacity:1 !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel .st-key-translate_complete_document button,
    [data-testid="stAppViewContainer"]:has(.doc-page) .st-key-doc_translation_panel .st-key-translate_complete_document button * {
      background:linear-gradient(90deg,#16834b,#20ad65) !important;
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      border-color:#16834b !important;
      opacity:1 !important;
    }
    /* Make all primary buttons readable in enabled and disabled states. */
    [data-testid="stAppViewContainer"]:has(.doc-page) button[kind="primary"],
    [data-testid="stAppViewContainer"]:has(.doc-page) button[kind="primary"]:disabled,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stBaseButton-primary"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stBaseButton-primary"] * {
      color:#ffffff !important;
      -webkit-text-fill-color:#ffffff !important;
      opacity:1 !important;
    }

    /* Document chat: preserve the existing message bubbles and avatars.
       Force readable light text inside every Streamlit chat message because
       the app's global theme was overriding the earlier user-only selector. */
    [data-testid="stAppViewContainer"]:has(.doc-page)
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stAppViewContainer"]:has(.doc-page)
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page)
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
    [data-testid="stAppViewContainer"]:has(.doc-page)
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] * {
      color: #F4FFF7 !important;
      -webkit-text-fill-color: #F4FFF7 !important;
      opacity: 1 !important;
    }

    /* Document page only: improve sidebar text contrast without changing
       sidebar backgrounds, borders, spacing, buttons, or navigation behavior. */
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] p,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] span,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] label,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] a,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] button,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] button *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
      color: #EAF4ED !important;
      -webkit-text-fill-color: #EAF4ED !important;
      opacity: 1 !important;
    }

    /* Final uploader override: match the all-green Upload control in Translate. */
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button p,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] button span {
      background: #176b3c !important;
      background-color: #176b3c !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
      border-color: #176b3c !important;
      opacity: 1 !important;
      text-shadow: none !important;
    }
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzone"] small *,
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stAppViewContainer"]:has(.doc-page) [data-testid="stFileUploaderDropzoneInstructions"] * {
      background: transparent !important;
      background-color: transparent !important;
      color: #365c43 !important;
      -webkit-text-fill-color: #365c43 !important;
      opacity: 1 !important;
      text-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)