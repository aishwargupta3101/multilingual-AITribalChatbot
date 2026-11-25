"""Offline Mermaid-subset renderer for clean diagrams in Tribal AI responses."""
import html
import re
import streamlit as st

_FENCE = re.compile(r"(?ms)^[ \t]*```mermaid[ \t]*\n(.*?)^[ \t]*```[ \t]*$")
_NODE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*(?:\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\})")
_EDGE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*-->\s*([A-Za-z][A-Za-z0-9_]*)")


def extract_mermaid_blocks(markdown_text):
    diagrams = []
    def take(match):
        source = match.group(1).strip()
        if source:
            diagrams.append(source)
        return "\n\n"
    cleaned = _FENCE.sub(take, str(markdown_text or ""))
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip(), diagrams


def _parse_flowchart(source):
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    direction = "TD"
    if lines and lines[0].lower().startswith("flowchart"):
        direction = lines.pop(0).split()[-1].upper()
    nodes, edges = {}, []
    for line in lines:
        if line.startswith("%%") or line.startswith("classDef") or line.startswith("style "):
            continue
        # Remove simple edge labels and self loops; they are rendered as notes only
        # when explicitly supported by a future renderer.
        line = re.sub(r"\|[^|]*\|", " ", line)
        for m in _NODE.finditer(line):
            key = m.group(1)
            label = next((v for v in m.groups()[1:] if v), key).strip()
            nodes.setdefault(key, label)
        for a, b in _EDGE.findall(line):
            if a != b:
                edges.append((a, b))
            nodes.setdefault(a, a)
            nodes.setdefault(b, b)
    return direction, nodes, list(dict.fromkeys(edges))


def _wrap_label(label, max_chars=23):
    words = str(label).split()
    rows, current = [], ""
    for word in words:
        if current and len(current) + len(word) + 1 > max_chars:
            rows.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        rows.append(current)
    return rows[:3] or [""]


def flowchart_svg(source):
    direction, nodes, edges = _parse_flowchart(source)
    if not nodes:
        return ""
    keys = list(nodes)
    # Lay out in simple rows/columns. Predictable spacing is preferable to
    # malformed browser-side Mermaid syntax and keeps labels legible.
    horizontal = direction in {"LR", "RL"}
    card_w, card_h, gap = 210, 76, 54
    n = len(keys)
    if horizontal:
        cols, rows = min(n, 4), (n + 3) // 4
    else:
        cols, rows = min(n, 2), (n + 1) // 2
    width = 34 + cols * card_w + (cols - 1) * gap
    height = 40 + rows * card_h + (rows - 1) * gap
    if horizontal:
        positions = {k: (17 + (i % cols) * (card_w + gap), 20 + (i // cols) * (card_h + gap)) for i,k in enumerate(keys)}
    else:
        positions = {k: (17 + (i % cols) * (card_w + gap), 20 + (i // cols) * (card_h + gap)) for i,k in enumerate(keys)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Concept flow diagram" style="width:100%;height:auto;display:block">',
        '<defs><marker id="tribal-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#43845b"/></marker></defs>',
        '<rect width="100%" height="100%" rx="16" fill="#f6faf7"/>'
    ]
    # Edges first so they sit behind the node cards.
    for a,b in edges:
        if a not in positions or b not in positions:
            continue
        ax,ay=positions[a]; bx,by=positions[b]
        x1,y1=ax+card_w/2,ay+card_h/2
        x2,y2=bx+card_w/2,by+card_h/2
        if horizontal:
            x1 = ax+card_w if bx >= ax else ax
            x2 = bx if bx >= ax else bx+card_w
            y1, y2 = ay+card_h/2, by+card_h/2
        else:
            y1 = ay+card_h if by >= ay else ay
            y2 = by if by >= ay else by+card_h
            x1, x2 = ax+card_w/2, bx+card_w/2
        parts.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="#43845b" stroke-width="2.4" fill="none" marker-end="url(#tribal-arrow)"/>')
    for i,k in enumerate(keys):
        x,y=positions[k]
        fill = "#e7f4eb" if i % 2 == 0 else "#edf5f8"
        parts.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="{fill}" stroke="#9bc8a8" stroke-width="1.4"/>')
        rows_text=_wrap_label(nodes[k])
        start_y=y+card_h/2-(len(rows_text)-1)*9+5
        for j,line in enumerate(rows_text):
            parts.append(f'<text x="{x+card_w/2}" y="{start_y+j*19}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="600" fill="#244633">{html.escape(line)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def render_mermaid_diagrams(diagrams):
    """Render diagrams without a CDN, iframe, or GPU requirement."""
    for source in diagrams or []:
        svg = flowchart_svg(source)
        if svg:
            st.markdown(
                '<div class="tribal-visual-card"><div class="tribal-visual-label">VISUAL EXPLANATION</div>'
                + svg + '</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("A diagram was requested, but its structure could not be interpreted. The explanation is still available above.")
