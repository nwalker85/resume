#!/usr/bin/env python3
"""
Resume PDF generator from markdown source.
Converts a resume markdown file to a professional PDF using ReportLab.

Usage:
    python3 scripts/build-resume.py <resume.md> <out.pdf>

Example:
    python3 scripts/build-resume.py ../../../docs/40-personal/portfolio/_portfolio-root/nathan-walker-resume-se-leadership.md public/resume.pdf
"""

import sys
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas


def parse_markdown(md_text):
    """
    Parse markdown resume structure.
    Returns a list of (type, content) tuples.
    Types: 'h1', 'h2', 'h3', 'para', 'bullet', 'hr', 'table'
    """
    lines = md_text.split('\n')
    elements = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines (except after elements that need spacing)
        if not stripped:
            i += 1
            continue

        # H1
        if stripped.startswith('# '):
            elements.append(('h1', stripped[2:].strip()))
            i += 1
        # H2
        elif stripped.startswith('## '):
            elements.append(('h2', stripped[3:].strip()))
            i += 1
        # H3
        elif stripped.startswith('### '):
            elements.append(('h3', stripped[4:].strip()))
            i += 1
        # Horizontal rule
        elif stripped.startswith('---'):
            elements.append(('hr', None))
            i += 1
        # Table (markdown table)
        elif '|' in stripped:
            # Collect table lines
            table_lines = [stripped]
            i += 1
            while i < len(lines) and '|' in lines[i].strip():
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) > 1:
                elements.append(('table', table_lines))
        # Bullet (starts with -)
        elif stripped.startswith('- '):
            elements.append(('bullet', stripped[2:].strip()))
            i += 1
        # Paragraph
        else:
            # Accumulate multi-line paragraphs
            para_lines = [stripped]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    break
                if next_line.startswith(('#', '|', '-', '---')):
                    break
                para_lines.append(next_line)
                i += 1
            if para_lines:
                elements.append(('para', ' '.join(para_lines)))

    return elements


def format_text(text):
    """
    Convert markdown inline formatting to ReportLab compatible text.
    **bold** -> <b>bold</b>
    Preserves other text as-is.
    """
    # Bold: **text** -> <b>text</b>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return text


def parse_table(table_lines):
    """
    Parse markdown table into rows.
    Returns list of rows, where each row is a list of cell texts.
    """
    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells:
            rows.append(cells)

    # Remove header separator row (all dashes)
    filtered_rows = []
    for row in rows:
        if not all(c.replace('-', '').replace(':', '') == '' for c in row):
            filtered_rows.append(row)

    return filtered_rows


def build_pdf(md_path, pdf_path):
    """Build resume PDF from markdown source."""

    md_text = Path(md_path).read_text(encoding='utf-8')
    elements_list = parse_markdown(md_text)

    # Set up PDF
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Margins
    margin = 0.75 * inch
    page_width, page_height = letter
    available_width = page_width - 2 * margin

    # Create document with custom page size accounting for margins
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    # Styles
    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c2c2c'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        borderPadding=0,
    )

    h3_style = ParagraphStyle(
        'H3Style',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#2c2c2c'),
        spaceAfter=4,
        spaceBefore=6,
        fontName='Helvetica-Bold',
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=12,
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leftIndent=18,
        leading=11,
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
        alignment=TA_CENTER,
        leading=10,
    )

    # Build story
    story = []

    for elem_type, content in elements_list:
        if elem_type == 'h1':
            story.append(Paragraph(format_text(content), name_style))

        elif elem_type == 'para':
            # Check if it's a contact info paragraph (contains @ or phone)
            if '@' in content or '•' in content:
                story.append(Paragraph(format_text(content), contact_style))
            else:
                story.append(Paragraph(format_text(content), body_style))

        elif elem_type == 'h2':
            story.append(Spacer(1, 0.08 * inch))
            story.append(Paragraph(format_text(content), h2_style))

        elif elem_type == 'h3':
            story.append(Paragraph(format_text(content), h3_style))

        elif elem_type == 'bullet':
            # Format bullet with a dash
            bullet_text = '• ' + format_text(content)
            story.append(Paragraph(bullet_text, bullet_style))

        elif elem_type == 'hr':
            story.append(Spacer(1, 0.12 * inch))

        elif elem_type == 'table':
            rows = parse_table(content)
            if rows:
                # Flatten all table cells to bullets, row by row, left then right,
                # skipping empty cells. Avoids ReportLab Table text-overflow issues.
                for row in rows:
                    for cell in row:
                        if cell.strip():
                            bullet_text = '• ' + format_text(cell.strip())
                            story.append(Paragraph(bullet_text, bullet_style))
                story.append(Spacer(1, 0.06 * inch))

    # Build PDF
    doc.build(story)
    return pdf_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2]

    try:
        result_path = build_pdf(md_file, pdf_file)
        print(f"✓ Generated: {result_path}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
