
"""Generate a professional PDF interview report using ReportLab."""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF


# -- Colour palette ----------------------------------------------------------

_HEADER_BG = colors.HexColor("#1a237e")
_BAR_FILL = colors.HexColor("#3f51b5")
_BAR_BG = colors.HexColor("#e8eaf6")
_TEXT_DARK = colors.HexColor("#212121")

_SCORE_LABELS = [
    ("technical_strength", "Technical Strength"),
    ("communication", "Communication"),
    ("confidence", "Confidence"),
    ("problem_solving", "Problem Solving"),
    ("relevance", "Relevance"),
    ("clarity", "Clarity"),
]


# -- Helpers ------------------------------------------------------------------

def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontSize=22, textColor=colors.white, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SubHead", parent=styles["Heading2"],
        fontSize=14, textColor=_HEADER_BG, spaceBefore=14, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "BodyText2", parent=styles["BodyText"],
        fontSize=10, leading=14, textColor=_TEXT_DARK,
    ))
    return styles


def _score_bars(metrics: dict) -> Drawing:
    """Return a Drawing with horizontal bars for the 6 scores."""
    bar_w = 300
    bar_h = 14
    row_h = 28
    label_w = 140
    d = Drawing(label_w + bar_w + 50, row_h * len(_SCORE_LABELS) + 10)

    for i, (key, label) in enumerate(_SCORE_LABELS):
        y = (len(_SCORE_LABELS) - 1 - i) * row_h + 5
        score = min(max(int(metrics.get(key, 50)), 0), 100)

        # Label
        d.add(String(0, y + 2, label, fontSize=9, fillColor=_TEXT_DARK))

        # Background bar
        d.add(Rect(label_w, y, bar_w, bar_h, fillColor=_BAR_BG,
                    strokeColor=None))

        # Filled bar
        filled_w = bar_w * score / 100
        d.add(Rect(label_w, y, filled_w, bar_h, fillColor=_BAR_FILL,
                    strokeColor=None))

        # Score text
        d.add(String(label_w + bar_w + 6, y + 2, f"{score}",
                      fontSize=9, fillColor=_TEXT_DARK))

    return d


# -- Public API ---------------------------------------------------------------

def generate_pdf_report(
    candidate_name: str,
    job_title: str,
    report_data: dict,
    conversations: list,
) -> bytes:
    """Build a PDF and return its bytes."""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = _build_styles()
    story: list = []

    # --- Header table (coloured banner) ------------------------------------
    header_data = [[
        Paragraph("Interview Report", styles["ReportTitle"]),
    ]]
    header_table = Table(header_data, colWidths=[doc.width])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _HEADER_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Meta info
    story.append(Paragraph(
        f"<b>Candidate:</b> {candidate_name} &nbsp;&nbsp; "
        f"<b>Position:</b> {job_title} &nbsp;&nbsp; "
        f"<b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d')}",
        styles["BodyText2"],
    ))
    story.append(Spacer(1, 12))

    # --- Metrics section ----------------------------------------------------
    metrics = report_data.get("metrics", {})
    story.append(Paragraph("Performance Metrics", styles["SubHead"]))
    story.append(_score_bars(metrics))
    story.append(Spacer(1, 12))

    # --- Overall summary ----------------------------------------------------
    summary = report_data.get("summary", {})
    story.append(Paragraph("Overall Summary", styles["SubHead"]))
    story.append(Paragraph(
        summary.get("overall_summary", "N/A"), styles["BodyText2"],
    ))
    story.append(Spacer(1, 8))

    # --- Key strengths ------------------------------------------------------
    strengths = summary.get("key_strengths", [])
    if strengths:
        story.append(Paragraph("Key Strengths", styles["SubHead"]))
        for s in strengths:
            story.append(Paragraph(f"&bull; {s}", styles["BodyText2"]))
        story.append(Spacer(1, 6))

    # --- Improvement areas --------------------------------------------------
    areas = summary.get("improvement_areas", [])
    if areas:
        story.append(Paragraph("Areas for Improvement", styles["SubHead"]))
        for a in areas:
            story.append(Paragraph(f"&bull; {a}", styles["BodyText2"]))
        story.append(Spacer(1, 6))

    # --- Conversation Q&A ---------------------------------------------------
    if conversations:
        story.append(Paragraph("Interview Conversation", styles["SubHead"]))
        for idx, conv in enumerate(conversations, 1):
            q = conv.get("question", "N/A")
            a = conv.get("answer", conv.get("transcript", "N/A"))
            story.append(Paragraph(
                f"<b>Q{idx}:</b> {q}", styles["BodyText2"],
            ))
            story.append(Paragraph(
                f"<b>A{idx}:</b> {a}", styles["BodyText2"],
            ))
            story.append(Spacer(1, 6))

    # --- Build PDF ----------------------------------------------------------
    doc.build(story)
    return buf.getvalue()
