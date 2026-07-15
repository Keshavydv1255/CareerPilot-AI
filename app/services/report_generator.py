from datetime import datetime
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _safe(value) -> str:
    return escape(str(value or ""))


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dbe3f0"))
    canvas.line(18 * mm, 13 * mm, 192 * mm, 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(18 * mm, 8 * mm, "CareerPilot AI - Confidential Candidate Report")
    canvas.drawRightString(192 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _bullet_items(title, items, heading, body):
    output = [Paragraph(title, heading)]
    if items:
        for item in items:
            output.append(Paragraph(f"• {_safe(item)}", body))
    else:
        output.append(Paragraph("No items identified.", body))
    return output


def generate_report(
    filename,
    analysis,
    skill_gap,
    roadmap,
    questions,
    resume_text,
    original_filename="resume.pdf",
):
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleBrand",
        parent=styles["Title"],
        fontSize=27,
        leading=32,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4f46e5"),
        spaceAfter=10,
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=10,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
    )
    resume_body = ParagraphStyle(
        "ResumeBody",
        parent=body,
        fontSize=9,
        leading=12,
        spaceAfter=2,
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title="CareerPilot AI Resume Report",
        author="CareerPilot AI",
    )

    source_label = "Gemini AI" if analysis.get("analysis_source") == "gemini" else "Reliable local ATS fallback"
    score = int(analysis.get("score", 0) or 0)

    story = [
        Spacer(1, 12 * mm),
        Paragraph("CareerPilot AI", title),
        Paragraph("AI Resume Analysis Report", subtitle),
        Spacer(1, 5 * mm),
        Table(
            [
                ["Resume file", _safe(original_filename)],
                ["Generated", datetime.now().strftime("%d %B %Y, %I:%M %p")],
                ["Analysis source", source_label],
            ],
            colWidths=[45 * mm, 105 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2ff")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 9),
                ]
            ),
        ),
        Spacer(1, 10 * mm),
        Paragraph("Candidate Snapshot", heading),
    ]

    score_table = Table(
        [
            ["ATS Score", "Detected Skills", "Learning Time"],
            [f"{score}%", str(len(analysis.get("skills", []))), skill_gap.get("duration", "Not available")],
        ],
        colWidths=[50 * mm, 50 * mm, 50 * mm],
    )
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 1), (-1, 1), 15),
                ("PADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story += [score_table, Spacer(1, 8 * mm)]

    if analysis.get("summary"):
        story += [Paragraph("Professional Summary", heading), Paragraph(_safe(analysis["summary"]), body)]

    story += _bullet_items("Detected Skills", analysis.get("skills", []), heading, body)
    story += _bullet_items("Strengths", analysis.get("strengths", []), heading, body)
    story += _bullet_items("Weaknesses", analysis.get("weaknesses", []), heading, body)
    story += _bullet_items("Recommended Improvements", analysis.get("suggestions", []), heading, body)
    story += _bullet_items("Missing Skills", skill_gap.get("missing_skills", []), heading, body)

    story.append(Paragraph("Personalized Career Roadmap", heading))
    roadmap_rows = [["Week", "Learning Goal"]]
    for item in roadmap:
        roadmap_rows.append(
            [
                Paragraph(f"Week {_safe(item.get('week', ''))}", body),
                Paragraph(_safe(item.get("topic", "")), body),
            ]
        )
    roadmap_table = Table(roadmap_rows, colWidths=[30 * mm, 120 * mm], repeatRows=1)
    roadmap_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story += [roadmap_table, Spacer(1, 6 * mm)]

    story.append(Paragraph("Interview Preparation", heading))
    for group in ("technical", "project", "hr"):
        block = [Paragraph(group.title() + " Questions", styles["Heading3"])]
        group_items = questions.get(group, [])
        if group_items:
            block += [Paragraph(f"• {_safe(item)}", body) for item in group_items]
        else:
            block.append(Paragraph("No questions generated.", body))
        story.append(KeepTogether(block))

    # The complete extracted resume is intentionally included as an appendix.
    story += [PageBreak(), Paragraph("Appendix: Complete Extracted Resume", title)]
    story.append(
        Paragraph(
            "The text below is the full content extracted from the uploaded resume. Formatting may differ from the original PDF, but no resume section is intentionally omitted.",
            subtitle,
        )
    )
    for line in resume_text.splitlines():
        if line.strip():
            story.append(Paragraph(_safe(line), resume_body))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
