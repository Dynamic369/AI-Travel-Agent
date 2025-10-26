from model import TravelState
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from xml.sax.saxutils import escape
import io
import re

def _text_to_pdf_bytes(title: str, body: str) -> bytes:
    """Render wrapped itinerary text into a paginated PDF with margins, headings, and bullets."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=60,
        bottomMargin=60,
    )
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = styles["Heading1"]
    title_style.fontName = "Helvetica-Bold"
    title_style.fontSize = 18
    title_style.textColor = "#2C3E50"
    title_style.spaceAfter = 12
    
    # Day heading style
    day_style = ParagraphStyle(
        "DayHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor="#34495E",
        spaceBefore=12,
        spaceAfter=8,
        leftIndent=0,
    )
    
    # Body text style
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        spaceBefore=4,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    
    # Bullet style
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        leftIndent=20,
        bulletIndent=10,
    )

    story = []
    story.append(Paragraph(escape(title), title_style))
    story.append(Spacer(1, 0.3*inch))

    # Parse itinerary into structured sections
    lines = body.split("\n")
    current_section = []
    bullet_items = []
    
    # Patterns to detect day headings and bullets
    day_pattern = re.compile(r"^(Day\s+\d+|DAY\s+\d+)", re.IGNORECASE)
    bullet_pattern = re.compile(r"^\s*[-•*]\s+(.+)")
    
    for line in lines:
        line_stripped = line.strip()
        
        # Empty line: flush current section
        if not line_stripped:
            if bullet_items:
                story.append(ListFlowable(
                    [ListItem(Paragraph(escape(item), bullet_style)) for item in bullet_items],
                    bulletType='bullet',
                    start='•',
                ))
                bullet_items = []
            elif current_section:
                text = " ".join(current_section)
                story.append(Paragraph(escape(text), body_style))
                current_section = []
            story.append(Spacer(1, 0.1*inch))
            continue
        
        # Day heading
        if day_pattern.match(line_stripped):
            # Flush previous content
            if bullet_items:
                story.append(ListFlowable(
                    [ListItem(Paragraph(escape(item), bullet_style)) for item in bullet_items],
                    bulletType='bullet',
                    start='•',
                ))
                bullet_items = []
            elif current_section:
                text = " ".join(current_section)
                story.append(Paragraph(escape(text), body_style))
                current_section = []
            
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph(escape(line_stripped), day_style))
            continue
        
        # Bullet item
        bullet_match = bullet_pattern.match(line_stripped)
        if bullet_match:
            # Flush previous non-bullet section
            if current_section:
                text = " ".join(current_section)
                story.append(Paragraph(escape(text), body_style))
                current_section = []
            bullet_items.append(bullet_match.group(1))
            continue
        
        # Regular text
        if bullet_items:
            # Flush bullets before starting regular text
            story.append(ListFlowable(
                [ListItem(Paragraph(escape(item), bullet_style)) for item in bullet_items],
                bulletType='bullet',
                start='•',
            ))
            bullet_items = []
        
        current_section.append(line_stripped)
    
    # Flush remaining content
    if bullet_items:
        story.append(ListFlowable(
            [ListItem(Paragraph(escape(item), bullet_style)) for item in bullet_items],
            bulletType='bullet',
            start='•',
        ))
    elif current_section:
        text = " ".join(current_section)
        story.append(Paragraph(escape(text), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def reporter_node(state: TravelState) -> Dict[str, Any]:
    if not state.itinerary_text:
        return {"error": "reporter: no itinerary_text"}

    title = f"Itinerary for {state.city} ({state.days} days)"
    pdf_bytes = _text_to_pdf_bytes(title, state.itinerary_text)
    return {"itinerary_pdf_bytes": pdf_bytes, "status": "reporter_completed"}
