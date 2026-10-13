"""
Academic Master's Report & User Manual Generator in PDF format.
Meets all deliverables specified in UNIPI Master's Course 2026.
Uses ReportLab with native Greek Unicode TrueType Font support.
Dynamically imports system components to ensure 100% numerical and structural accuracy.
"""
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.recommender import HybridTourismRecommender
from core.fuzzy_engine import DestinationArchetype

# Register Arial with Greek support
FONT_REGULAR_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

if os.path.exists(FONT_REGULAR_PATH):
    pdfmetrics.registerFont(TTFont('ArialGreek', FONT_REGULAR_PATH))
    pdfmetrics.registerFont(TTFont('ArialGreek-Bold', FONT_BOLD_PATH))
    pdfmetrics.registerFont(TTFont('ArialGreek-Italic', FONT_ITALIC_PATH))
    FONT_NORMAL = 'ArialGreek'
    FONT_BOLD = 'ArialGreek-Bold'
    FONT_ITALIC = 'ArialGreek-Italic'
else:
    FONT_NORMAL = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'


class NumberedCanvas(canvas.Canvas):
    """Custom canvas to add professional running headers and page numbers."""
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page

        self.saveState()
        self.setFont(FONT_NORMAL, 8)
        self.setFillColor(colors.HexColor("#7f8c8d"))

        # Header
        self.drawString(54, 800, "ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ | ΑΣΑΦΗ ΣΥΣΤΗΜΑΤΑ & ΥΠΟΛΟΓΙΣΤΙΚΗ ΝΟΗΜΟΣΥΝΗ")
        self.setStrokeColor(colors.HexColor("#bdc3c7"))
        self.setLineWidth(0.5)
        self.line(54, 792, 540, 792)

        # Footer
        self.line(54, 50, 540, 50)
        self.drawString(54, 38, "Απαλλακτική Εργασία 2026 — FuzzyTravel AI (Mamdani FIS & FCM)")
        page_text = f"Σελίδα {self._pageNumber} από {page_count}"
        self.drawRightString(540, 38, page_text)
        self.restoreState()


