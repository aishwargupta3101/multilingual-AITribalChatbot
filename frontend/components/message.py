import streamlit as st
from html import escape
from markdown_it import MarkdownIt
import re
from components.response_formatter import format_for_display

def normalize_assistant_markdown(content):
    """Repair common Markdown layout damage from translated responses."""
    content = str(content or "").replace("\r\n", "\n").replace("\r", "\n")
    # Repair literal line-break escape sequences returned by some voice paths.
    content = content.replace("\\n", "\n")
    # Put Markdown headings on their own lines.
    content = re.sub(r"(?m)(?<!^)\s*(#{1,6}\s+)", r"\n\n\1", content)
    # Unescape Markdown markers that arrive literally escaped (e.g. \\*\\*text\\*\\*).
    content = re.sub(r"\\([*_#`])", r"\1", content)
    # Repair spaces inserted just inside bold markers by translation.
    content = re.sub(r"\*\*\s+", "**", content)
    content = re.sub(r"\s+\*\*", "**", content)
    # Restore line breaks when headings or numbered sections were flattened together.
    content = re.sub(r"(?<!\n)\s+(#{1,6}\s+)", r"\n\n\1", content)
    content = re.sub(r"(?<=[.!?])\s+(?=(?:\d+[.)])\s+\*?\*?[A-Z])", r"\n\n", content)
    content = re.sub(r"(?<!\n)\s+(?=\d+[.)]\s+\*?\*?[A-Z][^\n]{1,70}(?:\*\*)?\s)", r"\n\n", content)
    # Separate list markers and numbered items that have been flattened.
    content = re.sub(r"(?m)(?<!^)\s+([-*]\s+)", r"\n\1", content)
    content = re.sub(r"(?m)^([-*])(?=\*\*)", r"\1 ", content)
    content = re.sub(r"(?m)^(\d+[.)])(?=\*\*)", r"\1 ", content)
    return content.strip()

def html_block(content):
    """
    Remove indentation/newlines before sending HTML
    to Streamlit Markdown.
    """
    content = " ".join(
        line.strip()
        for line in content.splitlines()
        if line.strip()
    )
    st.markdown(
        content,
        unsafe_allow_html=True
    )
def apply_message_ui():
    st.markdown(
        """
        <style>
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
            line-height: 1.35;
            margin: 0.9rem 0 0.5rem;
        }
        .assistant-message h1 { font-size: 1.35rem; }
        .assistant-message h2 { font-size: 1.2rem; }
        .assistant-message h3 { font-size: 1.05rem; }
        .assistant-message p { margin: 0.45rem 0 0.75rem; }
        .assistant-message ul,
        .assistant-message ol {
            padding-left: 1.5rem;
            margin: 0.4rem 0 0.8rem;
        }
        .assistant-message li { margin: 0.2rem 0; }
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
            color: #e2e8f0;
            margin: 12px 0;
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
    rendered_content = markdown_renderer.render(normalized_content)

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
                <div class="assistant-message">
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
