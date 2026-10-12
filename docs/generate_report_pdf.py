"""
Academic Master's Report & User Manual Generator in PDF format.
Meets all deliverables specified in UNIPI Master's Course 2026.
Uses ReportLab with native Greek Unicode TrueType Font support.
"""
import os
import sys

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        self.drawString(54, 800, "ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ | ΑΣΑΦΕΣ ΕΜΠΕΙΡΟ ΣΥΣΤΗΜΑ ΤΟΥΡΙΣΤΙΚΩΝ ΠΡΟΤΑΣΕΩΝ")
        self.setStrokeColor(colors.HexColor("#bdc3c7"))
        self.setLineWidth(0.5)
        self.line(54, 792, 540, 792)

        # Footer
        self.line(54, 50, 540, 50)
        self.drawString(54, 38, "Απαλλακτική Εργασία 2026 — FuzzyTravel AI")
        page_text = f"Σελίδα {self._pageNumber} από {page_count}"
        self.drawRightString(540, 38, page_text)
        self.restoreState()


def build_academic_pdf(output_pdf_path: str):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
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
        fontSize=20,
        leading=26,
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
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#0c2461"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'H2',
        fontName=FONT_BOLD,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e3799"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body',
        fontName=FONT_NORMAL,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=6
    )
    style_bullet = ParagraphStyle(
        'Bullet',
        fontName=FONT_NORMAL,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2c3e50"),
        leftIndent=15,
        spaceAfter=3
    )
    style_table_header = ParagraphStyle(
        'TableHeader',
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    style_table_cell = ParagraphStyle(
        'TableCell',
        fontName=FONT_NORMAL,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2c3e50")
    )

    story = []

    # =========================================================================
    # 1. ΕΞΩΦΥΛΛΟ
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ", style_cover_uni))
    story.append(Paragraph("ΤΜΗΜΑ ΠΛΗΡΟΦΟΡΙΚΗΣ", style_cover_uni))
    story.append(Paragraph("ΠΡΟΓΡΑΜΜΑ ΜΕΤΑΠΤΥΧΙΑΚΩΝ ΣΠΟΥΔΩΝ", style_cover_sub))
    story.append(Spacer(1, 40))

    story.append(Paragraph("ΑΠΑΛΛΑΚΤΙΚΗ ΕΡΓΑΣΙΑ 2026", style_cover_sub))
    story.append(Spacer(1, 15))
    story.append(Paragraph("ΕΜΠΕΙΡΟ ΣΥΣΤΗΜΑ ΤΟΥΡΙΣΤΙΚΩΝ ΠΡΟΤΑΣΕΩΝ ΜΕ ΧΡΗΣΗ ΑΣΑΦΟΥΣ ΛΟΓΙΚΗΣ (MAMDANI FIS) ΚΑΙ ΟΜΑΔΟΠΟΙΗΣΗ ΠΡΟΦΙΛ ΜΕ FUZZY C-MEANS (FCM)", style_cover_title))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Θέμα 3: Σύστημα Τουριστικών Προτάσεων & Επέκταση FCM</i>", style_cover_sub))
    story.append(Spacer(1, 70))

    info_data = [
        [Paragraph("<b>Μάθημα:</b>", style_body), Paragraph("Ασαφή Συστήματα & Υπολογιστική Νοημοσύνη", style_body)],
        [Paragraph("<b>Διδάσκουσα:</b>", style_body), Paragraph("Δρ. Κ. Χρυσαφιάδη (kchrysafiadi@unipi.gr)", style_body)],
        [Paragraph("<b>Ακαδημαϊκό Έτος:</b>", style_body), Paragraph("2025 - 2026", style_body)],
        [Paragraph("<b>Παραδοτέα:</b>", style_body), Paragraph("1. Πηγαίος Κώδικας & Εφαρμογή<br/>2. Τεχνική Έκθεση & Εγχειρίδιο Χρήστη (PDF)", style_body)]
    ]
    t_info = Table(info_data, colWidths=[120, 320])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0"))
    ]))
    story.append(t_info)

    story.append(PageBreak())

    # =========================================================================
    # 2. ΕΙΣΑΓΩΓΗ & ΕΠΙΧΕΙΡΗΣΙΑΚΗ ΑΡΧΙΤΕΚΤΟΝΙΚΗ
    # =========================================================================
    story.append(Paragraph("1. Εισαγωγή & Επιχειρησιακό Πλαίσιο (B2B Travel Tech)", style_h1))
    story.append(Paragraph(
        "Η παρούσα εργασία υλοποιεί ένα προηγμένο <b>Έμπειρο Σύστημα Τουριστικών Προτάσεων (FuzzyTravel AI)</b>, "
        "βασισμένο στις αρχές της Ασαφούς Λογικής (Fuzzy Logic) και της Ασαφούς Ομαδοποίησης (Fuzzy C-Means Clustering). "
        "Στον τομέα του τουρισμού, οι ανθρώπινες προτιμήσεις και οι ταξιδιωτικές επιθυμίες χαρακτηρίζονται εγγενώς από υψηλή αβεβαιότητα, υποκειμενικότητα και ασάφεια. "
        "Ένας ταξιδιώτης σπάνια εκφράζει τις επιθυμίες του με απόλυτα ψηφιακά όρια (π.χ. 'θέλω αυστηρά 23.4°C και 1.150€'). "
        "Αντιθέτως, χρησιμοποιεί γλωσσικούς όρους όπως <i>«οικονομικός προϋπολογισμός»</i>, <i>«ήπιο κλίμα»</i>, <i>«έντονο ενδιαφέρον για πολιτισμό»</i>.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Εμπορική Διάσταση & Μεταπώληση σε Γραφεία:</b> "
        "Το σύστημα σχεδιάστηκε εξαρχής με <i>αρθρωτή αρχιτεκτονική (modular decoupled design)</i>. "
        "Ο μαθηματικός πυρήνας αξιολόγησης είναι πλήρως διαχωρισμένος από το περιβάλλον διεπαφής (Streamlit UI). "
        "Αυτό επιτρέπει στα ταξιδιωτικά γραφεία να εισάγουν το δικό τους απόθεμα πακέτων (inventory), να εξάγουν εξατομικευμένες προτάσεις σε πραγματικό χρόνο και να παρέχουν <b>πλήρη επεξηγησιμότητα (Explainable AI - XAI)</b> στον πελάτη για το 'γιατί' προτάθηκε κάθε προορισμός.",
        style_body
    ))

    story.append(Spacer(1, 8))

    # =========================================================================
    # 3. ΑΣΑΦΕΣ ΣΥΣΤΗΜΑ MAMDANI
    # =========================================================================
    story.append(Paragraph("2. Σχεδιασμός Ασαφούς Συστήματος (Mamdani FIS)", style_h1))
    story.append(Paragraph(
        "Το σύστημα υιοθετεί την κλασική αρχιτεκτονική <b>Mamdani Fuzzy Inference System</b>, η οποία περιλαμβάνει τέσσερα στάδια: "
        "<i>Ασαφοποίηση (Fuzzification)</i>, <i>Αξιολόγηση Κανόνων (Rule Evaluation με Min/Max)</i>, <i>Συνένωση (Aggregation)</i> και <i>Αποσαφοποίηση (Defuzzification με Centroid)</i>.",
        style_body
    ))

    story.append(Paragraph("2.1 Μεταβλητές Εισόδου & Πεδία Ορισμού (Universes of Discourse)", style_h2))
    story.append(Paragraph("Σύμφωνα με τις προδιαγραφές του Θέματος 3, ορίστηκαν 4 θεμελιώδεις κατηγορίες μεταβλητών εισόδου:", style_body))

    inputs_table_data = [
        [Paragraph("<b>Μεταβλητή</b>", style_table_header), Paragraph("<b>Πεδίο Ορισμού (U)</b>", style_table_header), Paragraph("<b>Μονάδα</b>", style_table_header), Paragraph("<b>Γλωσσικοί Όροι & Μορφή Συναρτήσεων</b>", style_table_header)],
        [Paragraph("Προϋπολογισμός (Budget)", style_table_cell), Paragraph("[100, 5000]", style_table_cell), Paragraph("€", style_table_cell), Paragraph("Low: Τραπεζοειδής (100,100,500,900)<br/>Medium: Τριγωνική (650,1500,2500)<br/>High: Τραπεζοειδής (2000,3200,5000,5000)", style_table_cell)],
        [Paragraph("Κλίμα (Climate)", style_table_cell), Paragraph("[-10, 45]", style_table_cell), Paragraph("°C", style_table_cell), Paragraph("Cold: Τραπεζοειδής (-10,-10,8,15)<br/>Mild: Τριγωνική (12,20,27)<br/>Warm: Τραπεζοειδής (24,30,45,45)", style_table_cell)],
        [Paragraph("Διάρκεια (Duration)", style_table_cell), Paragraph("[1, 30]", style_table_cell), Paragraph("Ημέρες", style_table_cell), Paragraph("Short: Τραπεζοειδής (1,1,3,5)<br/>Medium: Τριγωνική (4,7,12)<br/>Long: Τραπεζοειδής (10,15,30,30)", style_table_cell)],
        [Paragraph("Δραστηριότητες (Activities:<br/>Culture, Adventure, Relaxation, Nightlife)", style_table_cell), Paragraph("[0, 10]", style_table_cell), Paragraph("Κλίμακα 0-10", style_table_cell), Paragraph("Low: Τραπεζοειδής (0,0,2.5,4.5)<br/>Medium: Τριγωνική (3.5,5.5,7.5)<br/>High: Τραπεζοειδής (6.5,8.5,10,10)", style_table_cell)]
    ]
    t_inputs = Table(inputs_table_data, colWidths=[110, 75, 45, 230])
    t_inputs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(t_inputs)

    story.append(Spacer(1, 8))

    # Check and embed figure if exists
    fig_budget = os.path.join(os.path.dirname(__file__), "figures", "mf_budget.png")
    fig_climate = os.path.join(os.path.dirname(__file__), "figures", "mf_climate.png")
    if os.path.exists(fig_budget) and os.path.exists(fig_climate):
        img_table = Table([[Image(fig_budget, width=225, height=110), Image(fig_climate, width=225, height=110)]], colWidths=[230, 230])
        story.append(img_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph("2.2 Βάση Ασαφών Κανόνων (Rule Base) & Firing Strength", style_h2))
    story.append(Paragraph(
        "Ορίστηκαν 18 ασαφείς κανόνες εμπειρογνώμονα (IF-THEN) που μοντελοποιούν τις σχέσεις μεταξύ των επιθυμιών του ταξιδιώτη και των αρχετύπων προορισμών. "
        "Για τον τελεστή AND χρησιμοποιείται η πράξη της ελαχιστοποίησης (Mamdani Min operator): "
        "α = min(μ_1(x_1), μ_2(x_2), ...).",
        style_body
    ))

    rules_table_data = [
        [Paragraph("<b>ID</b>", style_table_header), Paragraph("<b>IF (Υπόθεση / Antecedent)</b>", style_table_header), Paragraph("<b>THEN (Συμπέρασμα)</b>", style_table_header)],
        [Paragraph("R01", style_table_cell), Paragraph("Culture is High AND Duration is Short AND Climate is Mild", style_table_cell), Paragraph("Archetype = Cultural & Heritage City (Excellent)", style_table_cell)],
        [Paragraph("R04", style_table_cell), Paragraph("Relaxation is High AND Climate is Warm AND Duration is Medium", style_table_cell), Paragraph("Archetype = Coastal & Island Relaxation (Excellent)", style_table_cell)],
        [Paragraph("R06", style_table_cell), Paragraph("Relaxation is High AND Budget is High AND Climate is Warm", style_table_cell), Paragraph("Archetype = Luxury & Premium Wellness (Excellent)", style_table_cell)],
        [Paragraph("R07", style_table_cell), Paragraph("Adventure is High AND Climate is Cold", style_table_cell), Paragraph("Archetype = Alpine & Mountain Adventure (Excellent)", style_table_cell)],
        [Paragraph("R10", style_table_cell), Paragraph("Nightlife is High AND Duration is Short AND Budget is Low", style_table_cell), Paragraph("Archetype = Vibrant Urban & Entertainment (High)", style_table_cell)],
        [Paragraph("R12", style_table_cell), Paragraph("Adventure is High AND Duration is Long AND Climate is Warm", style_table_cell), Paragraph("Archetype = Exotic & Tropical Explorer (Excellent)", style_table_cell)],
        [Paragraph("R14", style_table_cell), Paragraph("Budget is Low AND Duration is Long", style_table_cell), Paragraph("Archetype = Luxury & Premium Wellness (Poor)", style_table_cell)],
    ]
    t_rules = Table(rules_table_data, colWidths=[35, 230, 195])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
    ]))
    story.append(t_rules)

    story.append(Spacer(1, 8))
    story.append(Paragraph("2.3 Μέθοδος Αποσαφοποίησης (Centroid / Center of Gravity)", style_h2))
    story.append(Paragraph(
        "Για τη μετατροπή του συνενωμένου ασαφούς συνόλου εξόδου σε έναν καθαρό αριθμό καταλληλότητας (0 - 100%), "
        "εφαρμόζεται η μέθοδος του <b>Κέντρου Βάρους (Centroid Defuzzification)</b>:",
        style_body
    ))
    story.append(Paragraph(
        "<font face='Helvetica-Oblique'>z* = [ ∫ z · μ_A(z) dz ] / [ ∫ μ_A(z) dz ] ≈ [ Σ (z_i · μ_A(z_i)) ] / [ Σ μ_A(z_i) ]</font>",
        ParagraphStyle('MathStyle', fontName=FONT_BOLD, fontSize=9.5, alignment=1, textColor=colors.HexColor("#1e3799"), spaceAfter=6)
    ))

    story.append(PageBreak())

    # =========================================================================
    # 4. ΕΠΕΚΤΑΣΗ: FUZZY C-MEANS (FCM)
    # =========================================================================
    story.append(Paragraph("3. Επέκταση: Fuzzy C-Means (FCM) Customer Profiling", style_h1))
    story.append(Paragraph(
        "Η επέκταση της εργασίας απαιτεί τη χρήση <b>Fuzzy C-Means (FCM)</b> για την ομαδοποίηση χρηστών σε τουριστικά προφίλ "
        "και την παραγωγή εξατομικευμένων συστάσεων. "
        "Σε αντίθεση με το κλασικό K-Means όπου ένας χρήστης ανήκει αυστηρά σε μία ομάδα (hard clustering), "
        "το FCM επιτρέπει σε έναν ταξιδιώτη να έχει βαθμό συμμετοχής u_ij σε πολλαπλά προφίλ ταυτόχρονα (soft clustering).",
        style_body
    ))

    story.append(Paragraph("3.1 Μαθηματική Διατύπωση Αλγορίθμου Bezdek (1981)", style_h2))
    story.append(Paragraph(
        "Ο αλγόριθμος ελαχιστοποιεί την αντικειμενική συνάρτηση κόστους:",
        style_body
    ))
    story.append(Paragraph(
        "<font face='Helvetica-Oblique'>J_m = Σ_{i=1}^N Σ_{j=1}^C (u_{ij})^m · ||x_i - v_j||^2</font>",
        ParagraphStyle('MathStyle2', fontName=FONT_BOLD, fontSize=10, alignment=1, textColor=colors.HexColor("#1e3799"), spaceAfter=6)
    ))
    story.append(Paragraph("Οι εξισώσεις ανανέωσης κεντροειδών και συμμετοχών είναι:", style_body))
    story.append(Paragraph(
        "1. Κεντροειδή: <i>v_j = [ Σ_{i=1}^N (u_{ij})^m · x_i ] / [ Σ_{i=1}^N (u_{ij})^m ]</i><br/>"
        "2. Πίνακας Συμμετοχών: <i>u_{ij} = 1 / [ Σ_{k=1}^C ( ||x_i - v_j|| / ||x_i - v_k|| )^(2 / (m - 1)) ]</i>",
        style_bullet
    ))

    story.append(Paragraph("3.2 Τουριστικά Αρχέτυπα (Personas) & Επικύρωση (Validation)", style_h2))
    story.append(Paragraph(
        "Ομαδοποιήσαμε το ιστορικό δεδομένων σε 5 διακριτά τουριστικά προφίλ:<br/>"
        "<b>1. Cultural & Heritage Explorer</b> (Υψηλός πολιτισμός, ήπιο κλίμα, μεσαίο-υψηλό budget)<br/>"
        "<b>2. Luxury & Wellness Relaxer</b> (Υψηλό budget, θερμό κλίμα, πολυήμερες διακοπές spa/resort)<br/>"
        "<b>3. Budget Backpacker & Youth Nomad</b> (Χαμηλό κόστος, αυθεντικότητα, ευελιξία, έντονη περιπέτεια)<br/>"
        "<b>4. Alpine & Nature Adventure Seeker</b> (Υπαίθριες δραστηριότητες, δροσερό κλίμα, trekking/hiking)<br/>"
        "<b>5. Cosmopolitan & Nightlife Vibe</b> (City breaks, νυχτερινή ζωή, γαστρονομία, festivals)",
        style_body
    ))

    fig_fcm = os.path.join(os.path.dirname(__file__), "figures", "fcm_convergence.png")
    if os.path.exists(fig_fcm):
        story.append(Image(fig_fcm, width=440, height=180))

    story.append(Spacer(1, 8))

    # =========================================================================
    # 5. ΤΡΟΠΟΣ ΛΕΙΤΟΥΡΓΙΑΣ & ΜΗΧΑΝΙΣΜΟΣ ΑΝΑΔΡΑΣΗΣ (FEEDBACK LOOP)
    # =========================================================================
    story.append(Paragraph("4. Τρόπος Λειτουργίας & Μηχανισμός Ανάδρασης (Feedback Loop)", style_h1))
    story.append(Paragraph(
        "Σύμφωνα με τις προδιαγραφές της εργασίας, το σύστημα δεν αποτελεί ένα στατικό μηχανισμό αποφάσεων, "
        "αλλά υλοποιεί έναν <b>κλειστό βρόχο ανάδρασης (Closed Feedback Loop)</b> που επιτρέπει τη συνεχή προσαρμογή "
        "και αυτο-βελτίωση των παραγόμενων τουριστικών συστάσεων.",
        style_body
    ))

    story.append(Paragraph("4.1 Αρχιτεκτονική Ροής & Ανάδρασης", style_h2))
    story.append(Paragraph(
        "Η ροή λειτουργίας και ανάδρασης εκτελείται σε τέσσερα διαδοχικά βήματα:<br/>"
        "<b>1. Εισαγωγή & Ασαφοποίηση:</b> Ο χρήστης εισάγει τις προτιμήσεις του (budget, κλίμα, διάρκεια, ενδιαφέροντα).<br/>"
        "<b>2. Υβριδική Εκτίμηση:</b> Συνδυάζονται οι κανόνες Mamdani FIS και οι βαθμοί συμμετοχής στις FCM personas.<br/>"
        "<b>3. Συλλογή Ανάδρασης (Feedback Collection):</b> Κάτω από κάθε προτεινόμενο προορισμό, ο χρήστης ή ο πράκτορας υποβάλλει αξιολόγηση (βαθμολογία 1-5 αστέρια, δήλωση αποδοχής ή απόρριψης και προαιρετικό σχόλιο).<br/>"
        "<b>4. Προσαρμοστική Επαναστάθμιση (Adaptive Adjustment):</b> Η καταγεγραμμένη ανάδραση τροφοδοτεί πίσω τον αλγόριθμο, προσαρμόζοντας το τελικό σκορ των προορισμών σε μελλοντικές αναζητήσεις.",
        style_body
    ))

    story.append(Paragraph("4.2 Μαθηματικό Μοντέλο Προσαρμογής Ανάδρασης", style_h2))
    story.append(Paragraph(
        "Το τελικό σκορ καταλληλότητας κάθε προορισμού αναπροσαρμόζεται με βάση την ιστορική ανάδραση σύμφωνα με τη σχέση:",
        style_body
    ))
    story.append(Paragraph(
        "<font face='Helvetica-Oblique'>FinalScore = BaseScore + Δ_feedback</font>",
        ParagraphStyle('MathStyleFB1', fontName=FONT_BOLD, fontSize=9.5, alignment=1, textColor=colors.HexColor("#1e3799"), spaceAfter=4)
    ))
    story.append(Paragraph(
        "<font face='Helvetica-Oblique'>Δ_feedback = w_r · ( r̄ - 3.0 ) + w_a · ( AcceptanceRate - 0.5 )</font>",
        ParagraphStyle('MathStyleFB2', fontName=FONT_BOLD, fontSize=9.5, alignment=1, textColor=colors.HexColor("#1e3799"), spaceAfter=6)
    ))
    story.append(Paragraph(
        "Όπου <i>r̄ ∈ [1, 5]</i> είναι η μέση ιστορική βαθμολογία αστεριών του προορισμού, <i>AcceptanceRate ∈ [0, 1]</i> είναι το ποσοστό επιλογής, "
        "και <i>w_r = 4.0, w_a = 4.0</i> είναι συντελεστές στάθμισης. "
        "Προορισμοί με υψηλή ικανοποίηση χρηστών λαμβάνουν θετική ενίσχυση (έως +10%), ενώ απορριπτόμενες επιλογές υποβαθμίζονται αυτόματα.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # 6. ΕΓΧΕΙΡΙΔΙΟ ΧΡΗΣΤΗ
    # =========================================================================
    story.append(Paragraph("5. Εγχειρίδιο Χρήστη Εφαρμογής (User Manual)", style_h1))
    story.append(Paragraph(
        "Η εφαρμογή FuzzyTravel AI παρέχει ένα ολοκληρωμένο, σύγχρονο γραφικό περιβάλλον (GUI) μέσω Streamlit. "
        "Είναι διαθέσιμη με πλήρη διαδραστικότητα και περιλαμβάνει τρεις βασικές ενότητες:",
        style_body
    ))

    story.append(Paragraph("5.1 Οδηγίες Εκκίνησης (Installation & Run)", style_h2))
    story.append(Paragraph(
        "Για την εκτέλεση της εφαρμογής σε οποιοδήποτε υπολογιστή:<br/>"
        "1. Άνοιγμα τερματικού στον φάκελο του έργου.<br/>"
        "2. Ενεργοποίηση περιβάλλοντος: <code>source venv/bin/activate</code><br/>"
        "3. Εκτέλεση εφαρμογής: <code>streamlit run ui/app.py</code><br/>"
        "4. Η εφαρμογή ανοίγει αυτόματα στον browser στη διεύθυνση <code>http://localhost:8501</code>.",
        style_body
    ))

    story.append(Paragraph("5.2 Λειτουργία 1: Σύμβουλος Προτάσεων (Travel Agent Recommender)", style_h2))
    story.append(Paragraph(
        "Ο ταξιδιωτικός πράκτορας εισάγει τα κριτήρια του πελάτη (προϋπολογισμός, κλίμα, διάρκεια, δραστηριότητες). "
        "Το σύστημα υπολογίζει άμεσα το <b>FCM Soft Persona Profile</b> και κατατάσσει τους προορισμούς με ποσοστό καταλληλότητας. "
        "Για κάθε προορισμό παρέχονται εικόνα, εκτιμώμενο κόστος, προτεινόμενο πακέτο γραφείου, <b>πλήρης αιτιολόγηση (XAI)</b> και πεδίο υποβολής <b>ανάδρασης χρήστη</b>.<br/>"
        "<b>Νέα Εμπορική Δυνατότητα — Εξαγωγή Επίσημης Προσφοράς σε PDF:</b> "
        "Ο πράκτορας μπορεί να εισάγει το ονοματεπώνυμο του πελάτη, το όνομα του συμβούλου και τυχόν παρατηρήσεις (π.χ. παροχές ξενοδοχείου) "
        "και με ένα κλικ να παράγει ένα επίσημο, branded έντυπο ταξιδιωτικής προσφοράς (PDF Quotation) έτοιμο για άμεση αποστολή στον πελάτη.",
        style_body
    ))

    story.append(Paragraph("5.3 Λειτουργία 2: Ακαδημαϊκή Εποπτεία & Μαθηματικός Έλεγχος", style_h2))
    story.append(Paragraph(
        "Παρουσιάζει διαδραστικά γραφήματα των Συναρτήσεων Συμμετοχής με ένδειξη των τρεχουσών εισόδων, "
        "τον πίνακα των 18 κανόνων με τα ενεργά firing strengths, τις μετρικές σύγκλισης του FCM (Partition Coefficient, Partition Entropy), "
        "καθώς και το ζωντανό ιστορικό και τα analytics της ανάδρασης.",
        style_body
    ))

    story.append(Paragraph("5.4 Λειτουργία 3: Διαχείριση Καταλόγου & Αποθέματος (B2B Inventory Management)", style_h2))
    story.append(Paragraph(
        "Η βάση δεδομένων έχει εμπλουτιστεί με <b>22 ολοκληρωμένους προορισμούς</b> (12 ελληνικούς: Σαντορίνη, Χανιά, Ζαγοροχώρια, Αθήνα, Μύκονος, Πήλιο, Μετέωρα, Κέρκυρα, Νάξος, Μάνη/Μονεμβασιά, Καστοριά, Ναύπλιο και 10 διεθνείς: Ρώμη, Παρίσι, Βιέννη, Ζερμάτ, Ρέικιαβικ, Μπαλί, Βαρκελώνη, Άμστερνταμ, Τόκιο, Νέα Υόρκη). "
        "Επιτρέπει στο γραφείο να προβάλει το απόθεμά του, να προσθέσει δυναμικά νέα πακέτα και να εξάγει τον πλήρη κατάλογο σε μορφή CSV.",
        style_body
    ))

    story.append(Spacer(1, 15))
    story.append(Paragraph("6. Συμπεράσματα & Εμπορικές Προοπτικές", style_h1))
    story.append(Paragraph(
        "Το σύστημα επιτυγχάνει πλήρη κάλυψη των απαιτήσεων της Απαλλακτικής Εργασίας 2026 και αποτελεί ένα λειτουργικό MVP "
        "υψηλής προστιθέμενης αξίας για την τουριστική βιομηχανία. "
        "Η αρθρωτή του δομή επιτρέπει άμεση μετατροπή του μαθηματικού πυρήνα σε cloud REST API (μέσω FastAPI) για ενσωμάτωση "
        "σε υπάρχοντα συστήματα κρατήσεων (GDS, OTA, Tour Operators).",
        style_body
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Academic Report PDF successfully compiled to: {output_pdf_path}")


if __name__ == "__main__":
    pdf_out = os.path.join(os.path.dirname(__file__), "Fuzzy_Tourism_Recommendation_System_Report.pdf")
    build_academic_pdf(pdf_out)
