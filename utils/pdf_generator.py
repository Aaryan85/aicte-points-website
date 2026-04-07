"""
utils/pdf_generator.py - PDF Report & Certificate Generator
AICTE Activity & Points Management System

Generates professional AICTE points reports and participation certificates
using the reportlab library.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config import REPORT_DIR, CERTIFICATE_DIR, MAX_AICTE_POINTS


# =============================================================================
# Color Palette
# =============================================================================
PRIMARY_COLOR = colors.HexColor('#6c5ce7')
SECONDARY_COLOR = colors.HexColor('#00b894')
DARK_COLOR = colors.HexColor('#2d3436')
LIGHT_COLOR = colors.HexColor('#dfe6e9')
ACCENT_COLOR = colors.HexColor('#0984e3')


def generate_report(student, total_points, category_points, event_history):
    """
    Generate a comprehensive AICTE Points Report PDF.

    Args:
        student: User object for the student
        total_points: Total AICTE points earned
        category_points: Dict of {category: points}
        event_history: List of event participation records

    Returns:
        str: Absolute path to the generated PDF file
    """
    filename = f"report_{student.roll_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------------------------------------------------------
    # Custom Styles
    # -------------------------------------------------------------------------
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=PRIMARY_COLOR,
        spaceAfter=6, alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=12, textColor=DARK_COLOR,
        spaceAfter=20, alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=14, textColor=PRIMARY_COLOR,
        spaceBefore=15, spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'],
        fontSize=10, textColor=DARK_COLOR, spaceAfter=4
    )
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.gray,
        alignment=TA_CENTER
    )

    # -------------------------------------------------------------------------
    # Header
    # -------------------------------------------------------------------------
    elements.append(Paragraph("AICTE Activity Points Report", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style
    ))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=PRIMARY_COLOR,
        spaceAfter=15
    ))

    # -------------------------------------------------------------------------
    # Student Details
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Student Information", heading_style))

    student_data = [
        ['Full Name:', student.full_name, 'Roll Number:', student.roll_number or 'N/A'],
        ['Department:', student.department or 'N/A', 'Email:', student.email],
        ['Username:', student.username, 'Member Since:', 
         student.created_at.strftime('%B %Y') if student.created_at else 'N/A'],
    ]

    student_table = Table(student_data, colWidths=[90, 170, 90, 170])
    student_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('FONT', (3, 0), (3, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), PRIMARY_COLOR),
        ('TEXTCOLOR', (2, 0), (2, -1), PRIMARY_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # Points Summary
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Points Summary", heading_style))

    progress = min((total_points / MAX_AICTE_POINTS) * 100, 100)

    summary_data = [
        ['Total AICTE Points:', f'{total_points} / {MAX_AICTE_POINTS}'],
        ['Progress:', f'{progress:.1f}%'],
        ['Status:', 'COMPLETED ✓' if total_points >= MAX_AICTE_POINTS else 'IN PROGRESS'],
    ]

    summary_table = Table(summary_data, colWidths=[150, 370])
    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
        ('TEXTCOLOR', (0, 0), (0, -1), DARK_COLOR),
        ('TEXTCOLOR', (1, 2), (1, 2),
         SECONDARY_COLOR if total_points >= MAX_AICTE_POINTS else ACCENT_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, LIGHT_COLOR),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Category-wise Breakdown
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Category-wise Points Breakdown", heading_style))

    categories = ['technical', 'cultural', 'social', 'sports']
    cat_header = ['Category', 'Points Earned']
    cat_data = [cat_header]
    for cat in categories:
        pts = category_points.get(cat, 0)
        cat_data.append([cat.capitalize(), str(pts)])
    cat_data.append(['Total', str(total_points)])

    cat_table = Table(cat_data, colWidths=[260, 260])
    cat_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -2), 'Helvetica', 10),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(cat_table)
    elements.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # Event History Table
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Event Participation History", heading_style))

    if event_history:
        evt_header = ['#', 'Event', 'Category', 'Date', 'Status', 'Points']
        evt_data = [evt_header]
        for i, evt in enumerate(event_history, 1):
            status = 'Attended' if evt['attended'] else 'Registered'
            date_str = evt['event_date'].strftime('%d %b %Y') if evt['event_date'] else 'N/A'
            evt_data.append([
                str(i),
                str(evt['title'])[:35],
                str(evt['category']).capitalize(),
                date_str,
                status,
                str(evt['points_awarded'])
            ])

        evt_table = Table(evt_data, colWidths=[30, 180, 80, 80, 70, 60])
        evt_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (4, 0), (5, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_COLOR),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(evt_table)
    else:
        elements.append(Paragraph("No events participated yet.", normal_style))

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_COLOR))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(
        "This is an auto-generated report from the AICTE Activity & Points Management System. "
        "For queries, contact the administration office.",
        footer_style
    ))

    # Build PDF
    doc.build(elements)
    return filepath


def generate_certificate(student, event):
    """
    Generate a participation certificate PDF.

    Args:
        student: User object for the student
        event: dict with event details

    Returns:
        str: Absolute path to the generated PDF file
    """
    filename = f"cert_{student.roll_number}_{event['id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(CERTIFICATE_DIR, filename)

    # Use landscape A4 for certificate
    doc = SimpleDocTemplate(
        filepath, pagesize=landscape(A4),
        rightMargin=50, leftMargin=50,
        topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------------------------------------------------------
    # Custom Styles
    # -------------------------------------------------------------------------
    cert_title = ParagraphStyle(
        'CertTitle', parent=styles['Title'],
        fontSize=36, textColor=PRIMARY_COLOR,
        spaceAfter=10, alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    cert_subtitle = ParagraphStyle(
        'CertSubtitle', parent=styles['Normal'],
        fontSize=16, textColor=DARK_COLOR,
        spaceAfter=25, alignment=TA_CENTER
    )
    cert_body = ParagraphStyle(
        'CertBody', parent=styles['Normal'],
        fontSize=14, textColor=DARK_COLOR,
        alignment=TA_CENTER, leading=22
    )
    cert_name = ParagraphStyle(
        'CertName', parent=styles['Title'],
        fontSize=28, textColor=ACCENT_COLOR,
        spaceBefore=15, spaceAfter=15, alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    cert_event = ParagraphStyle(
        'CertEvent', parent=styles['Normal'],
        fontSize=18, textColor=PRIMARY_COLOR,
        spaceBefore=10, spaceAfter=10, alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    cert_footer = ParagraphStyle(
        'CertFooter', parent=styles['Normal'],
        fontSize=10, textColor=colors.gray,
        alignment=TA_CENTER
    )

    # -------------------------------------------------------------------------
    # Certificate Content
    # -------------------------------------------------------------------------

    # Top border
    elements.append(HRFlowable(
        width="100%", thickness=3, color=PRIMARY_COLOR, spaceAfter=20
    ))

    elements.append(Spacer(1, 20))

    # Institution name
    elements.append(Paragraph("AICTE Activity & Points Management System", cert_subtitle))

    # Title
    elements.append(Paragraph("Certificate of Participation", cert_title))

    elements.append(HRFlowable(
        width="40%", thickness=1, color=SECONDARY_COLOR, spaceAfter=20
    ))

    # Body
    elements.append(Paragraph("This is to certify that", cert_body))

    elements.append(Paragraph(student.full_name, cert_name))

    dept_text = f"Department: {student.department}" if student.department else ""
    roll_text = f"Roll Number: {student.roll_number}" if student.roll_number else ""
    elements.append(Paragraph(f"{dept_text} | {roll_text}", cert_body))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("has successfully participated in", cert_body))

    elements.append(Paragraph(event['title'], cert_event))

    event_date = event['event_date']
    if hasattr(event_date, 'strftime'):
        date_str = event_date.strftime('%B %d, %Y')
    else:
        date_str = str(event_date)

    elements.append(Paragraph(
        f"held on {date_str} at {event.get('venue', 'N/A')}",
        cert_body
    ))

    elements.append(Spacer(1, 5))
    elements.append(Paragraph(
        f"Category: {event.get('category', 'N/A').capitalize()} | "
        f"AICTE Points Awarded: {event.get('points', 0)}",
        cert_body
    ))

    elements.append(Spacer(1, 40))

    # Signature line
    sig_data = [
        ['_' * 30, '', '_' * 30],
        ['Event Organizer', '', 'Administration'],
    ]
    sig_table = Table(sig_data, colWidths=[200, 200, 200])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 1), (-1, 1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.gray),
        ('TOPPADDING', (0, 1), (-1, 1), 5),
    ]))
    elements.append(sig_table)

    elements.append(Spacer(1, 20))

    # Bottom border
    elements.append(HRFlowable(
        width="100%", thickness=3, color=PRIMARY_COLOR, spaceBefore=10
    ))

    elements.append(Paragraph(
        f"Certificate ID: AICTE-{student.id}-{event['id']}-{datetime.now().strftime('%Y%m%d')} | "
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
        cert_footer
    ))

    # Build PDF
    doc.build(elements)
    return filepath
