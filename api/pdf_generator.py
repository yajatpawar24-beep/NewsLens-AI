"""
PDF Generator for NewsLens AI Briefings
========================================

Generates professional PDF reports from briefing data.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def generate_briefing_pdf(briefing_data: Dict[str, Any], output_path: str) -> str:
    """
    Generate a professional PDF briefing report.

    Args:
        briefing_data: Dictionary containing briefing information
        output_path: Path where PDF should be saved

    Returns:
        Path to the generated PDF file
    """

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Get styles
    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#f59e0b'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        leftIndent=20,
        fontName='Helvetica',
        leading=13
    )

    # Build content
    content = []

    # Header
    content.append(Paragraph("NewsLens AI", title_style))
    content.append(Paragraph(
        f"Intelligence Briefing • Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style
    ))
    content.append(Spacer(1, 0.3 * inch))

    # Add horizontal line
    line_table = Table([['']],  colWidths=[6.5 * inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#f59e0b')),
    ]))
    content.append(line_table)
    content.append(Spacer(1, 0.2 * inch))

    # Executive Summary
    content.append(Paragraph("Executive Summary", heading_style))
    summary = briefing_data.get('summary', 'No summary available')
    # Split long summary into paragraphs for better readability
    summary_paragraphs = summary.split('\n\n') if '\n\n' in summary else [summary]
    for para in summary_paragraphs:
        if para.strip():
            content.append(Paragraph(para.strip(), body_style))
            content.append(Spacer(1, 0.1 * inch))

    content.append(Spacer(1, 0.2 * inch))

    # Key Points
    content.append(Paragraph("What You Need to Know", heading_style))
    key_points = briefing_data.get('key_points', [])
    for idx, point in enumerate(key_points, 1):
        bullet_text = f"<b>{idx}.</b> {point}"
        content.append(Paragraph(bullet_text, bullet_style))

    content.append(Spacer(1, 0.3 * inch))

    # Strategic Questions
    questions = briefing_data.get('questions', [])
    if questions:
        content.append(Paragraph("Strategic Questions to Consider", heading_style))
        for idx, question in enumerate(questions, 1):
            question_text = f"<b>Q{idx}:</b> {question}"
            content.append(Paragraph(question_text, bullet_style))

        content.append(Spacer(1, 0.3 * inch))

    # Insights (if available)
    insights = briefing_data.get('insights', {})
    if insights:
        consensus = insights.get('consensus', [])
        contradictions = insights.get('contradictions', [])

        if consensus:
            content.append(Paragraph("Key Consensus Points", heading_style))
            for point in consensus:
                content.append(Paragraph(f"• {point}", bullet_style))
            content.append(Spacer(1, 0.2 * inch))

        if contradictions:
            content.append(Paragraph("Contradictions Identified", heading_style))
            for point in contradictions:
                content.append(Paragraph(f"• {point}", bullet_style))
            content.append(Spacer(1, 0.2 * inch))

    # Footer
    content.append(Spacer(1, 0.5 * inch))
    line_table2 = Table([['']],  colWidths=[6.5 * inch])
    line_table2.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cccccc')),
    ]))
    content.append(line_table2)
    content.append(Spacer(1, 0.1 * inch))

    footer_text = """
    <font size=8 color="#666666">
    <b>NewsLens AI</b> • Multi-Modal Business Intelligence Platform<br/>
    ET AI Hackathon 2026 • Problem Statement #8<br/>
    <i>This briefing was auto-generated using advanced AI agents.
    8x faster reading • 90% consolidation • Production-ready intelligence</i>
    </font>
    """
    content.append(Paragraph(footer_text, subtitle_style))

    # Build PDF
    doc.build(content)

    return output_path


def generate_briefing_pdf_simple(briefing_data: Dict[str, Any], output_path: str) -> str:
    """
    Generate a simple text-based PDF briefing (fallback).

    Args:
        briefing_data: Dictionary containing briefing information
        output_path: Path where PDF should be saved

    Returns:
        Path to the generated PDF file
    """
    from reportlab.pdfgen import canvas

    # Create PDF
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(72, height - 72, "NewsLens AI Intelligence Briefing")

    # Date
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 92, f"Generated: {datetime.now().strftime('%B %d, %Y')}")

    # Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 130, "Executive Summary")
    c.setFont("Helvetica", 10)

    # Simple text wrapping
    summary = briefing_data.get('summary', 'No summary available')
    y = height - 150
    for line in summary.split('\n')[:20]:  # First 20 lines
        if y < 100:  # Leave space for footer
            break
        c.drawString(72, y, line[:80])  # Truncate long lines
        y -= 15

    c.save()
    return output_path
