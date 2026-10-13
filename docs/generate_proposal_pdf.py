"""
B2B Client Travel Proposal (Quotation) Generator in PDF format.
Generates a branded, professional travel itinerary proposal for clients,
including FCM Persona breakdown, recommended packages, cost estimates, and XAI rationale.
Uses DejaVu Sans TTF fonts bundled in docs/fonts/ for 100% Greek Unicode support.
"""
import io
import os
import sys
from typing import Dict, List, Any
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu Sans fonts from docs/fonts/ for full Greek Unicode coverage
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
DEJAVU_REGULAR = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
DEJAVU_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")
DEJAVU_ITALIC = os.path.join(FONTS_DIR, "DejaVuSans-Italic.ttf")

ARIAL_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ARIAL_ITALIC = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

if os.path.exists(DEJAVU_REGULAR) and os.path.exists(DEJAVU_BOLD):
    pdfmetrics.registerFont(TTFont('DejaVuGreek', DEJAVU_REGULAR))
    pdfmetrics.registerFont(TTFont('DejaVuGreek-Bold', DEJAVU_BOLD))
    pdfmetrics.registerFont(TTFont('DejaVuGreek-Italic', DEJAVU_ITALIC))
    FONT_NORMAL = 'DejaVuGreek'
    FONT_BOLD = 'DejaVuGreek-Bold'
    FONT_ITALIC = 'DejaVuGreek-Italic'
elif os.path.exists(ARIAL_REGULAR):
    pdfmetrics.registerFont(TTFont('ArialGreek', ARIAL_REGULAR))
    pdfmetrics.registerFont(TTFont('ArialGreek-Bold', ARIAL_BOLD))
    pdfmetrics.registerFont(TTFont('ArialGreek-Italic', ARIAL_ITALIC))
    FONT_NORMAL = 'ArialGreek'
    FONT_BOLD = 'ArialGreek-Bold'
    FONT_ITALIC = 'ArialGreek-Italic'
else:
    FONT_NORMAL = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'


