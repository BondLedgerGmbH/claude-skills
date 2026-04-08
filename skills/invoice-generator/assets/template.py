"""
Modern Black Invoice Template.

Style constants, colors, fonts, and layout helpers for the invoice generator.
Keep all visual design decisions in this file so the main script stays
focused on data wiring and orchestration.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# ============ BRAND COLORS ============
DARK = colors.HexColor("#2C3E4C")       # navy - borders, accents, headers
TEXT = colors.HexColor("#1a1a1a")       # primary text
MUTED = colors.HexColor("#6b7280")      # labels, secondary text
LIGHT_LINE = colors.HexColor("#c8cdd3") # horizontal rules

# ============ PAGE DIMENSIONS ============
PAGE_W, PAGE_H = A4
BORDER_INSET = 10 * mm         # distance from page edge to dark frame
BORDER_WIDTH = 2.5             # stroke width of frame
CONTENT_MARGIN_L = 22 * mm     # inner content left margin
CONTENT_MARGIN_R = 22 * mm
CONTENT_MARGIN_T = 20 * mm
CONTENT_MARGIN_B = 20 * mm
CONTENT_WIDTH = PAGE_W - CONTENT_MARGIN_L - CONTENT_MARGIN_R

# ============ PARAGRAPH STYLES ============
# Invoke via styles() after importing to get fresh instances.
def build_styles():
    s = {}
    s["invoice_label"] = ParagraphStyle(
        "IL", fontName="Helvetica", fontSize=13,
        textColor=DARK, leading=15,
    )
    s["wordmark"] = ParagraphStyle(
        "WM", fontName="Times-Roman", fontSize=28,
        textColor=DARK, leading=32,
    )
    s["body"] = ParagraphStyle(
        "B", fontName="Helvetica", fontSize=9,
        textColor=TEXT, leading=12,
    )
    s["body_right"] = ParagraphStyle(
        "BR", fontName="Helvetica", fontSize=9,
        textColor=TEXT, leading=12, alignment=TA_RIGHT,
    )
    s["pill"] = ParagraphStyle(
        "PILL", fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.white, leading=13,
    )
    s["th"] = ParagraphStyle(
        "TH", fontName="Helvetica", fontSize=11,
        textColor=DARK, leading=13,
    )
    s["th_right"] = ParagraphStyle(
        "THR", fontName="Helvetica", fontSize=11,
        textColor=DARK, leading=13, alignment=TA_RIGHT,
    )
    s["td"] = ParagraphStyle(
        "TD", fontName="Helvetica", fontSize=9.5,
        textColor=TEXT, leading=13,
    )
    s["td_right"] = ParagraphStyle(
        "TDR", fontName="Helvetica", fontSize=9.5,
        textColor=TEXT, leading=13, alignment=TA_RIGHT,
    )
    s["tot_label"] = ParagraphStyle(
        "TL", fontName="Helvetica", fontSize=10,
        textColor=MUTED, alignment=TA_RIGHT, leading=15,
    )
    s["tot_value"] = ParagraphStyle(
        "TV", fontName="Helvetica", fontSize=10,
        textColor=TEXT, alignment=TA_RIGHT, leading=15,
    )
    s["tot_label_bold"] = ParagraphStyle(
        "TLB", fontName="Helvetica-Bold", fontSize=10,
        textColor=TEXT, alignment=TA_RIGHT, leading=15,
    )
    s["tot_value_bold"] = ParagraphStyle(
        "TVB", fontName="Helvetica-Bold", fontSize=10,
        textColor=TEXT, alignment=TA_RIGHT, leading=15,
    )
    s["balance"] = ParagraphStyle(
        "BAL", fontName="Helvetica-Bold", fontSize=12,
        textColor=TEXT, alignment=TA_RIGHT, leading=16,
    )
    s["app_label"] = ParagraphStyle(
        "AL", fontName="Helvetica", fontSize=13,
        textColor=DARK, leading=15,
    )
    s["app_title"] = ParagraphStyle(
        "AT", fontName="Times-Roman", fontSize=22,
        textColor=DARK, leading=26,
    )
    s["td_wrap"] = ParagraphStyle(
        "TDW", fontName="Helvetica", fontSize=9.5,
        textColor=TEXT, leading=13,
        wordWrap="CJK",  # enables aggressive word wrapping for long strings
        splitLongWords=True,
    )
    return s


def draw_border_and_page_number(canvas, doc, total_pages):
    """Draw the dark frame around each page + page number bottom-right."""
    canvas.saveState()
    # Frame
    canvas.setStrokeColor(DARK)
    canvas.setLineWidth(BORDER_WIDTH)
    canvas.rect(
        BORDER_INSET, BORDER_INSET,
        PAGE_W - 2 * BORDER_INSET, PAGE_H - 2 * BORDER_INSET,
        stroke=1, fill=0,
    )
    # Page number
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(
        PAGE_W - BORDER_INSET - 6 * mm,
        BORDER_INSET + 6 * mm,
        f"{doc.page}/{total_pages}",
    )
    canvas.restoreState()
