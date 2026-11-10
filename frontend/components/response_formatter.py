"""
Language-agnostic response formatting helpers for Tribal AI Chatbot.
Presentation-only: does not translate, summarize, or intentionally remove content.
"""
import re
from typing import Optional

SUPPORTED_LANGUAGE_ALIASES = {
    "en": "english", "eng": "english", "hi": "hindi", "hin": "hindi",
    "mni": "manipuri", "mni_beng": "manipuri", "manipuri_beng": "manipuri",
    "manipuri_bengali": "manipuri", "meitei": "manipuri",
    "mni_mtei": "manipuri_mtei", "meitei_mayek": "manipuri_mtei",
    "manipuri_meitei": "manipuri_mtei", "tai_khamti": "tai_khamti",
}

def normalize_language(language: Optional[str]) -> str:
    value = str(language or "").strip().lower().replace("-", "_").replace(" ", "_")
    return SUPPORTED_LANGUAGE_ALIASES.get(value, value)

def _repair_heading_spacing(text: str) -> str:
    lines, output, in_fence = text.split("\n"), [], False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line)
            continue
        if not in_fence:
            match = re.match(r"^(\s{0,3}#{1,6})(?!#)(?=\S)(\S.*)$", line)
            if match:
                line = f"{match.group(1)} {match.group(2)}"
        output.append(line)
    return "\n".join(output)



def _format_flat_java_code(code: str) -> str:
    """Best-effort formatting for a flattened, single-line Java code fence."""
    code = code.replace("\\n", "\n").replace("\\r", "\n")
    if "\n" in code.strip() or not code.strip():
        return code
    out, indent, parens = [], 0, 0
    buf, quote, block_comment, line_comment = "", None, False, False
    i = 0

    def flush():
        nonlocal buf
        value = buf.strip()
        if value:
            out.append("    " * max(indent, 0) + value)
        buf = ""

    while i < len(code):
        ch = code[i]
        nxt = code[i + 1] if i + 1 < len(code) else ""
        if line_comment:
            buf += ch
            if ch == "\n":
                flush()
                line_comment = False
            i += 1
            continue
        if block_comment:
            buf += ch
            if ch == "*" and nxt == "/":
                buf += nxt
                i += 2
                block_comment = False
                flush()
                continue
            i += 1
            continue
        if quote:
            buf += ch
            if ch == "\\\\" and nxt:
                buf += nxt
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in ('"', "\'"):
            quote = ch
            buf += ch
        elif ch == "/" and nxt == "*":
            buf += "/*"
            i += 2
            block_comment = True
            continue
        elif ch == "/" and nxt == "/":
            buf += "//"
            i += 2
            line_comment = True
            continue
        elif ch == "(":
            parens += 1
            buf += ch
        elif ch == ")":
            parens = max(0, parens - 1)
            buf += ch
        elif ch == "{":
            buf += ch
            flush()
            indent += 1
        elif ch == "}":
            flush()
            indent = max(0, indent - 1)
            buf = "}"
            # Keep punctuation after a closing brace with that brace.
            j = i + 1
            while j < len(code) and code[j].isspace():
                j += 1
            if j < len(code) and code[j] in ";,":
                buf += code[j]
                i = j
            flush()
        elif ch == ";" and parens == 0:
            buf += ch
            flush()
        else:
            buf += ch
        i += 1
    flush()
    # Avoid returning a worse result for code the simple formatter cannot improve.
    return "\n".join(out) if len(out) > 1 else code


def _repair_fenced_code_blocks(text: str) -> str:
    """Preserve code fences and format flattened Java source inside them."""
    pattern = re.compile(
        r"(?P<opening>^[ \t]*```(?P<info>[^\n]*)\n)"
        r"(?P<code>.*?)"
        r"(?P<closing>^[ \t]*```[ \t]*$)",
        re.MULTILINE | re.DOTALL,
    )

    def replace(match):
        info = match.group("info").strip().lower()
        language = info.split()[0] if info else ""
        code = match.group("code")
        first = code.lstrip().lower()
        looks_like_java = (
            language in {"java", "java17", "java-17"}
            or (not language and (
                first.startswith(("import java.", "public class ", "class "))
                and ("class " in first or "interface " in first)
            ))
        )
        if looks_like_java and len(code.splitlines()) <= 1:
            code = _format_flat_java_code(code)
        return match.group("opening") + code + match.group("closing")

    return pattern.sub(replace, text)



