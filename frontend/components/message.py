import streamlit as st
from html import escape
from markdown_it import MarkdownIt
import re
from components.response_formatter import format_for_display

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
            max-width: min(820px, calc(100% - 50px));
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
            background: #ffffff;
            border: 1px solid rgba(100, 116, 139, 0.13);
            color: #1f2937;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.045);
            border-top-left-radius: 5px;
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
        .user-message {
            background: #1f2937;
            color: #ffffff;
            border-top-right-radius: 5px;
            box-shadow: 0 5px 16px rgba(15, 23, 42, 0.12);
        }
        .assistant-message strong {
            font-weight: 700;
        }
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
            .assistant-message,
            .user-message {
                padding: 11px 13px;
                font-size: 0.9rem;
                line-height: 1.6;
            }
            .message-info {
                margin-left: 39px;
            }
        }
        [data-testid="stAppViewContainer"] .assistant-message,
        [data-testid="stAppViewContainer"] .user-message {
            transition: box-shadow 0.18s ease, transform 0.18s ease;
        }
        .assistant-message:hover {
            box-shadow: 0 7px 22px rgba(15, 23, 42, 0.07);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_message(
    role,
    content,
    language=None,
    detected_language=None,
    sources=None,
    timestamp=None
):
    """
    Render user and AI messages as clean separate cards.
    Sources from the backend are displayed when official URLs are available.
    """
    apply_message_ui()
    if role == "user":
        user_content = escape(str(content)).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
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

    rendered_content = markdown_renderer.render(normalized_content)
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

    # Render the full assistant card in one HTML call to avoid nesting
    # Streamlit elements inside an HTML container.
    html_block(
        f"""
        <div class="chat-row assistant-row">
            <div class="ai-avatar">🌿</div>
            <div class="assistant-message-wrapper">
                <div class="ai-label">
                    Tribal AI
                    <span class="ai-online-dot"></span>
                </div>
                <div class="assistant-message{language_class}">
                    {rendered_content}
                </div>
            </div>
        </div>
        """
    )
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
    if sources:
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
