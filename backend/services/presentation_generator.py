import json
import os
import re
from io import BytesIO
from typing import Any

import httpx
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.util import Inches, Pt

NAVY = RGBColor(18, 32, 56)
INK = RGBColor(35, 47, 62)
MUTED = RGBColor(95, 109, 126)
PAPER = RGBColor(248, 250, 253)
WHITE = RGBColor(255, 255, 255)
TEAL = RGBColor(0, 150, 136)
BLUE = RGBColor(57, 105, 200)
GOLD = RGBColor(230, 166, 54)
CORAL = RGBColor(220, 95, 86)
ACCENTS = [TEAL, BLUE, GOLD, CORAL]


class PresentationGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model = os.getenv(
            "PRESENTATION_OPENROUTER_MODEL",
            os.getenv("EDUCATION_OPENROUTER_MODEL", "openrouter/free"),
        ).strip()
        self.url = "https://openrouter.ai/api/v1/chat/completions"


    @staticmethod
    def _response_content(response: httpx.Response, operation: str) -> str:
        """Validate an OpenRouter response and return its textual content."""
        try:
            payload = response.json()
        except ValueError as exc:
            preview = (response.text or "")[:500]
            raise ValueError(
                f"OpenRouter returned non-JSON during {operation} "
                f"(HTTP {response.status_code}): {preview or 'empty body'}"
            ) from exc

        if response.is_error:
            error = payload.get("error", payload) if isinstance(payload, dict) else payload
            detail = json.dumps(error, ensure_ascii=False)[:1000]
            raise ValueError(
                f"OpenRouter request failed during {operation} "
                f"(HTTP {response.status_code}): {detail}"
            )

        if not isinstance(payload, dict):
            raise ValueError(
                f"OpenRouter returned an unexpected response during {operation}."
            )

        if payload.get("error"):
            detail = json.dumps(payload["error"], ensure_ascii=False)[:1000]
            raise ValueError(
                f"OpenRouter reported an error during {operation}: {detail}"
            )

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            detail = json.dumps(payload, ensure_ascii=False)[:1000]
            raise ValueError(
                f"OpenRouter returned no choices during {operation}: {detail}"
            )

        choice = choices[0]
        message = choice.get("message") if isinstance(choice, dict) else None
        content = message.get("content") if isinstance(message, dict) else None

        if isinstance(content, list):
            content = "\n".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict)
                and isinstance(block.get("text"), str)
            )

        if not isinstance(content, str) or not content.strip():
            reason = (
                choice.get("finish_reason")
                if isinstance(choice, dict)
                else None
            )
            model = payload.get("model", "configured model")
            if reason == "length":
                raise ValueError(
                    f"OpenRouter exhausted the output budget during {operation} "
                    f"for {model} before returning presentation JSON. "
                    "Use a model with a larger completion limit or reduce slide count."
                )
            raise ValueError(
                f"OpenRouter returned no usable text during {operation} "
                f"(finish_reason={reason!r}, model={model})."
            )

        return content.strip()

    async def generate_slides(
        self,
        topic: str = "",
        slide_count: int = 8,
        source_text: str = "",
        output_language: str = "auto",
    ) -> dict:
        """Generate one compact slide per request to reduce free-model truncation."""
        slide_count = max(3, min(int(slide_count or 8), 10))
        topic = str(topic or "").strip() or "Presentation"
        source_text = str(source_text or "").strip()
        output_language = str(output_language or "auto").strip().lower()

        language_instruction = (
            "Detect the source language and write in that language."
            if output_language in {"", "auto", "same as input"}
            else f"Write in {output_language}."
        )

        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured.")

        slide_plan = [
            "Introduction and definition",
            "Core concepts",
            "How it works",
            "Practical applications",
            "Benefits and opportunities",
            "Challenges and limitations",
            "Best practices",
            "Summary and next steps",
            "Further examples",
            "Conclusion",
        ]
        slides = []

        async with httpx.AsyncClient(timeout=90) as client:
            for index in range(slide_count):
                slide_topic = slide_plan[index] if index < len(slide_plan) else f"Part {index + 1}"
                source_excerpt = source_text[:1800]
                prompt = f"""Write ONE educational presentation slide explaining {topic}.
Slide {index + 1} of {slide_count}; focus: {slide_topic}.
Language: {language_instruction}
Source material (use accurately, if provided):
{source_excerpt or "(No source supplied; use reliable general knowledge.)"}

Return only compact valid JSON:
{{"title":"short informative title","bullets":["complete explanatory sentence","complete explanatory sentence","complete explanatory sentence"],"key_takeaway":"one clear sentence"}}

Rules:
- Explain, do not ask questions or give instructions to the presenter.
- Exactly 3 complete, factual, meaningful bullets, each about 12-22 words.
- Use plain language and a concrete example where appropriate.
- No generic filler, placeholders, or repeated topic wording.
- No markdown fences or text outside the JSON.
"""
                content = None
                last_error = None
                # Retry once with a shorter prompt/output budget if the model truncates.
                for attempt in range(2):
                    try:
                        response = await client.post(
                            self.url,
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json",
                                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
                                "X-Title": "Tribal AI Presentation Generator",
                            },
                            json={
                                "model": self.model,
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": "Return concise, accurate educational slide content as valid JSON only."
                                    },
                                    {
                                        "role": "user",
                                        "content": prompt if attempt == 0 else (
                                            f"Explain {topic} for slide {index + 1}. "
                                            f"Return JSON with title, exactly 3 complete explanatory bullets, "
                                            f"and key_takeaway. Language: {language_instruction}. "
                                            f"Source: {source_text[:500] or 'Use reliable general knowledge.'}"
                                        ),
                                    },
                                ],
                                "temperature": 0.25,
                                "max_tokens": 900 if attempt == 0 else 550,
                            },
                        )
                        content = self._response_content(response, f"slide {index + 1}")
                        content = re.sub(
                            r"^\s*```(?:json)?\s*|\s*```\s*$",
                            "",
                            content.strip(),
                        )
                        parsed = json.loads(content)
                        if not isinstance(parsed, dict):
                            raise ValueError("The AI returned a non-object slide.")
                        bullets = parsed.get("bullets", [])
                        if not isinstance(bullets, list):
                            bullets = [bullets]
                        bullets = [str(b).strip() for b in bullets if str(b or "").strip()]
                        if len(bullets) < 3:
                            raise ValueError("The AI returned fewer than 3 explanatory bullets.")
                        slides.append({
                            "title": str(parsed.get("title") or f"{topic}: {slide_topic}"),
                            "bullets": bullets[:3],
                            "layout": "bullets",
                            "visual_type": "none",
                            "visual_data": [],
                            "example": "",
                            "key_takeaway": str(parsed.get("key_takeaway") or ""),
                            "source": "",
                        })
                        break
                    except (ValueError, json.JSONDecodeError) as exc:
                        last_error = exc
                        content = None
                if content is None:
                    raise ValueError(
                        f"Could not generate slide {index + 1} after a compact retry: {last_error}"
                    )

        return {
            "title": topic[:1].upper() + topic[1:],
            "subtitle": f"A clear explanation of {topic}",
            "slides": slides,
            "sources": [],
        }

    def create_pptx(self, data: dict) -> BytesIO:
        """Create a styled PowerPoint from generated slide data."""
        if not isinstance(data, dict) or not isinstance(data.get("slides"), list):
            raise ValueError("Invalid presentation data: expected a slides list.")

        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        prs.core_properties.title = str(data.get("title", "Presentation"))
        prs.core_properties.subject = str(data.get("subtitle", ""))

        # Title slide
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = NAVY
        self._shape(slide, 0.85, 1.0, 0.14, 4.9, TEAL)
        self._text(slide, data.get("title", "Presentation"), 1.35, 1.45, 10.8, 1.8,
                  34, WHITE, True)
        self._text(slide, data.get("subtitle", ""), 1.38, 3.45, 10.2, 1.0,
                  19, RGBColor(205, 218, 232))
        self._text(slide, "TRIBAL AI • PRESENTATION GENERATOR", 1.38, 6.35,
                  10.5, 0.35, 10, RGBColor(180, 196, 214), True)

        total = len(data["slides"])
        for idx, item in enumerate(data["slides"], 1):
            if not isinstance(item, dict):
                continue
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = PAPER
            self._shape(slide, 0, 0, 13.333, 0.15, TEAL)
            self._text(slide, item.get("title", f"Slide {idx}"), 0.75, 0.45,
                      11.9, 0.8, 27, NAVY, True)

            layout = str(item.get("layout", item.get("visual_type", "bullets"))).lower()
            visual = item.get("visual_data") or []
            bullets = item.get("bullets") or []
            if layout == "statistic" and visual:
                stat = visual[0] if isinstance(visual, list) else visual
                if not isinstance(stat, dict):
                    stat = {"value": str(stat)}
                self._text(slide, stat.get("value", ""), 1.0, 1.8, 11.3, 1.7,
                          46, TEAL, True, PP_ALIGN.CENTER)
                self._text(slide, stat.get("context", stat.get("label", "")),
                          1.2, 3.7, 10.9, 1.3, 20, NAVY, True, PP_ALIGN.CENTER)
                self._text(slide, stat.get("source", ""), 1.2, 5.25, 10.9, 0.4,
                          10, MUTED, False, PP_ALIGN.CENTER)
            elif layout in {"cards", "comparison", "process", "timeline"} and visual:
                cards = visual[:4] if isinstance(visual, list) else [visual]
                n = len(cards)
                gap = 0.25
                card_w = (11.7 - gap * (n - 1)) / n
                for j, card in enumerate(cards):
                    if not isinstance(card, dict):
                        card = {"text": str(card)}
                    x = 0.8 + j * (card_w + gap)
                    self._shape(slide, x, 1.75, card_w, 4.55, WHITE, rounded=True)
                    self._shape(slide, x, 1.75, card_w, 0.12, ACCENTS[j % len(ACCENTS)])
                    heading = card.get("title", card.get("label", f"Item {j+1}"))
                    body = card.get("text", card.get("description", card.get("value", "")))
                    self._text(slide, heading, x + 0.18, 2.1, card_w - 0.36, 0.75,
                              16, NAVY, True)
                    self._text(slide, body, x + 0.18, 2.95, card_w - 0.36, 2.95,
                              13, INK)
            elif layout == "quote":
                quote = item.get("example", "")
                self._shape(slide, 1.0, 1.8, 11.3, 4.5, WHITE, rounded=True)
                self._text(slide, f'“{quote}”', 1.45, 2.25, 10.4, 2.6,
                          24, NAVY, True, PP_ALIGN.CENTER)
            else:
                self._bullets(slide, bullets)

            takeaway = str(item.get("key_takeaway", "")).strip()
            if takeaway:
                self._shape(slide, 0.8, 6.42, 11.7, 0.48, RGBColor(230, 242, 241), rounded=True)
                self._text(slide, f"TAKEAWAY  {takeaway}", 1.0, 6.45, 11.3, 0.38,
                          11, TEAL, True)
            self._shape(slide, 0.55, 7.12, 12.2, 0.012, RGBColor(220, 226, 234))
            self._text(slide, str(item.get("source", ""))[:160], 0.62, 7.15,
                      10.7, 0.2, 8, MUTED)
            self._text(slide, f"{idx} / {total}", 11.65, 7.15, 1.0, 0.2,
                      9, MUTED, False, PP_ALIGN.RIGHT)

        output = BytesIO()
        prs.save(output)
        output.seek(0)
        return output

    @staticmethod
    def _shape(slide, x, y, w, h, color, rounded=False):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(y), Inches(w), Inches(h)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
        return shape

    @staticmethod
    def _text(slide, text, x, y, w, h, size=18, color=INK, bold=False,
              align=PP_ALIGN.LEFT):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = Inches(0.08)
        tf.margin_right = Inches(0.08)
        tf.margin_top = Inches(0.05)
        tf.margin_bottom = Inches(0.05)
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = str(text or "")
        run.font.name = "Aptos"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        return box

    @staticmethod
    def _bullets(slide, bullets):
        box = slide.shapes.add_textbox(Inches(0.9), Inches(1.55), Inches(11.5), Inches(4.85))
        tf = box.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = Inches(0.1)
        tf.margin_right = Inches(0.1)
        for i, bullet in enumerate([str(x).strip() for x in (bullets or []) if str(x).strip()][:6]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = bullet
            p.level = 0
            p.font.name = "Aptos"
            p.font.size = Pt(18 if len(bullets) <= 4 else 17)
            p.font.color.rgb = INK
            p.space_after = Pt(14)
            p.bullet = True