class ProposalCanvas(canvas.Canvas):
    """Custom canvas for branded header and footer on travel proposals."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont(FONT_NORMAL, 8)
        self.setFillColor(colors.HexColor("#7f8c8d"))

        # Header bar
        self.drawString(54, 805, "FUZZYTRAVEL AI | ΕΠΙΣΗΜΗ ΕΞΑΤΟΜΙΚΕΥΜΕΝΗ ΤΑΞΙΔΙΩΤΙΚΗ ΠΡΟΣΦΟΡΑ")
        self.setStrokeColor(colors.HexColor("#1e3799"))
        self.setLineWidth(1)
        self.line(54, 798, 540, 798)

        # Footer bar
        self.line(54, 45, 540, 45)
        self.drawString(54, 34, "FuzzyTravel Agency Concierge • Εμπειρία Ταξιδιών Υψηλής Ακρίβειας")
        self.drawRightString(540, 34, f"Σελίδα {self._pageNumber} από {page_count}")
        self.restoreState()


def create_travel_proposal_pdf(
    client_name: str,
    agent_name: str,
    user_query: Dict[str, float],
    fcm_data: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    proposal_notes: str = ""
) -> bytes:
    """Generates the proposal PDF and returns it as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'PropTitle',
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0c2461"),
        spaceAfter=4
    )
    style_subtitle = ParagraphStyle(
        'PropSub',
        fontName=FONT_NORMAL,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4a69bd"),
        spaceAfter=12
    )
    style_h2 = ParagraphStyle(
        'PropH2',
        fontName=FONT_BOLD,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e3799"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'PropBody',
        fontName=FONT_NORMAL,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=4
    )
    style_badge = ParagraphStyle(
        'PropBadge',
        fontName=FONT_BOLD,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e3799"),
        alignment=1
    )
    style_meta_label = ParagraphStyle(
        'PropMetaL',
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#34495e")
    )
    style_meta_val = ParagraphStyle(
        'PropMetaV',
        fontName=FONT_NORMAL,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2c3e50")
    )

    story = []

    # 1. Header Information Block
    story.append(Paragraph("ΕΠΙΣΗΜΗ ΤΑΞΙΔΙΩΤΙΚΗ ΠΡΟΣΦΟΡΑ &amp; ΠΛΑΝΟ", style_title))
    today_str = datetime.now().strftime("%d/%m/%Y")
    ref_num = f"QT-{datetime.now().strftime('%Y%m%d')}-{abs(hash(client_name)) % 10000:04d}"
    story.append(Paragraph(f"Αρ. Προσφοράς: <b>{ref_num}</b> | Ημερομηνία Έκδοσης: <b>{today_str}</b>", style_subtitle))

    meta_table_data = [
        [
            Paragraph("<b>Στοιχεία Πελάτη:</b>", style_meta_label),
            Paragraph(client_name or "Εκτιμώμενος Ταξιδιώτης", style_meta_val),
            Paragraph("<b>Σύμβουλος Ταξιδιού:</b>", style_meta_label),
            Paragraph(agent_name or "FuzzyTravel Specialist", style_meta_val)
        ],
        [
            Paragraph("<b>Προϋπολογισμός:</b>", style_meta_label),
            Paragraph(f"~{int(user_query.get('budget', 1200))}€ / άτομο", style_meta_val),
            Paragraph("<b>Επιθυμητή Διάρκεια:</b>", style_meta_label),
            Paragraph(f"{int(user_query.get('duration', 5))} Ημέρες", style_meta_val)
        ],
        [
            Paragraph("<b>Προτιμώμενο Κλίμα:</b>", style_meta_label),
            Paragraph(f"{int(user_query.get('climate', 22))}°C (Θερμοκρασία)", style_meta_val),
            Paragraph("<b>Κατάσταση Προσφοράς:</b>", style_meta_label),
            Paragraph("<font color='#27ae60'><b>Ενεργή - Εξατομικευμένη</b></font>", style_meta_val)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[100, 150, 110, 150])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 2. Traveler Persona DNA (FCM Analysis)
    story.append(Paragraph("1. Ανάλυση Ταξιδιωτικού Προφίλ (FCM Soft Persona DNA)", style_h2))
    dom_persona = fcm_data.get("dominant_persona", "Ισορροπημένος Εξερευνητής")
    dom_pct = fcm_data.get("dominant_pct", 50.0)
    story.append(Paragraph(
        f"Με βάση την ασαφή μοντελοποίηση των προτιμήσεών σας, το κυρίαρχο τουριστικό σας προφίλ προσδιορίζεται ως: "
        f"<b><font color='#1e3799'>{dom_persona} ({dom_pct}%)</font></b>. "
        "Το σύστημά μας αναγνωρίζει ότι κάθε ταξιδιώτης διαθέτει σύνθετη συμπεριφορά, γι' αυτό και καταγράφει το διάνυσμα συμμετοχής σας:",
        style_body
    ))

    # Persona breakdown row
    p_headers = [Paragraph(f"<b>{p['greek_name'][:18]}...</b>", style_meta_label) for p in fcm_data.get("all_personas", [])]
    p_values = [Paragraph(f"<b>{p['membership_pct']}%</b>", style_badge) for p in fcm_data.get("all_personas", [])]
    if p_headers:
        t_persona = Table([p_headers, p_values], colWidths=[102] * len(p_headers))
        t_persona.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e8f0fe")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_persona)

    story.append(Spacer(1, 12))

    # 3. Top Tailored Destination Packages
    story.append(Paragraph("2. Προτεινόμενα Εξατομικευμένα Πακέτα Διακοπών", style_h2))

    top_n_print = recommendations[:3] if recommendations else []
    for rank, rec in enumerate(top_n_print, 1):
        dest = rec["destination"]
        score = rec["final_score"]
        est_cost = rec["estimated_trip_cost"]
        pkg_title = dest.get("agency_package", f"Ειδικό Πακέτο {dest['name']}")

        dest_header_data = [
            [
                Paragraph(f"<b>#{rank}. {dest['name']} ({dest['country']})</b> — {dest.get('region', '')}", ParagraphStyle('DH1', fontName=FONT_BOLD, fontSize=11, textColor=colors.HexColor("#0c2461"))),
                Paragraph(f"<b>Ταίριασμα: {score}%</b>", ParagraphStyle('DH2', fontName=FONT_BOLD, fontSize=11, textColor=colors.HexColor("#1b5e20"), alignment=2))
            ]
        ]
        t_dhead = Table(dest_header_data, colWidths=[380, 130])
        t_dhead.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor("#1e3799"))
        ]))

        pkg_desc_data = [
            [Paragraph(f"<b>Τίτλος Πακέτου:</b> <i>{pkg_title}</i>", style_body)],
            [Paragraph(f"<b>Εκτιμώμενο Συνολικό Κόστος:</b> ~{est_cost}€ / άτομο | <b>Ιδανική Εποχή:</b> {dest.get('best_season', 'Όλο το έτος')}", style_body)],
            [Paragraph(f"<b>Περιγραφή:</b> {dest.get('description', '')}", style_body)],
            [Paragraph(f"<b>Κορυφαία Αξιοθέατα:</b> {', '.join(dest.get('highlights', []))}", style_body)]
        ]

        # Rationale bullets
        reasons_text = " • ".join(rec.get("rationale", []))
        if reasons_text:
            pkg_desc_data.append([Paragraph(f"<b>💡 Γιατί σας ταιριάζει (AI Rationale):</b> <font color='#1e3799'>{reasons_text}</font>", style_body)])

        t_pdesc = Table(pkg_desc_data, colWidths=[510])
        t_pdesc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))

        card_flowables = [t_dhead, t_pdesc, Spacer(1, 8)]
        story.append(KeepTogether(card_flowables))

    if proposal_notes:
        story.append(Spacer(1, 4))
        story.append(Paragraph("3. Ειδικές Σημειώσεις Συμβούλου", style_h2))
        story.append(Paragraph(f"<i>{proposal_notes}</i>", style_body))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Όροι &amp; Κράτηση:</b> Οι ανωτέρω προτάσεις έχουν παραχθεί εξατομικευμένα με το Ασαφές Έμπειρο Σύστημα FuzzyTravel AI. "
        "Οι τιμές και η διαθεσιμότητα επιβεβαιώνονται κατά την οριστική δέσμευση των εισιτηρίων και της διαμονής. "
        "Επικοινωνήστε με τον ταξιδιωτικό σας πράκτορα για ολοκλήρωση της κράτησης.",
        ParagraphStyle('PropFooterNote', fontName=FONT_NORMAL, fontSize=7.5, leading=10, textColor=colors.HexColor("#64748b"))
    ))

    doc.build(story, canvasmaker=ProposalCanvas)
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    from core.recommender import HybridTourismRecommender
    rec_engine = HybridTourismRecommender()
    t_query = {"budget": 1200.0, "climate": 24.0, "duration": 5.0, "culture": 8.0, "adventure": 4.0, "relaxation": 7.0, "nightlife": 6.0}
    res = rec_engine.recommend(t_query, top_n=3)
    pdf_bytes = create_travel_proposal_pdf(
        "Παναγιώτης Μπεκιάρης",
        "Ταξιδιωτικός Σύμβουλος",
        t_query,
        res["fcm_profiling"],
        res["recommendations"],
        "Περιλαμβάνει πρωινό και απευθείας πτήσεις."
    )
    sample_out = os.path.join(os.path.dirname(__file__), "Sample_Travel_Proposal.pdf")
    with open(sample_out, "wb") as f:
        f.write(pdf_bytes)
    print(f"Sample Travel Proposal successfully saved to: {sample_out}")
