import streamlit as st
from html import escape
from markdown_it import MarkdownIt
import re
from components.response_formatter import format_for_display
from components.visual_renderer import extract_mermaid_blocks, render_mermaid_diagrams

def normalize_assistant_markdown(content):
    """Normalize prose Markdown while preserving fenced code blocks."""
    content = str(content or "").replace("\r\n", "\n").replace("\r", "\n")
    content = content.replace("\\n", "\n")

    # Process only prose segments. Regex cleanup must never rewrite code.
    parts = re.split(r"(?ms)(^```[^\n]*\n.*?^```[ \t]*$|^~~~[^\n]*\n.*?^~~~[ \t]*$)", content)
    normalized = []
    for part in parts:
        if part.startswith("```") or part.startswith("~~~"):
            normalized.append(part)
            continue
        part = re.sub(r"(?m)^(#{1,6})(?=[^#\s])", r"\1 ", part)
        part = re.sub(
            r"(?i)\b(Definition|Explanation|Examples|Applications\s*/\s*Importance|Summary|Key Concepts)(?=[A-Z])",
            r"\1\n\n", part,
        )
        part = re.sub(r"(\*\*[^*\n]+?\*\*)(?=[A-Za-z0-9])", r"\1 ", part)
        part = re.sub(r"(?m)(?<!^)\s+([-*+]\s+)", r"\n\1", part)
        part = re.sub(r"(?m)(?<!^)\s+(\d+[.)]\s+)", r"\n\1", part)
        part = re.sub(r"\n{3,}", "\n\n", part)

        # Prevent a long introductory paragraph wrapped entirely in Markdown
        # bold from appearing as a wall of bold text. Keep short bold labels
        # and inline emphasis unchanged.
        part = re.sub(
            r"(?m)^\s*\*\*([^*\n]{100,})\*\*\s*$",
            lambda match: match.group(1).strip(),
            part,
        )
        normalized.append(part)
    return "".join(normalized).strip()


def html_block(content):
    """Render prebuilt HTML directly, without parsing it a second time as Markdown."""
    # MarkdownIt has already converted the assistant response to HTML. Passing that
    # HTML through st.markdown() runs another Markdown parse and can turn escaped or
    # trailing HTML fragments into visible code blocks. st.html() renders the result
    # directly while preserving the existing HTML/CSS structure.
    if hasattr(st, "html"):
        st.html(content)
    else:
        # Compatibility fallback for older Streamlit versions.
        st.markdown(content, unsafe_allow_html=True)

