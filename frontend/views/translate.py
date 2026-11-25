"""Language Studio: standalone, animated document translation workspace."""

import streamlit as st

from components.upload import _render_document_styles, _render_translation


def show_translate_page() -> None:
    """Render the translation workspace without changing its translation logic."""
    _render_document_styles()

    st.markdown(
        """
        <style>
        /* LIGHT CANVAS: override the app's dark theme on this workspace only */
        html:has(.language-studio-hero),
        body:has(.language-studio-hero),
        body:has(.language-studio-hero) .stApp,
        body:has(.language-studio-hero) [data-testid="stAppViewContainer"],
        body:has(.language-studio-hero) [data-testid="stMain"],
        body:has(.language-studio-hero) section.main,
        body:has(.language-studio-hero) .main .block-container {
            background: #ffffff !important;
            background-color: #ffffff !important;
        }
        body:has(.language-studio-hero) [data-testid="stAppViewContainer"] {
            color: #183b28 !important;
        }
        body:has(.language-studio-hero) .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }
        body:has(.language-studio-hero) [data-testid="stHeader"] {
            background: rgba(255,255,255,.94) !important;
        }
        body:has(.language-studio-hero) [data-testid="stMain"] p,
        body:has(.language-studio-hero) [data-testid="stMain"] label,
        body:has(.language-studio-hero) [data-testid="stMain"] small {
            color: #365744 !important;
            -webkit-text-fill-color: #365744 !important;
            opacity: 1 !important;
        }

        @keyframes ls-float {
            0%, 100% { transform: translateY(0) rotateX(0deg); }
            50% { transform: translateY(-9px) rotateX(2deg); }
        }
        @keyframes ls-glow {
            0%, 100% { opacity: .45; transform: scale(.96); }
            50% { opacity: .9; transform: scale(1.04); }
        }
        @keyframes ls-shimmer {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }
        body:has(.language-studio-hero) [data-testid="stMain"] {
            background-image:
                radial-gradient(circle at 8% 16%, rgba(60, 174, 105, .055) 0 2px, transparent 3px),
                radial-gradient(circle at 92% 42%, rgba(60, 174, 105, .05) 0 3px, transparent 4px),
                linear-gradient(180deg, #ffffff 0%, #fbfefc 55%, #f7fcf8 100%) !important;
            background-size: 42px 42px, 58px 58px, auto !important;
        }
        .language-studio-hero {
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 28px;
            padding: 34px 38px;
            margin: 8px 0 28px;
            border: 1px solid rgba(124, 184, 143, .42);
            border-radius: 26px;
            background: linear-gradient(135deg, #f7fcf8 0%, #e7f5eb 48%, #f3faf6 100%);
            box-shadow: 0 18px 45px rgba(26, 91, 53, .10),
                        inset 0 1px 0 rgba(255,255,255,.9);
            perspective: 900px;
        }
        .language-studio-hero:before {
            content: "";
            position: absolute;
            width: 250px; height: 250px;
            right: 7%; top: -145px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(54, 171, 103, .22), transparent 68%);
            animation: ls-glow 5s ease-in-out infinite;
        }
        .language-studio-copy { position: relative; z-index: 1; max-width: 680px; }
        .language-studio-kicker {
            color: #24804a; font-size: 11px; font-weight: 800;
            letter-spacing: .16em; text-transform: uppercase; margin-bottom: 12px;
        }
        .language-studio-title {
            color: #123b25; font-size: clamp(29px, 3.5vw, 43px);
            line-height: 1.08; font-weight: 850; letter-spacing: -.035em;
            margin: 0 0 12px;
        }
        .language-studio-title span {
            background: linear-gradient(90deg, #16834b, #43b879, #16834b);
            background-size: 200% auto; color: transparent;
            -webkit-background-clip: text; background-clip: text;
            animation: ls-shimmer 5s linear infinite;
        }
        .language-studio-description { color: #587263; font-size: 15px; line-height: 1.65; margin: 0; }
        .language-studio-art {
            position: relative; z-index: 1; flex: 0 0 150px; height: 130px;
            display: grid; place-items: center; animation: ls-float 5s ease-in-out infinite;
            transform-style: preserve-3d;
        }
        .language-studio-orbit {
            position: absolute; width: 126px; height: 126px; border-radius: 50%;
            border: 1px solid rgba(39, 139, 77, .28); transform: rotateX(65deg) rotateZ(-25deg);
            box-shadow: 0 0 28px rgba(47, 157, 88, .12);
        }
        .language-studio-card {
            width: 78px; height: 94px; border-radius: 16px;
            display: grid; place-items: center; font-size: 38px;
            background: linear-gradient(145deg, #ffffff, #d9f0e0);
            border: 1px solid rgba(78, 155, 101, .45);
            box-shadow: 12px 15px 24px rgba(24, 91, 49, .18),
                        inset 0 1px 0 #fff;
            transform: rotateY(-14deg) rotateX(8deg);
        }
        /* Page-only styling for the existing translation widgets */
        body:has(.language-studio-hero) [data-testid="stAppViewContainer"] .doc-translate-heading {
            padding: 8px 4px 18px !important;
            color: #173f29 !important;
        }
        body:has(.language-studio-hero) [data-testid="stAppViewContainer"] .doc-translate-heading * {
            opacity: 1 !important;
            text-shadow: none !important;
        }
        body:has(.language-studio-hero) [data-testid="stAppViewContainer"] .doc-translate-heading .doc-section-heading {
            color: #174b2d !important;
            -webkit-text-fill-color: #174b2d !important;
            font-size: 23px !important;
            font-weight: 850 !important;
        }
        body:has(.language-studio-hero) [data-testid="stAppViewContainer"] .doc-translate-heading .doc-section-sub {
            color: #5b7464 !important;
            -webkit-text-fill-color: #5b7464 !important;
            font-size: 14px !important;
        }
        body:has(.language-studio-hero) .st-key-doc_translation_panel,
        body:has(.language-studio-hero) .st-key-doc_translation_panel * {
            text-shadow: none !important;
        }
        body:has(.language-studio-hero) .st-key-doc_translation_panel .doc-translate-panel-title {
            color: #173f29 !important;
            -webkit-text-fill-color: #173f29 !important;
            font-size: 17px !important;
            font-weight: 850 !important;
        }
        body:has(.language-studio-hero) .st-key-doc_translation_panel .doc-translate-help {
            color: #61796a !important;
            -webkit-text-fill-color: #61796a !important;
            opacity: 1 !important;
        }
        body:has(.language-studio-hero) .st-key-doc_translation_panel [data-testid="stWidgetLabel"],
        body:has(.language-studio-hero) .st-key-doc_translation_panel [data-testid="stWidgetLabel"] * {
            color: #244d34 !important;
            -webkit-text-fill-color: #244d34 !important;
            opacity: 1 !important;
            font-weight: 750 !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .doc-translate-heading {
            padding: 0 2px 14px !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .doc-translate-heading .doc-section-heading {
            color: #16472c !important; font-size: 21px !important; font-weight: 800 !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .doc-translate-heading .doc-section-sub {
            color: #60796a !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel {
            border: 1px solid #d5e9da !important; border-radius: 22px !important;
            background: linear-gradient(145deg, #ffffff, #f5fbf6) !important;
            padding: clamp(18px, 3vw, 30px) !important;
            box-shadow: 0 22px 48px rgba(28, 88, 49, .12),
                        0 5px 12px rgba(28, 88, 49, .05),
                        inset 0 1px 0 #ffffff !important;
            transform: translateZ(0);
            transition: transform .28s ease, box-shadow .28s ease !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel:hover {
            transform: translateY(-4px) perspective(1000px) rotateX(.35deg);
            box-shadow: 0 22px 48px rgba(28, 88, 49, .14) !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel [data-testid="stWidgetLabel"],
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel [data-testid="stWidgetLabel"] * {
            color: #244d34 !important; -webkit-text-fill-color: #244d34 !important;
            opacity: 1 !important; font-weight: 700 !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"] {
            border: 1.5px dashed #79b98b !important; border-radius: 17px !important;
            background: linear-gradient(135deg, #f3fbf5, #eaf7ee) !important;
            box-shadow: inset 0 1px 0 #fff, 0 8px 20px rgba(39, 125, 67, .06) !important;
            transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel [data-testid="stFileUploaderDropzone"]:hover {
            transform: translateY(-3px); border-color: #269653 !important;
            box-shadow: 0 12px 24px rgba(39, 125, 67, .12) !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel input,
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel [data-baseweb="select"] > div {
            border-radius: 12px !important; border-color: #cfe2d4 !important;
            background: #ffffff !important; color: #173b26 !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel .stButton button[kind="primary"] {
            min-height: 50px !important; border-radius: 14px !important;
            background: linear-gradient(110deg, #147b43, #20a85e, #147b43) !important;
            background-size: 200% 100% !important; animation: ls-shimmer 7s linear infinite;
            box-shadow: 0 10px 22px rgba(22, 132, 72, .20) !important;
            transition: transform .2s ease, box-shadow .2s ease !important;
        }
        [data-testid="stAppViewContainer"]:has(.language-studio-hero) .st-key-doc_translation_panel .stButton button[kind="primary"]:hover {
            transform: translateY(-2px); box-shadow: 0 14px 28px rgba(22, 132, 72, .28) !important;
        }
        @media (max-width: 700px) {
            .language-studio-hero { padding: 25px 22px; }
            .language-studio-art { flex-basis: 88px; transform: scale(.78); }
        }
        @media (prefers-reduced-motion: reduce) {
            .language-studio-hero *, [data-testid="stAppViewContainer"]:has(.language-studio-hero) * {
                animation: none !important; transition: none !important;
            }
        }
        </style>
        <section class="language-studio-hero">
          <div class="language-studio-copy">
            <div class="language-studio-kicker">🌐 &nbsp; TRIBAL AI · LANGUAGE STUDIO</div>
            <h1 class="language-studio-title">Every document, <span>every language.</span></h1>
            <p class="language-studio-description">
              Turn lecture notes, assignments and study material into clear, readable translations.
              Upload once, choose your languages, and let Language Studio do the rest.
            </p>
          </div>
          <div class="language-studio-art" aria-hidden="true">
            <div class="language-studio-orbit"></div>
            <div class="language-studio-card">🌐</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # Keep the existing upload, language selectors, API call and download flow.
    _render_translation()

    st.markdown(
        '<div class="doc-footer">🌿 Tribal AI · Language Studio · PDF · DOCX · TXT</div>',
        unsafe_allow_html=True,
    )