def _remove_rendering_artifacts(text: str) -> str:
    """Remove only HTML-tag-only fences and stray standalone HTML tags from prose."""
    tag = re.compile(
        r"^\s*</?(?:div|span|p|section|article|main|header|footer|pre|code|"
        r"strong|em|ul|ol|li|table|thead|tbody|tr|td|th|br|hr)(?:\s+[^<>]*)?\s*/?>\s*$",
        re.IGNORECASE,
    )
    fence = re.compile(r"(?ms)^[ \t]*```[ \t]*(?:html|xml|markup)?[ \t]*\n(?P<body>.*?)^[ \t]*```[ \t]*$")
    def strip_html_fence(m):
        rows = [x.strip() for x in m.group("body").splitlines() if x.strip()]
        return "" if rows and all(tag.fullmatch(x) for x in rows) else m.group(0)
    text = fence.sub(strip_html_fence, text)
    rows, output, in_fence = text.split("\n"), [], False
    for row in rows:
        if row.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(row)
        elif not in_fence and tag.fullmatch(row.strip()):
            continue
        else:
            output.append(row)
    text = "\n".join(output)
    # Do not attempt to reconstruct code from serialized object placeholders.
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def format_response(text: str, language: Optional[str] = None) -> str:
    """Normalize Markdown layout for English, Hindi, Manipuri, Tai Khamti, and other languages."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2028", "\n").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\u00a0", " ")
    text = _remove_rendering_artifacts(text)
    text = _repair_fenced_code_blocks(text)
    text = _repair_heading_spacing(text)

    # Repair heading markers that translation has joined to Gujarati
    # or other Indic-script words. Leave fenced code blocks untouched.
    lines, repaired, in_fence = text.split("\n"), [], False

    for line in lines:
        stripped = line.lstrip()

        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            repaired.append(line)
            continue

        if not in_fence:
            # Turn inline heading markers into proper Markdown headings.
            line = re.sub(
                r"(?<!\S)(#{1,6})(?=\S)",
                r"\n\1 ",
                line,
            )
            # Remove stray emphasis markers at the end of a line.
            line = re.sub(r"[ \t]+\*{1,2}[ \t]*$", "", line)
            line = re.sub(r"[ \t]+_{1,2}[ \t]*$", "", line)

        repaired.append(line)

    text = "\n".join(repaired)

    lines, output, in_fence = text.split("\n"), [], False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line.rstrip())
            continue
        if not in_fence:
            # Put headings, bullets and numbered items on their own lines
            # when a model/translation has flattened Markdown into a paragraph.
            line = re.sub(r"\s+(?=#{1,6}\s)", "\n\n", line)
            line = re.sub(r"(?<=[.!?。！？])\s+(?=(?:[-*+]|\d+[.)])\s+)", "\n", line)
            # Give common South Asian-script MCQ options their own lines when
            # translation returns the question and options as one long line.
            # This only inserts presentation newlines; it does not rewrite text.
            line = re.sub(
                r"(?<!^)[ \t]+(?=(?:\([কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়]\)|"
                r"[কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়][.)]))[ \t]*",
                "\\n",
                line,
            )
            # Repair malformed translated bold markers while preserving words.
            line = re.sub(r"\*\*[ \t]+(.*?)[ \t]+\*\*", r"\1", line)
            if line.count("**") % 2:
                line = line.replace("**", "")
        output.append(line.rstrip())
    text = "\n".join(output)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def format_for_display(text: str, language: Optional[str] = None) -> str:
    return format_response(text, language)

def format_for_voice(text: str, language: Optional[str] = None) -> str:
    """Return plain text for TTS while preserving words and paragraph breaks."""
    formatted = format_response(text, language)
    if not formatted:
        return ""
    output, in_fence = [], False
    for line in formatted.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
            line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
            line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", line)
            line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
            line = re.sub(r"(\*\*|__)(.*?)\1", r"\2", line)
            line = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)", r"\1", line)
            line = re.sub(r"(?<!_)_(?!_)(.*?)_(?!_)", r"\1", line)
            line = re.sub(r"`([^`]*)`", r"\1", line)
        output.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(output)).strip()

if __name__ == "__main__":
    examples = [
        ("english", "##Artificial Intelligence\n\nAI is **useful**.\n- Example one"),
        ("hindi", "##कृत्रिम बुद्धिमत्ता\n\nAI उपयोगी है।\n- पहला उदाहरण"),
        ("manipuri", "##ꯃꯤꯇꯩ\n\nꯃꯁꯤ **ꯐꯖꯩ**।"),
        ("manipuri_mtei", "##ꯃꯤꯇꯩ\n\nꯃꯁꯤ ꯐꯖꯩ।"),
        ("tai_khamti", "##Example\n\nA paragraph.\n1. First item"),
    ]
    for language, sample in examples:
        print(f"--- {language} ---")
        print(format_response(sample, language))
        print("[TTS]", format_for_voice(sample, language))
