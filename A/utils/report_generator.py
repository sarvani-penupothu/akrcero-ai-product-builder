"""PDF generation utilities leveraging ReportLab."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

BRAND_BLUE = colors.HexColor("#0077FF")
TEXT_COLOR = colors.HexColor("#0A0A0A")

ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"


def _build_header(c: canvas.Canvas, doc_width: float, doc_height: float) -> None:
    logo_path = ASSETS_PATH / "logo.png"
    if logo_path.exists():
        c.drawImage(str(logo_path), inch, doc_height - inch * 1.5, width=120, height=40, mask="auto")
    c.setFillColor(BRAND_BLUE)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(inch, doc_height - inch * 1.75, "Akcero AI Product Builder")
    c.setFont("Helvetica", 12)
    c.setFillColor(TEXT_COLOR)
    c.drawString(inch, doc_height - inch * 2.0, "From Idea to Product")
    c.line(inch, doc_height - inch * 2.1, doc_width - inch, doc_height - inch * 2.1)


def _section_title(text: str) -> Paragraph:
    style = ParagraphStyle(
        "SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=BRAND_BLUE,
        spaceAfter=6,
    )
    return Paragraph(text, style)


def _body_text(text: str) -> Paragraph:
    style = ParagraphStyle(
        "BodyText",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=TEXT_COLOR,
    )
    return Paragraph(text, style)


def build_pdf(blueprint_json: Dict[str, object], out_path: Path) -> str:
    """Render the product blueprint into a polished PDF and return its path."""

    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch * 1.8,
        bottomMargin=inch,
    )

    story = []

    styles = getSampleStyleSheet()
    summary = blueprint_json.get("summary", "")
    if summary:
        story.append(_section_title("Executive Summary"))
        story.append(_body_text(summary))
        story.append(Spacer(1, 0.3 * inch))

    sections = [
        ("Problem & Solution", blueprint_json.get("idea", {})),
        ("Business Model", blueprint_json.get("business_model", {})),
        ("Tech Stack & Architecture", blueprint_json.get("tech_stack", {})),
        ("UI/UX Suggestions", blueprint_json.get("ui_design", {})),
        ("Market & Competitors", blueprint_json.get("market_analysis", {})),
        ("Roadmap & Timeline", blueprint_json.get("timeline", {})),
    ]

    for title, data in sections:
        story.append(_section_title(title))
        if isinstance(data, dict):
            for key, value in data.items():
                label = key.replace("_", " ").title()
                if isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        bullets = []
                        for entry in value:
                            parts = [
                                f"{inner_key.replace('_', ' ').title()}: {inner_value}"
                                for inner_key, inner_value in entry.items()
                            ]
                            bullets.append("• " + " | ".join(parts))
                        story.append(
                            _body_text(f"<b>{label}</b><br/>{'<br/>'.join(bullets)}")
                        )
                    else:
                        bullets = "<br/>".join(f"• {item}" for item in value)
                        story.append(_body_text(f"<b>{label}</b><br/>{bullets}"))
                else:
                    story.append(_body_text(f"<b>{label}</b>: {value}"))
        else:
            story.append(_body_text(str(data)))
        story.append(Spacer(1, 0.25 * inch))

    footer_style = ParagraphStyle(
        "Footer",
        fontName="Helvetica-Oblique",
        fontSize=10,
        alignment=1,
        textColor=colors.grey,
    )
    footer_text = (
        f"Akcero — From Idea to Product | Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph(footer_text, footer_style))

    def on_first_page(canvas_obj: canvas.Canvas, doc_obj: SimpleDocTemplate) -> None:
        _build_header(canvas_obj, doc_obj.width + doc_obj.leftMargin + doc_obj.rightMargin, doc_obj.height + doc_obj.topMargin + doc_obj.bottomMargin)

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_first_page)
    return str(out_path)