def apply_message_ui():
    st.markdown(
        """
        <style>
        @import url("https://fonts.googleapis.com/css2?family=Noto+Sans+Ol+Chiki&display=swap");
        /* SANTALI_OL_CHIKI_WEBFONT_FIX */
        /* Ol Chiki requires an explicit script-capable font. */
        .assistant-message.santali-script,
        .assistant-message.santali-script * {
            font-family: "Noto Sans Ol Chiki", sans-serif !important;
        }
        .chat-row {
            display: flex;
            width: 100%;
            gap: 12px;
            margin: 0.9rem 0 1.15rem;
            box-sizing: border-box;
        }
        .assistant-row {
            align-items: flex-start;
        }
        .user-row {
            align-items: flex-start;
            justify-content: flex-end;
        }
        .ai-avatar,
        .user-avatar {
            width: 36px;
            height: 36px;
            min-width: 36px;
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
            box-sizing: border-box;
        }
        .ai-avatar {
            background: linear-gradient(135deg, #166534, #22c55e);
            color: white;
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.18);
        }
        .user-avatar {
            background: #eef2f7;
            border: 1px solid rgba(100, 116, 139, 0.16);
        }
        .assistant-message-wrapper {
            max-width: min(850px, calc(100% - 50px));
            width: 100%;
        }
        .user-message-wrapper {
            max-width: min(760px, calc(100% - 50px));
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        .ai-label,
        .user-label {
            font-size: 0.78rem;
            font-weight: 700;
            margin: 0 0 6px 2px;
            color: #475569;
        }
        .user-label {
            margin-right: 2px;
        }
        .ai-online-dot {
            display: inline-block;
            width: 7px;
            height: 7px;
            margin-left: 5px;
            border-radius: 50%;
            background: #22c55e;
            vertical-align: 1px;
            box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.10);
        }
        .assistant-message,
        .user-message {
            padding: 14px 17px;
            border-radius: 16px;
            font-size: 0.95rem;
            line-height: 1.7;
            word-break: break-word;
            box-sizing: border-box;
        }
        .assistant-message {
            /* Open ChatGPT-style answer: no enclosing bubble/card. */
            background: transparent !important;
            border: 0 !important;
            color: #1f2937;
            box-shadow: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100%;
            min-width: 0;
            overflow-wrap: anywhere;
            overflow-x: auto;
        }
        .assistant-message h1,
        .assistant-message h2,
        .assistant-message h3,
        .assistant-message h4 {
            color: #166534;
            line-height: 1.3;
            margin: 0.55rem 0 0.25rem !important;
            padding: 0 !important;
        }
        .assistant-message h1:first-child,
        .assistant-message h2:first-child,
        .assistant-message h3:first-child,
        .assistant-message h4:first-child {
            margin-top: 0;
        }
        .assistant-message h1 { font-size: 1.35rem; }
        .assistant-message h2 { font-size: 1.2rem; }
        .assistant-message h3 { font-size: 1.05rem; }
        .assistant-message p {
            margin: 0.25rem 0 0.4rem !important;
            padding: 0 !important;
        }
        .assistant-message ul,
        .assistant-message ol {
            padding-left: 1.4rem !important;
            margin: 0.2rem 0 0.4rem !important;
        }
        .assistant-message li {
            margin: 0.08rem 0 !important;
            padding: 0 !important;
        }
        .assistant-message h1 + p,
        .assistant-message h2 + p,
        .assistant-message h3 + p,
        .assistant-message h4 + p {
            margin-top: 0.15rem !important;
        }
        .assistant-message > :first-child { margin-top: 0; }
        .assistant-message > :last-child { margin-bottom: 0; }
        .assistant-message table {
            display: block;
            max-width: 100%;
            overflow-x: auto;
            border-collapse: collapse;
            margin: 0.75rem 0;
        }
        .assistant-message th,
        .assistant-message td {
            border: 1px solid #dbe3dd;
            padding: 8px 10px;
            text-align: left;
            vertical-align: top;
            min-width: 100px;
        }
        .assistant-message th { background: #f0f7f1; }
        .assistant-message img { max-width: 100%; height: auto; }
        .assistant-message a { color: #23834b; text-decoration: underline; }
        .assistant-message pre code { border: 0; }
        .assistant-message table { width: 100%; }

        .user-message {
            background: #1f2937;
            color: #ffffff;
            border-top-right-radius: 5px;
            box-shadow: 0 5px 16px rgba(15, 23, 42, 0.12);
        }
        /* ChatGPT-like answer typography */
        .assistant-message {
            color: #30343b !important;
            font-size: 15.5px !important;
            line-height: 1.78 !important;
            font-weight: 400 !important;
            letter-spacing: 0 !important;
            text-align: left !important;
        }
        .assistant-message p,
        .assistant-message li,
        .assistant-message blockquote,
        .assistant-message td {
            color: #30343b !important;
            font-weight: 400 !important;
            font-size: 15.5px !important;
            line-height: 1.78 !important;
        }
        .assistant-message strong,
        .assistant-message b {
            color: #202a36 !important;
            font-weight: 650 !important;
        }
        .assistant-message h1,
        .assistant-message h2,
        .assistant-message h3,
        .assistant-message h4 {
            color: #176b3a !important;
            font-weight: 700 !important;
            letter-spacing: -0.015em !important;
        }
        .assistant-message h1 { font-size: 1.45rem !important; margin-top: 1rem !important; }
        .assistant-message h2 { font-size: 1.25rem !important; margin-top: 0.9rem !important; }
        .assistant-message h3 { font-size: 1.08rem !important; margin-top: 0.75rem !important; }
        .assistant-message p { margin: 0.45rem 0 0.75rem !important; }
        .assistant-message ul,
        .assistant-message ol { margin: 0.35rem 0 0.8rem !important; }
        .assistant-message li { padding-left: 0.12rem !important; margin: 0.18rem 0 !important; }
        .assistant-message hr {
            border: 0 !important;
            border-top: 1px solid #e5e7eb !important;
            margin: 1rem 0 !important;
        }
        .assistant-message blockquote {
            border-left: 3px solid #d1d5db !important;
            background: #f9fafb !important;
            padding: 0.55rem 0.9rem !important;
            border-radius: 0 8px 8px 0 !important;
        }
        .assistant-message strong { font-weight: 650 !important; }
        .assistant-message code {
            padding: 2px 6px;
            border-radius: 6px;
            background: #f1f5f9;
            font-size: 0.88em;
        }
        .assistant-message pre {
            overflow-x: auto;
            padding: 13px 15px;
            border-radius: 10px;
            background: #0f172a;
            color: #f8fafc;
            margin: 12px 0;
            white-space: pre;
            tab-size: 4;
        }
        .assistant-message pre code {
            display: block;
            padding: 0;
            margin: 0;
            background: transparent;
            color: #f8fafc;
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.88rem;
            line-height: 1.55;
            white-space: pre;
            overflow-wrap: normal;
            word-break: normal;
        }
        .assistant-message blockquote {
            margin: 12px 0;
            padding: 8px 13px;
            border-left: 3px solid #22c55e;
            background: #f8faf9;
            color: #475569;
            border-radius: 0 8px 8px 0;
        }
        .message-info {
            margin: 7px 0 0 50px;
            font-size: 0.72rem;
            color: #94a3b8;
        }
        @media (max-width: 768px) {
            .chat-row {
                gap: 8px;
                margin: 0.75rem 0 1rem;
            }
            .ai-avatar,
            .user-avatar {
                width: 31px;
                height: 31px;
                min-width: 31px;
                font-size: 14px;
            }
            .assistant-message-wrapper,
            .user-message-wrapper {
                max-width: calc(100% - 39px);
            }
            .assistant-message {
                padding: 0 !important;
                font-size: 0.94rem;
                line-height: 1.7;
            }
            .user-message {
                padding: 11px 13px;
                font-size: 0.9rem;
                line-height: 1.6;
            }
            .message-info {
                margin-left: 39px;
            }
        }
        [data-testid="stAppViewContainer"] .user-message {
            transition: box-shadow 0.18s ease, transform 0.18s ease;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def _is_santali_language(language, content=""):
    key = str(language or "").strip().lower().replace("_", "-")
    return (
        "santali" in key
        or key in {"sat", "sat-olck", "ol-chiki"}
        or any("\\u1c50" <= ch <= "\\u1c7f" for ch in str(content or ""))
    )


def render_message(
    role,
    content,
    language=None,
    detected_language=None,
    sources=None,
    timestamp=None,
    show_sources=True
):
    """
    Render user and AI messages as clean separate cards.
    Sources from the backend are displayed when official URLs are available.
    """
    apply_message_ui()
    if role == "user":
        # UI-only cleanup for legacy messages where internal response-format
        # guidance was appended to the user's question. Stored data is untouched.
        user_display_content = str(content or "").replace("\\r\\n", "\n").replace("\\n", "\n")
        user_display_content = re.sub(
            r"(?is)\s*\[\s*TRIBAL\s+AI\s+(?:RESPONSE\s+FORMAT|TEACHING\s+AND\s+PRESENTATION\s+INSTRUCTIONS)\b.*$",
            "",
            user_display_content,
        ).strip()
        user_content = escape(user_display_content).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
        html_block(
            f"""
            <div class="chat-row user-row">
                <div class="user-message-wrapper">
                    <div class="user-label">You</div>
                    <div class="user-message">{user_content}</div>
                </div>
                <div class="user-avatar">👤</div>
            </div>
            """
        )
        return

    # Convert assistant Markdown to safe HTML. Raw HTML in the model response
    # is disabled, while headings, lists, bold text, code, quotes, and tables
    # are rendered as formatted content.
    markdown_renderer = MarkdownIt(
        "default",
        {"html": False, "breaks": True},
    ).enable("table")

    normalized_content = normalize_assistant_markdown(content)
    normalized_content = format_for_display(normalized_content, language)

    # SANTALI_MARKDOWN_DISPLAY_CLEANUP_V1: translated Markdown markers can
    # survive translation or leave empty list items. Clean only Santali cards.
    language_key = str(language or "").strip().lower().replace("_", "-")
    if "santali" in language_key or language_key in {"sat", "sat-olck", "ol-chiki"}:
        # Remove heading markers, including stray doubled hashes left mid-line.
        normalized_content = re.sub(r"(?m)^\s*#{1,6}\s*", "", normalized_content)
        normalized_content = re.sub(r"#{2,}", "", normalized_content)

        # Convert list items to plain lines so untranslated/empty Markdown
        # bullets do not appear as blank rows in the answer card.
        normalized_content = re.sub(
            r"(?m)^\s*(?:[-*+•◦▪●○]\s+|\d+[.)]\s+)",
            "",
            normalized_content,
        )
        # Remove list-marker-only rows after translation.
        normalized_content = re.sub(
            r"(?m)^\s*(?:[-*+•◦▪●○]|\d+[.)])\s*$\n?",
            "",
            normalized_content,
        )
        normalized_content = re.sub(r"(?m)^[ \t]+$", "", normalized_content)
        normalized_content = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", normalized_content)
        normalized_content = normalized_content.strip()

    # Replace Mermaid fences with visual placeholders so each diagram appears
    # exactly where it belongs in the explanation, not after the whole answer.
    mermaid_diagrams = []
    if not _is_santali_language(language, content):
        def _diagram_placeholder(match):
            mermaid_diagrams.append(match.group(1).strip())
            return f"\n\nTRIBALVISUALPLACEHOLDER{len(mermaid_diagrams)-1}\n\n"
        normalized_content = re.sub(
            r"(?ms)^[ \t]*```mermaid[ \t]*\n(.*?)^[ \t]*```[ \t]*$",
            _diagram_placeholder, normalized_content
        )
    rendered_content = markdown_renderer.render(normalized_content)
    # Keep diagram markers as plain tokens. SVG is rendered in a dedicated
    # Streamlit HTML component below; st.html sanitizers can strip inline SVG.
    # SANTALI_OL_CHIKI_FINAL_DISPLAY_FIX_V2: bypass Markdown/font fallbacks for Ol Chiki only.
    _santali_language_key = str(language or "").strip().lower().replace("_", "-")
    _santali_display = (
        "santali" in _santali_language_key
        or _santali_language_key in {"sat", "sat-olck", "ol-chiki"}
        or any("\u1c50" <= _ch <= "\u1c7f" for _ch in str(content or ""))
    )
    if _santali_display:
        _santali_plain = normalize_assistant_markdown(content)
        _santali_plain = format_for_display(_santali_plain, language)
        # Remove Markdown that survived machine translation, plus empty list rows.
        _santali_plain = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]*", "", _santali_plain)
        _santali_plain = re.sub(
            r"(?m)^[ \t]*(?:[-*+•◦▪●○]|\d+[.)])[ \t]*$\n?", "", _santali_plain
        )
        _santali_plain = re.sub(
            r"(?m)^[ \t]*(?:[-*+•◦▪●○]|\d+[.)])[ \t]+", "", _santali_plain
        )
        _santali_plain = re.sub(r"\*\*(.*?)\*\*", r"\1", _santali_plain)
        _santali_plain = re.sub(r"__(.*?)__", r"\1", _santali_plain)
        _santali_plain = re.sub(r"`([^`]*)`", r"\1", _santali_plain)
        _santali_plain = re.sub(r"(?m)^[ \t]+$", "", _santali_plain)
        _santali_plain = re.sub(r"\n{3,}", "\n\n", _santali_plain).strip()
        # Nirmala UI is available on Windows 10/11 and includes Ol Chiki glyphs.
        # Inline styling avoids depending on Google Fonts/network/CSS import behavior.
        rendered_content = (
            '<div lang="sat" dir="ltr" '
            'style="font-family: \'Noto Sans Ol Chiki\', \'Nirmala UI\', sans-serif !important; '
            'white-space: pre-wrap; line-height: 1.9;">'
            + escape(_santali_plain).replace("\n", "<br>")
            + "</div>"
        )

    # SANTALI_OL_CHIKI_WEBFONT_FIX: opt in only for Santali assistant cards.
    language_key = str(language or "").strip().lower().replace("_", "-")
    language_class = (
        " santali-script"
        if language_key in {"santali", "sat", "sat-olck", "ol-chiki"}
        else ""
    )

    # Render answer text and diagrams as separate Streamlit blocks. This avoids
    # inline-SVG sanitization and guarantees the diagram appears between its
    # surrounding explanation paragraphs.
    from components.visual_renderer import flowchart_svg
    html_block('<div class="chat-row assistant-row"><div class="ai-avatar">🌿</div><div class="assistant-message-wrapper">')
    _segments = re.split(r"TRIBALVISUALPLACEHOLDER(\d+)", rendered_content)
    _text_segment = _segments[0] if _segments else rendered_content
    if _text_segment.strip():
        html_block(f'<div class="assistant-message{language_class}">{_text_segment}</div>')
    for _idx in range(1, len(_segments), 2):
        _diagram_index = int(_segments[_idx])
        _diagram_source = mermaid_diagrams[_diagram_index] if _diagram_index < len(mermaid_diagrams) else ""
        _svg = flowchart_svg(_diagram_source)
        if _svg:
            _viewbox_match = re.search(
                r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"',
                _svg
            )
            _view_width = float(_viewbox_match.group(1)) if _viewbox_match else 900
            _view_height = float(_viewbox_match.group(2)) if _viewbox_match else 420
            # Compact, left-aligned diagram card. Short diagrams fit naturally;
            # tall diagrams scroll inside the card without widening the chat.
            _diagram_scale = min(1.0, 560.0 / max(_view_width, 1.0))
            _scaled_height = _view_height * _diagram_scale
            _viewport_height = min(230, max(115, int(_scaled_height + 6)))
            _card_height = _viewport_height + 48
            _component_height = _card_height + 16
            _component_html = f"""<!doctype html><html><head><meta charset="utf-8">
            <style>
            *{{box-sizing:border-box}}
            html,body{{margin:0;padding:0;width:100%;height:100%;background:transparent;overflow:hidden}}
            .tribal-visual-card{{width:100%;max-width:590px;height:{_card_height}px;
            margin:8px 0 12px 0;padding:9px 11px;border:1px solid #dce9df;
            border-radius:13px;background:#f8fbf8;font-family:Arial,sans-serif;
            overflow:hidden;display:flex;flex-direction:column}}
            .tribal-visual-label{{flex:0 0 auto;font-size:8px;font-weight:800;
            letter-spacing:.10em;color:#547561;margin:0 0 6px}}
            .tribal-diagram-scroll{{flex:1 1 auto;min-height:0;width:100%;
            overflow-y:auto;overflow-x:auto;overscroll-behavior:contain;
            scrollbar-width:thin;scrollbar-color:#8db99b #edf5ef;
            border-radius:8px;padding:2px}}
            .tribal-diagram-scroll svg{{display:block;width:100%!important;
            max-width:560px!important;height:auto!important;max-height:none!important;
            margin:0 auto}}
            .tribal-diagram-scroll::-webkit-scrollbar{{width:7px;height:7px}}
            .tribal-diagram-scroll::-webkit-scrollbar-thumb{{background:#8db99b;border-radius:8px}}
            .tribal-diagram-scroll::-webkit-scrollbar-track{{background:#edf5ef;border-radius:8px}}
            </style></head><body>
            <div class="tribal-visual-card">
              <div class="tribal-visual-label">VISUAL EXPLANATION · SCROLL TO EXPLORE</div>
              <div class="tribal-diagram-scroll">{_svg}</div>
            </div></body></html>"""
            st.components.v1.html(_component_html, height=_component_height, scrolling=False)
        else:
            st.info("The diagram format could not be rendered. The written explanation is still available.")
        _following_text = _segments[_idx + 1] if _idx + 1 < len(_segments) else ""
        if _following_text.strip():
            html_block(f'<div class="assistant-message{language_class}">{_following_text}</div>')
    html_block('</div></div></div>')
    info = []
    if language:
        info.append(
            f"🌐 {language.replace('_', ' ').title()}"
        )
    if detected_language:
        info.append(
            f"📝 Detected: "
            f"{detected_language.replace('_', ' ').title()}"
        )
    if timestamp:
        info.append(
            f"🕒 {timestamp}"
        )
    # Display official source links returned by MCP.
    if sources and show_sources:
        source_blocks = []
        for source in sources:
            if isinstance(source, dict):
                url = str(source.get("url", "")).strip()
                title = str(
                    source.get("title", "Official Source")
                ).strip()
                source_name = str(
                    source.get("source_name", "")
                ).strip()
                if (
                    url.startswith("https://")
                    or url.startswith("http://")
                ):
                    label = escape(title or "Official Source")
                    name = escape(source_name)
                    verified_on = escape(str(source.get("verified_on","")).strip())
                    name_html = (
                        f'<div style="font-size:13px;line-height:1.45;color:#64748b;margin-bottom:6px;">{name}</div>'
                        if name
                        else ""
                    )
                    verified_html = (
                        f'<div style="font-size:12px;color:#64748b;margin-bottom:9px;">✓ Verified: {verified_on}</div>'
                        if verified_on
                        else ""
                    )
                    source_blocks.append(
                        f"""
                        <div style="
                            margin:10px 0;
                            padding:14px 16px;
                            border:1px solid #dfe5e1;
                            border-radius:12px;
                            background:#f8faf9;
                            box-shadow:0 1px 3px rgba(0,0,0,0.04);
                            box-sizing:border-box;
                        ">
                            <div style="
                                font-weight:600;
                                font-size:15px;
                                line-height:1.45;
                                margin-bottom:5px;
                                color:#1f2937;
                            ">{label}</div>
                            {name_html}
                            {verified_html}
                            <a
                                href="{escape(url, quote=True)}"
                                target="_blank"
                                rel="noopener noreferrer"
                                style="
                                    color:#2563eb;
                                    font-size:14px;
                                    font-weight:500;
                                    text-decoration:none;
                                "
                            >
                                🔗 Open Official Website →
                            </a>
                        </div>
                        """
                    )
            else:
                # Preserve compatibility with existing string sources.
                source_text = escape(str(source))
                source_blocks.append(
                    f"""
                    <div style="
                        margin:10px 0;
                        padding:12px 14px;
                        border:1px solid #dfe5e1;
                        border-radius:12px;
                        background:#f8faf9;
                        box-sizing:border-box;
                    ">
                        <div style="
                            font-size:14px;
                            color:#374151;
                        ">{source_text}</div>
                    </div>
                    """
                )
        if source_blocks:
            html_block(
                f"""
                <div style="
                    margin-top:14px;
                    width:100%;
                    box-sizing:border-box;
                ">
                    <div style="
                        font-size:17px;
                        font-weight:600;
                        margin-bottom:8px;
                        color:#374151;
                    ">
                        🔗 Official Sources
                    </div>
                    {"".join(source_blocks)}
                </div>
                """
            )
    if info:
        html_block(
            f"""
            <div class="message-info">
                {" &nbsp; • &nbsp; ".join(info)}
            </div>
            """
        )


# VISUAL_LEARNING_PRESENTATION_CSS
try:
    st.markdown("""
    <style>
    .tribal-visual-card {
        margin: 18px 0 20px; padding: 18px 18px 14px;
        border: 1px solid #dce9df; border-radius: 16px;
        background: linear-gradient(145deg,#ffffff,#f5faf6);
        box-shadow: 0 5px 18px rgba(30,75,45,.055);
        overflow: hidden;
    }
    .tribal-visual-label {
        margin: 0 0 12px; color: #547561; font-size: 11px;
        font-weight: 800; letter-spacing: .11em;
    }
    .assistant-message h1, .assistant-message h2, .assistant-message h3 {
        line-height: 1.28; letter-spacing: -.02em; margin-top: 1.15em;
        margin-bottom: .48em;
    }
    .assistant-message p { line-height: 1.72; margin: .55em 0; }
    .assistant-message li { line-height: 1.68; margin: .25em 0; }
    .assistant-message table { width:100%; border-collapse:collapse; margin:14px 0; }
    .assistant-message th { background:#edf6ef; font-weight:700; }
    .assistant-message th, .assistant-message td { padding:10px 12px; border:1px solid #dbe6de; text-align:left; }
    @media (prefers-color-scheme: dark) {
      .tribal-visual-card { background:#17231c; border-color:#344c3b; }
      .tribal-visual-label { color:#afc7b6; }
    }
    </style>
    """, unsafe_allow_html=True)
except Exception:
    pass
