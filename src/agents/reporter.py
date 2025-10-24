from model import TravelState
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def _text_to_pdf_bytes(title: str, body: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 80, title)
    c.setFont("Helvetica", 11)
    y = height - 110
    for line in body.split("\n"):
        if y < 60:
            c.showPage()
            y = height - 60
        c.drawString(50, y, line)
        y -= 16
    c.save()
    buffer.seek(0)
    return buffer.read()

def reporter_node(state: TravelState) -> Dict[str, Any]:
    print(state.itinerary_text)
    if not state.itinerary_text:
        return {"error": "reporter: no itinerary_text"}

    title = f"Itinerary for {state.city} ({state.days} days)"
    pdf_bytes = _text_to_pdf_bytes(title, state.itinerary_text)
    return {"itinerary_pdf_bytes": pdf_bytes, "status": "reporter_completed"}