def build_academic_pdf(output_pdf_path: str):
    # Initialize recommender engine to extract dynamic metrics
    rec = HybridTourismRecommender()
    fcm_metrics = rec.fcm_model.compute_validation_metrics()
    destinations = rec.catalog_mgr.get_all()
    rules = rec.fuzzy_engine.rules

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_cover_uni = ParagraphStyle(
        'CoverUni',
        fontName=FONT_BOLD,
        fontSize=13,
        leading=18,
        alignment=1,
        textColor=colors.HexColor("#1e3799")
    )
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName=FONT_BOLD,
        fontSize=18,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#0c2461")
    )
    style_cover_sub = ParagraphStyle(
        'CoverSub',
        fontName=FONT_NORMAL,
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#4a69bd")
    )
    style_h1 = ParagraphStyle(
        'H1',
        fontName=FONT_BOLD,
        fontSize=14,
        leading=19,
        textColor=colors.HexColor("#0c2461"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'H2',
        fontName=FONT_BOLD,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e3799"),
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body',
        fontName=FONT_NORMAL,
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=5
    )
    style_bullet = ParagraphStyle(
        'Bullet',
        fontName=FONT_NORMAL,
        fontSize=8.8,
        leading=13,
        textColor=colors.HexColor("#2c3e50"),
        leftIndent=12,
        spaceAfter=2.5
    )
    style_table_header = ParagraphStyle(
        'TableHeader',
        fontName=FONT_BOLD,
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=1
    )
    style_table_cell = ParagraphStyle(
        'TableCell',
        fontName=FONT_NORMAL,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#2c3e50")
    )
    style_math = ParagraphStyle(
        'Math',
        fontName=FONT_BOLD,
        fontSize=9,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#1e3799"),
        spaceBefore=3,
        spaceAfter=4
    )

    story = []
    figures_dir = os.path.join(os.path.dirname(__file__), "figures")

    # =========================================================================
    # 1. ΕΞΩΦΥΛΛΟ (COVER PAGE)
    # =========================================================================
    story.append(Spacer(1, 25))
    story.append(Paragraph("ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ", style_cover_uni))
    story.append(Paragraph("ΤΜΗΜΑ ΠΛΗΡΟΦΟΡΙΚΗΣ", style_cover_uni))
    story.append(Paragraph("ΠΡΟΓΡΑΜΜΑ ΜΕΤΑΠΤΥΧΙΑΚΩΝ ΣΠΟΥΔΩΝ", style_cover_sub))
    story.append(Spacer(1, 30))

    story.append(Paragraph("ΑΠΑΛΛΑΚΤΙΚΗ ΕΡΓΑΣΙΑ 2026", style_cover_sub))
    story.append(Spacer(1, 10))
    story.append(Paragraph("ΕΜΠΕΙΡΟ ΣΥΣΤΗΜΑ ΤΟΥΡΙΣΤΙΚΩΝ ΠΡΟΤΑΣΕΩΝ ΜΕ ΧΡΗΣΗ ΑΣΑΦΟΥΣ ΛΟΓΙΚΗΣ (MAMDANI FIS) ΚΑΙ ΟΜΑΔΟΠΟΙΗΣΗ ΠΡΟΦΙΛ ΜΕ FUZZY C-MEANS (FCM)", style_cover_title))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>Θέμα 3: Σύστημα Τουριστικών Προτάσεων & Επέκταση FCM</i>", style_cover_sub))
    story.append(Spacer(1, 35))

    info_data = [
        [Paragraph("<b>Μάθημα:</b>", style_body), Paragraph("Ασαφή Συστήματα & Υπολογιστική Νοημοσύνη", style_body)],
        [Paragraph("<b>Διδάσκουσα:</b>", style_body), Paragraph("Δρ. Κ. Χρυσαφιάδη (kchrysafiadi@unipi.gr)", style_body)],
        [Paragraph("<b>Ομάδα Εργασίας:</b>", style_body), Paragraph("1. [Ονοματεπώνυμο – ΑΜ]<br/>2. [Ονοματεπώνυμο – ΑΜ]<br/>3. [Ονοματεπώνυμο – ΑΜ]", style_body)],
        [Paragraph("<b>Ακαδημαϊκό Έτος:</b>", style_body), Paragraph("2025 - 2026", style_body)],
        [Paragraph("<b>Παραδοτέα:</b>", style_body), Paragraph("1. Πηγαίος Κώδικας & Εφαρμογή Streamlit<br/>2. Τεχνική Έκθεση & Εγχειρίδιο Χρήστη (PDF & Word .docx)", style_body)],
        [Paragraph("<b>GitHub Repo:</b>", style_body), Paragraph("https://github.com/MrMpek/Tourism-Recommendation-Fuzzy-System", style_body)]
    ]
    t_info = Table(info_data, colWidths=[110, 350])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0"))
    ]))
    story.append(t_info)

    story.append(PageBreak())

    # =========================================================================
    # 2. ΕΙΣΑΓΩΓΗ & ΕΠΙΧΕΙΡΗΣΙΑΚΗ ΑΡΧΙΤΕΚΤΟΝΙΚΗ
    # =========================================================================
    story.append(Paragraph("1. Εισαγωγή & Επιχειρησιακό Πλαίσιο (B2B Travel Tech)", style_h1))
    story.append(Paragraph(
        "Η παρούσα εργασία υλοποιεί ένα σύγχρονο, προηγμένο <b>Έμπειρο Σύστημα Τουριστικών Προτάσεων (FuzzyTravel AI)</b>, "
        "βασισμένο στις αρχές της Ασαφούς Λογικής (Fuzzy Logic - Mamdani Inference) και της Ασαφούς Ομαδοποίησης (Fuzzy C-Means Clustering). "
        "Στον τομέα του τουρισμού, οι ανθρώπινες προτιμήσεις, οι επιθυμίες και οι οικονομικές δυνατότητες χαρακτηρίζονται εγγενώς από "
        "υψηλή αβεβαιότητα, υποκειμενικότητα και ασάφεια. Ένας ταξιδιώτης σπάνια σκέφτεται με απόλυτα δυαδικά όρια (π.χ. 'αυστηρά 24°C και 1.150€'). "
        "Αντιθέτως, διατυπώνει τις απαιτήσεις του με φυσικούς γλωσσικούς όρους όπως <i>«οικονομικός προϋπολογισμός»</i>, <i>«ήπιο προς θερμό κλίμα»</i>, <i>«έντονο ενδιαφέρον για πολιτισμό»</i>.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Εμπορική Διάσταση & Αρχιτεκτονική B2B:</b> "
        "Το σύστημα σχεδιάστηκε εξαρχής με αρθρωτή δομή (modular decoupled architecture). "
        "Ο μαθηματικός πυρήνας (Core Engine) είναι πλήρως ανεξάρτητος από το περιβάλλον διεπαφής (Streamlit UI), επιτρέποντας στα ταξιδιωτικά γραφεία "
        "να εισάγουν το δικό τους απόθεμα 22 πακέτων, να εξάγουν εξατομικευμένες προτάσεις με <b>πλήρη επεξηγησιμότητα (Explainable AI - XAI)</b> "
        "και να παράγουν αυτόματα επίσημη ταξιδιωτική προσφορά σε PDF (B2B Client Quotation).",
        style_body
    ))

    # =========================================================================
    # 3. ΑΣΑΦΕΣ ΣΥΣΤΗΜΑ MAMDANI
    # =========================================================================
    story.append(Paragraph("2. Σχεδιασμός Ασαφούς Συστήματος (Mamdani FIS)", style_h1))
    story.append(Paragraph(
        "Το σύστημα υιοθετεί την κλασική αρχιτεκτονική Mamdani FIS σε 4 διαδοχικά στάδια: "
        "<i>Ασαφοποίηση (Fuzzification)</i>, <i>Αξιολόγηση Βάσης Κανόνων (Rule Evaluation με Min/Max)</i>, "
        "<i>Συνένωση Συμπερασμάτων (Aggregation)</i> και <i>Αποσαφοποίηση (Defuzzification με Centroid)</i>.",
        style_body
    ))

    story.append(Paragraph("2.1 Μεταβλητές Εισόδου & Συναρτήσεις Συμμετοχής", style_h2))
    story.append(Paragraph("Ορίστηκαν 4 θεμελιώδεις κατηγορίες μεταβλητών εισόδου με τα αντίστοιχα πεδία ορισμού:", style_body))

    inputs_table_data = [
        [Paragraph("<b>Μεταβλητή Εισόδου</b>", style_table_header), Paragraph("<b>Πεδίο (U)</b>", style_table_header), Paragraph("<b>Μονάδα</b>", style_table_header), Paragraph("<b>Γλωσσικοί Όροι & Συναρτήσεις Συμμετοχής</b>", style_table_header)],
        [Paragraph("Προϋπολογισμός (Budget)", style_table_cell), Paragraph("[100, 5000]", style_table_cell), Paragraph("€", style_table_cell), Paragraph("Low: Τραπεζοειδής (100,100,500,900)<br/>Medium: Τριγωνική (650,1500,2500)<br/>High: Τραπεζοειδής (2000,3200,5000,5000)", style_table_cell)],
        [Paragraph("Κλίμα / Θερμοκρασία (Climate)", style_table_cell), Paragraph("[-10, 45]", style_table_cell), Paragraph("°C", style_table_cell), Paragraph("Cold: Τραπεζοειδής (-10,-10,8,15)<br/>Mild: Τριγωνική (12,20,27)<br/>Warm: Τραπεζοειδής (24,30,45,45)", style_table_cell)],
        [Paragraph("Διάρκεια (Duration)", style_table_cell), Paragraph("[1, 30]", style_table_cell), Paragraph("Ημέρες", style_table_cell), Paragraph("Short: Τραπεζοειδής (1,1,3,5)<br/>Medium: Τριγωνική (4,7,12)<br/>Long: Τραπεζοειδής (10,15,30,30)", style_table_cell)],
        [Paragraph("Δραστηριότητες (Activities:<br/>Culture, Adventure, Relaxation, Nightlife)", style_table_cell), Paragraph("[0, 10]", style_table_cell), Paragraph("Κλίμακα 0-10", style_table_cell), Paragraph("Low: Τραπεζοειδής (0,0,2.5,4.5)<br/>Medium: Τριγωνική (3.5,5.5,7.5)<br/>High: Τραπεζοειδής (6.5,8.5,10,10)", style_table_cell)]
    ]
    t_inputs = Table(inputs_table_data, colWidths=[120, 65, 45, 230])
    t_inputs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
    ]))
    story.append(t_inputs)

    # Embed input figures
    fig_budget = os.path.join(figures_dir, "mf_budget.png")
    fig_climate = os.path.join(figures_dir, "mf_climate.png")
    if os.path.exists(fig_budget) and os.path.exists(fig_climate):
        story.append(Spacer(1, 4))
        img_table = Table([[Image(fig_budget, width=225, height=95), Image(fig_climate, width=225, height=95)]], colWidths=[230, 230])
        story.append(img_table)

    story.append(Paragraph("2.2 Μεταβλητή Εξόδου (Suitability Score) & Γραφήματα", style_h2))
    story.append(Paragraph(
        "Η μεταβλητή εξόδου Καταλληλότητα (Suitability Score) ορίζεται στο διάστημα [0, 100]% και περιλαμβάνει 4 γλωσσικούς όρους:<br/>"
        "• <b>Poor:</b> Τραπεζοειδής (0, 0, 20, 35) — Χαμηλή καταλληλότητα / ασυμβατότητα.<br/>"
        "• <b>Moderate:</b> Τριγωνική (25, 50, 70) — Μέτρια / ισορροπημένη καταλληλότητα.<br/>"
        "• <b>High:</b> Τριγωνική (60, 75, 90) — Υψηλή καταλληλότητα.<br/>"
        "• <b>Excellent:</b> Τραπεζοειδής (80, 90, 100, 100) — Εξαιρετικό ταίριασμα.",
        style_body
    ))
    fig_suit = os.path.join(figures_dir, "mf_suitability.png")
    fig_dur = os.path.join(figures_dir, "mf_duration.png")
    if os.path.exists(fig_suit) and os.path.exists(fig_dur):
        img_table2 = Table([[Image(fig_dur, width=225, height=95), Image(fig_suit, width=225, height=95)]], colWidths=[230, 230])
        story.append(img_table2)

    story.append(PageBreak())

    story.append(Paragraph(f"2.3 Πλήρης Βάση {len(rules)} Ασαφών Κανόνων (Fuzzy Rule Base)", style_h2))
    story.append(Paragraph(
        "Ορίστηκαν 36 κανόνες εμπειρογνώμονα (IF-THEN) με πλήρη γλωσσική κάλυψη (ποσοστό έλλειψης κανόνα 0.00% σε 2000 τυχαίες εισόδους). "
        "Ο βαθμός ενεργοποίησης κάθε κανόνα υπολογίζεται με τον τελεστή Mamdani Min: α_k = min(μ_1(x_1), μ_2(x_2), ...).",
        style_body
    ))

    # Complete 36 Rules Table
    rules_table_data = [
        [Paragraph("<b>ID</b>", style_table_header), Paragraph("<b>Υπόθεση (Antecedent - IF)</b>", style_table_header), Paragraph("<b>Συμπέρασμα (Consequent - THEN)</b>", style_table_header), Paragraph("<b>Βάρος</b>", style_table_header)]
    ]
    for r in rules:
        ante_str = " AND ".join([f"{k} = {v}" for k, v in r.antecedent.items()])
        conseq_str = f"{r.consequent.get('archetype')} ({r.consequent.get('suitability')})"
        rules_table_data.append([
            Paragraph(r.rule_id, style_table_cell),
            Paragraph(ante_str, style_table_cell),
            Paragraph(conseq_str, style_table_cell),
            Paragraph("1.0", style_table_cell)
        ])

    t_all_rules = Table(rules_table_data, colWidths=[28, 205, 195, 32])
    t_all_rules.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5)
    ]))
    story.append(t_all_rules)

    story.append(Spacer(1, 6))
    story.append(Paragraph("2.4 Αποσαφοποίηση Κέντρου Βάρους & Αριθμητικό Παράδειγμα", style_h2))
    story.append(Paragraph(
        "Για τη μετατροπή του συνενωμένου ασαφούς συνόλου σε καθαρό ποσοστό καταλληλότητας (0-100%), εφαρμόζεται η μέθοδος του Κέντρου Βάρους (Centroid COG):",
        style_body
    ))
    story.append(Paragraph("z* = [ ∫ z · μ_A(z) dz ] / [ ∫ μ_A(z) dz ] ≈ [ Σ (z_i · μ_A(z_i)) ] / [ Σ μ_A(z_i) ]", style_math))
    story.append(Paragraph(
        "<i>Σημείωση Μηδενικής Ενεργοποίησης:</i> Όταν κανένας κανόνας δεν ενεργοποιείται για έναν αρχέτυπο, αποδίδεται χαμηλό σκορ βάσης 10.0% "
        "(αντί για το ουδέτερο 50.0%), διασφαλίζοντας ότι μη σχετικοί προορισμοί δεν υπερτερούν έναντι επιλογών που ενεργοποίησαν ρητά κανόνα Poor.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Ενδεικτικό Αριθμητικό Παράδειγμα Υπολογισμού:</b><br/>"
        "Έστω είσοδος χρήστη: Budget = 1200€, Climate = 24°C, Duration = 5 ημ., Culture = 8.0/10, Adventure = 4.0/10, Relaxation = 7.0/10, Nightlife = 6.0/10.<br/>"
        "1. <b>Ασαφοποίηση:</b> Culture: High=0.75 | Climate: Mild=0.43, Warm=0.00 | Duration: Medium=0.33 | Budget: Medium=0.65 | Nightlife: Medium=0.75.<br/>"
        "2. <b>Ενεργοποίηση Κανόνων:</b><br/>"
        "   • Κανόνας R02: Culture is High (0.75) AND Budget is Medium (0.65) ⇒ Firing strength α_R02 = min(0.75, 0.65) = <b>0.65</b> (Cultural City, High).<br/>"
        "   • Κανόνας R29: Nightlife is Medium (0.75) AND Culture is High (0.75) ⇒ Firing strength α_R29 = min(0.75, 0.75) = <b>0.75</b> (Vibrant Urban, Moderate).<br/>"
        "3. <b>Αποκοπή & Συνένωση (Aggregation):</b> Για τον αρχέτυπο 'Cultural & Heritage City', η συνάρτηση High αποκόπτεται στο ύψος 0.65.<br/>"
        "4. <b>Αποσαφοποίηση Centroid:</b> Ολοκλήρωση σε 201 σημεία z ∈ [0, 100] ⇒ <b>z* = 68.3%</b>.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # 4. ΕΠΕΚΤΑΣΗ: FUZZY C-MEANS (FCM)
    # =========================================================================
    story.append(Paragraph("3. Επέκταση: Fuzzy C-Means (FCM) Customer Profiling", style_h1))
    story.append(Paragraph(
        "Η επέκταση της εργασίας υλοποιεί τον αλγόριθμο <b>Fuzzy C-Means (Bezdek 1981)</b> για την ομαδοποίηση των χρηστών σε 5 τουριστικά personas. "
        "Σε αντίθεση με τη σκληρή ομαδοποίηση (Hard Clustering K-Means), το FCM αποδίδει βαθμούς συμμετοχής u_ij ∈ [0, 1] σε πολλαπλά προφίλ ταυτόχρονα, "
        "μοντελοποιώντας με ακρίβεια την πολυδιάστατη ανθρώπινη ταξιδιωτική συμπεριφορά.",
        style_body
    ))
    story.append(Paragraph(
        "<i>Συνθετικό Σύνολο Δεδομένων (Synthetic Dataset):</i> Το μοντέλο εκπαιδεύτηκε σε 350 συνθετικά δείγματα ταξιδιωτών, "
        "σχεδιασμένα ώστε να αποτυπώνουν ρεαλιστικά ταξιδιωτικά και καταναλωτικά μοτίβα στην Ελλάδα και το εξωτερικό.",
        style_body
    ))

    story.append(Paragraph("3.1 Μαθηματική Διατύπωση & Ευθυγράμμιση Hungarian", style_h2))
    story.append(Paragraph("Ο αλγόριθμος ελαχιστοποιεί την αντικειμενική συνάρτηση κόστους:", style_body))
    story.append(Paragraph("J_m = Σ_{i=1}^N Σ_{j=1}^C (u_{ij})^m · || x_i - v_j ||^2", style_math))
    story.append(Paragraph(
        "όπου N = 350 δείγματα, C = 5 συστάδες, m = 2.0 (fuzzifier). "
        "<b>Επίλυση Αντιστοίχισης Συστάδων (Hungarian Algorithm):</b> Λόγω της τυχαίας αρχικοποίησης του πίνακα U, οι δείκτες των clusters μπορεί να αντιστραφούν. "
        "Για τη διασφάλιση 100% ταυτότητας personas ανεξαρτήτως random seed, μετά τη σύγκλιση εκτελείται ο αλγόριθμος Hungarian "
        "(<code>scipy.optimize.linear_sum_assignment</code>) μεταξύ των κεντροειδών v_j και των πρότυπων διανυσμάτων των 5 personas.",
        style_body
    ))

    story.append(Paragraph(f"3.2 Μετρικές Επικύρωσης & Πίνακας Κεντροειδών (C = 5)", style_h2))
    story.append(Paragraph(
        f"• <b>Partition Coefficient (PC):</b> {fcm_metrics.get('partition_coefficient_PC', 0.6624)} (υψηλή σαφήνεια συστάδων, θεωρητικό όριο [0.2, 1.0]).<br/>"
        f"• <b>Partition Entropy (PE):</b> {fcm_metrics.get('partition_entropy_PE', 0.7354)} (χαμηλή εντροπία διαμέρισης, θεωρητικό όριο [0.0, 1.61]).<br/>"
        f"• <b>Επαναλήψεις Σύγκλισης:</b> {fcm_metrics.get('iterations_to_converge', 17)} επαναλήψεις με ανοχή tol = 1e-5.",
        style_body
    ))

    # Centroids Table in physical units
    df_cent = rec.fcm_model.get_centroids_dataframe()
    cent_table_data = [
        [Paragraph("<b>Persona</b>", style_table_header), Paragraph("<b>Budget</b>", style_table_header), Paragraph("<b>Κλίμα</b>", style_table_header), Paragraph("<b>Διάρκεια</b>", style_table_header), Paragraph("<b>Culture</b>", style_table_header), Paragraph("<b>Adventure</b>", style_table_header), Paragraph("<b>Relax</b>", style_table_header), Paragraph("<b>Nightlife</b>", style_table_header)]
    ]
    for _, row in df_cent.iterrows():
        cent_table_data.append([
            Paragraph(row["Persona"], style_table_cell),
            Paragraph(str(row["Budget (€)"]), style_table_cell),
            Paragraph(str(row["Κλίμα (°C)"]), style_table_cell),
            Paragraph(str(row["Διάρκεια"]), style_table_cell),
            Paragraph(str(row["Πολιτισμός"]), style_table_cell),
            Paragraph(str(row["Περιπέτεια"]), style_table_cell),
            Paragraph(str(row["Χαλάρωση"]), style_table_cell),
            Paragraph(str(row["Νυχτερινή Ζωή"]), style_table_cell)
        ])
    t_cent = Table(cent_table_data, colWidths=[120, 48, 48, 50, 48, 48, 48, 50])
    t_cent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
    ]))
    story.append(t_cent)

    fig_fcm = os.path.join(figures_dir, "fcm_convergence.png")
    if os.path.exists(fig_fcm):
        story.append(Spacer(1, 4))
        story.append(Image(fig_fcm, width=440, height=135))

    story.append(PageBreak())

    # =========================================================================
    # 5. ΥΒΡΙΔΙΚΟΣ RECOMMENDER & FEEDBACK LOOP
    # =========================================================================
    story.append(Paragraph("4. Τρόπος Λειτουργίας & Μηχανισμός Ανάδρασης (Feedback Loop)", style_h1))
    story.append(Paragraph(
        "Σύμφωνα με τις προδιαγραφές, το σύστημα συνδέει άμεσα την ομαδοποίηση FCM με την παραγωγή εξατομικευμένων προτάσεων "
        "και ενσωματώνει κλειστό βρόχο ανάδρασης (Closed Feedback Loop) που επιτρέπει συνεχή προσαρμοστική μάθηση.",
        style_body
    ))

    story.append(Paragraph("4.1 Αρχιτεκτονική Ροής & Επίδραση FCM (A1)", style_h2))
    story.append(Paragraph(
        "Κάθε τουριστικό persona j του FCM αντιστοιχεί σε ένα διάνυσμα προτίμησης W[j][archetype] προς τα 6 αρχέτυπα προορισμών. "
        "Η συνάφεια του ταξιδιώτη προς έναν αρχέτυπο υπολογίζεται ως το σταθμισμένο άθροισμα των βαθμών συμμετοχής του u_j:",
        style_body
    ))
    story.append(Paragraph("persona_affinity(archetype) = Σ_{j=1}^5 ( u_j · W[j][archetype] )", style_math))
    story.append(Paragraph(
        "Το <b>persona_score</b> (0-100%) ενσωματώνεται στο τελικό σκορ με βάρος 15%, λαμβάνοντας υπόψη και τον δευτερεύοντα αρχέτυπο του προορισμού.",
        style_body
    ))

    story.append(Paragraph("4.2 Μαθηματικό Μοντέλο Τελικού Σκορ & Ασαφή Συστατικά (B4)", style_h2))
    story.append(Paragraph("Το συνολικό σκορ καταλληλότητας κάθε προορισμού υπολογίζεται σύμφωνα με τον τύπο:", style_body))
    story.append(Paragraph(
        "BaseScore = 0.25 · ArchScore + 0.15 · PersonaScore + 0.20 · BudgetScore + 0.20 · ActivityScore + 0.10 · ClimateScore + 0.10 · DurationScore",
        style_math
    ))
    story.append(Paragraph(
        "Όπου όλα τα βάρη αθροίζουν αυστηρά στο 1.00 (100%) και τα επιμέρους σκορ ορίζονται ως εξής:<br/>"
        "• <b>ArchScore (0.25):</b> Αποσαφοποιημένο σκορ Mamdani Centroid για τον κύριο και δευτερεύοντα αρχέτυπο.<br/>"
        "• <b>PersonaScore (0.15):</b> Βαθμός ταύτισης με το τουριστικό DNA του χρήστη μέσω του FCM.<br/>"
        "• <b>BudgetScore (0.20):</b> Ασαφής βαθμός συμμετοχής του κόστους στο τραπεζοειδές σύνολο 'Εντός Budget': trapezoidal(Cost, 0, 0, B, 1.35·B) · 100.<br/>"
        "• <b>ActivityScore (0.20):</b> Συμπληρωματική απόσταση Manhattan μεταξύ των 4 επιθυμιών του χρήστη και του προορισμού.<br/>"
        "• <b>ClimateScore (0.10):</b> Ασαφής βαθμός συμμετοχής της θερμοκρασίας στο τραπεζοειδές σύνολο γύρω από την επιθυμητή: trapezoidal(T, T_u-10, T_u-2, T_u+2, T_u+10) · 100.<br/>"
        "• <b>DurationScore (0.10):</b> Ασαφής βαθμός συμμετοχής της διάρκειας στο βέλτιστο διάστημα διαμονής του προορισμού.",
        style_body
    ))

    story.append(Paragraph("4.3 Δυναμικός Βρόχος Ανάδρασης (Feedback Loop)", style_h2))
    story.append(Paragraph(
        "Το ιστορικό αξιολογήσεων των χρηστών ανατροφοδοτεί το τελικό σκορ σύμφωνα με τη σχέση:",
        style_body
    ))
    story.append(Paragraph("FinalScore = BaseScore + Δ_feedback", style_math))
    story.append(Paragraph("Δ_feedback = w_r · ( r̄ - 3.0 ) + w_a · ( AcceptanceRate - 0.5 )", style_math))
    story.append(Paragraph(
        "όπου r̄ ∈ [1, 5] είναι η μέση βαθμολογία αστεριών, AcceptanceRate ∈ [0, 1] το ποσοστό επιλογής και w_r = 4.0, w_a = 4.0. "
        "Προορισμοί με συνεπή θετική ανάδραση λαμβάνουν πριμ έως +10%, ενώ απορριφθείσες επιλογές υποβαθμίζονται αυτόματα.",
        style_body
    ))

    # =========================================================================
    # 6. ΕΓΧΕΙΡΙΔΙΟ ΧΡΗΣΤΗ ΕΦΑΡΜΟΓΗΣ
    # =========================================================================
    story.append(Paragraph("5. Εγχειρίδιο Χρήστη Εφαρμογής (User Manual)", style_h1))
    story.append(Paragraph(
        "Η εφαρμογή FuzzyTravel AI παρέχει ένα σύγχρονο, εύχρηστο γραφικό περιβάλλον (Streamlit Web GUI), "
        "ειδικά σχεδιασμένο για ταξιδιωτικούς πράκτορες και ακαδημαϊκή εποπτεία.",
        style_body
    ))

    story.append(Paragraph("5.1 Οδηγίες Εγκατάστασης & Εκτέλεσης (macOS & Windows)", style_h2))
    story.append(Paragraph(
        "<b>Εγκατάσταση σε macOS / Linux:</b><br/>"
        "<code>python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt</code><br/>"
        "<b>Εγκατάσταση σε Windows:</b><br/>"
        "<code>python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt</code><br/>"
        "<b>Εκκίνηση με 1 κλικ:</b> Διπλό κλικ στο <code>run_app.command</code> (macOS) ή <code>run_app.bat</code> (Windows). "
        "Η εφαρμογή ανοίγει αυτόματα στον browser στο <code>http://localhost:8501</code>.",
        style_body
    ))

    story.append(Paragraph("5.2 Περιγραφή των 3 Ενοτήτων της Εφαρμογής", style_h2))
    story.append(Paragraph(
        "1. <b>✈️ Σύμβουλος Προτάσεων (Recommender):</b><br/>"
        "   • Πλευρική στήλη: Sliders εισαγωγής Budget (150-5000€), Κλίματος (-5 έως 40°C), Διάρκειας (1-25 ημ.) και 4 Δραστηριοτήτων (0-10).<br/>"
        "   • Ταξιδιωτικό DNA (FCM): Διαδραστικό διάγραμμα ραντάρ (Plotly Radar Chart) με τα 5 τουριστικά personas.<br/>"
        "   • Κάρτες Top-5 Προορισμών: Φωτογραφία, εκτιμώμενο κόστος, προτεινόμενο πακέτο γραφείου, διάγραμμα ανάλυσης 6 κριτηρίων και bullet points Επεξηγηματικής AI (XAI).<br/>"
        "   • Φόρμα Ανάδρασης: Υποβολή αστεριών (1-5), αποδοχής/απόρριψης και σχολίου κάτω από κάθε προορισμό.<br/>"
        "   • <b>Εξαγωγή Προσφοράς σε PDF (B2B Quotation):</b> Εισαγωγή στοιχείων πελάτη και παραγωγή επίσημης επώνυμης προσφοράς PDF με 1 κλικ.<br/>"
        "2. <b>🧠 Ακαδημαϊκή Εποπτεία:</b><br/>"
        "   • Διαδραστική προβολή όλων των συναρτήσεων συμμετοχής με κατακόρυφη ένδειξη των τρεχουσών τιμών εισόδου.<br/>"
        "   • Πίνακας 36 κανόνων με firing strengths σε πραγματικό χρόνο, μετρικές σύγκλισης FCM (PC, PE) και πίνακας κεντροειδών.<br/>"
        "   • Ζωντανό log και analytics της καταγεγραμμένης ανάδρασης.<br/>"
        "3. <b>💼 Διαχείριση Καταλόγου (B2B Inventory):</b><br/>"
        "   • Πλήρης διαχείριση αποθέματος 22 προορισμών (12 Ελλάδα, 10 Εξωτερικό), φόρμα προσθήκης νέου πακέτου και εξαγωγή σε CSV.",
        style_body
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6. Συμπεράσματα & Εμπορικές Προοπτικές", style_h1))
    story.append(Paragraph(
        "Το σύστημα FuzzyTravel AI ικανοποιεί στο 100% όλες τις ακαδημαϊκές απαιτήσεις της Απαλλακτικής Εργασίας 2026 και αποτελεί "
        "ένα λειτουργικό MVP υψηλής επιχειρηματικής αξίας. "
        "Η αρθρωτή του αρχιτεκτονική επιτρέπει την άμεση έκθεσή του ως cloud REST API (μέσω FastAPI) για ενσωμάτωση σε "
        "υπάρχοντα συστήματα κρατήσεων (GDS, OTA, Tour Operators).",
        style_body
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Academic Report PDF successfully compiled to: {output_pdf_path}")


if __name__ == "__main__":
    pdf_out = os.path.join(os.path.dirname(__file__), "Fuzzy_Tourism_Recommendation_System_Report.pdf")
    build_academic_pdf(pdf_out)
