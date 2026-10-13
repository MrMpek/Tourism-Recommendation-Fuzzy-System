"""
Academic Master's Report & User Manual Generator in Microsoft Word (.docx) format.
Meets all deliverables specified in UNIPI Master's Course 2026.
Creates a professional, fully-formatted document with tables, mathematical formulas,
embedded figures, and comprehensive documentation in Greek.
"""
import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Sets background fill color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Sets internal padding (in dxa: 20 dxa = 1 pt) for a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header_footer(doc):
    """Adds running header and footer across document sections."""
    for section in doc.sections:
        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ | ΑΣΑΦΕΣ ΕΜΠΕΙΡΟ ΣΥΣΤΗΜΑ ΤΟΥΡΙΣΤΙΚΩΝ ΠΡΟΤΑΣΕΩΝ")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(127, 140, 141)
        
        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun1 = fp.add_run("Απαλλακτική Εργασία 2026 — FuzzyTravel AI (Mamdani FIS & FCM)")
        frun1.font.name = "Arial"
        frun1.font.size = Pt(8.5)
        frun1.font.color.rgb = RGBColor(127, 140, 141)

def format_run(run, font_name="Arial", size_pt=10.5, bold=False, italic=False, color_rgb=(44, 62, 80)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def add_styled_paragraph(doc, text="", space_before=0, space_after=6, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = align
    if text:
        run = p.add_run(text)
        format_run(run, "Arial", 10.5, False, False, (44, 62, 80))
    return p

def add_h1(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    format_run(run, "Arial", 15, bold=True, color_rgb=(12, 36, 97))
    return p

def add_h2(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    format_run(run, "Arial", 12, bold=True, color_rgb=(30, 55, 153))
    return p

def add_h3(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    format_run(run, "Arial", 11, bold=True, color_rgb=(74, 105, 189))
    return p

def add_bullet(doc, title, desc):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run1 = p.add_run(title + ": ")
    format_run(run1, "Arial", 10, bold=True, color_rgb=(30, 55, 153))
    run2 = p.add_run(desc)
    format_run(run2, "Arial", 10, bold=False, color_rgb=(44, 62, 80))
    return p

def add_formula_box(doc, formula_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.right_indent = Inches(0.4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(formula_text)
    format_run(run, "Georgia", 11, bold=True, italic=True, color_rgb=(30, 55, 153))
    return p

def build_docx_report(output_path: str):
    doc = Document()
    
    # Set page margins to standard A4 (2.5 cm / 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
    add_header_footer(doc)
    
    # -------------------------------------------------------------
    # ΕΞΩΦΥΛΛΟ (COVER PAGE)
    # -------------------------------------------------------------
    cover_p1 = add_styled_paragraph(doc, space_before=20, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_uni = cover_p1.add_run("ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ\nΤΜΗΜΑ ΠΛΗΡΟΦΟΡΙΚΗΣ")
    format_run(run_uni, "Arial", 14, bold=True, color_rgb=(30, 55, 153))
    
    cover_p2 = add_styled_paragraph(doc, space_before=2, space_after=30, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_pms = cover_p2.add_run("ΠΡΟΓΡΑΜΜΑ ΜΕΤΑΠΤΥΧΙΑΚΩΝ ΣΠΟΥΔΩΝ ΣΤΗΝ ΠΛΗΡΟΦΟΡΙΚΗ")
    format_run(run_pms, "Arial", 11, bold=False, italic=True, color_rgb=(74, 105, 189))
    
    cover_p3 = add_styled_paragraph(doc, space_before=15, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_appal = cover_p3.add_run("ΑΠΑΛΛΑΚΤΙΚΗ ΕΡΓΑΣΙΑ 2026")
    format_run(run_appal, "Arial", 12, bold=True, color_rgb=(230, 126, 34))
    
    cover_title_p = add_styled_paragraph(doc, space_before=10, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_title = cover_title_p.add_run("ΕΜΠΕΙΡΟ ΣΥΣΤΗΜΑ ΤΟΥΡΙΣΤΙΚΩΝ ΠΡΟΤΑΣΕΩΝ ΜΕ ΧΡΗΣΗ ΑΣΑΦΟΥΣ ΛΟΓΙΚΗΣ (MAMDANI FIS) ΚΑΙ ΟΜΑΔΟΠΟΙΗΣΗ ΠΡΟΦΙΛ ΜΕ FUZZY C-MEANS (FCM)")
    format_run(run_title, "Arial", 18, bold=True, color_rgb=(12, 36, 97))
    
    cover_sub_p = add_styled_paragraph(doc, space_before=4, space_after=40, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_sub = cover_sub_p.add_run("Θέμα 3: Σύστημα Τουριστικών Προτάσεων | Πλήρης Υλοποίηση Βασικού Συστήματος & Επέκτασης FCM")
    format_run(run_sub, "Arial", 11.5, bold=False, italic=True, color_rgb=(74, 105, 189))
    
    # Πίνακας Στοιχείων Έργου
    info_table = doc.add_table(rows=5, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(2.0), Inches(4.5)]
    
    meta_info = [
        ("Μάθημα:", "Ασαφή Συστήματα & Υπολογιστική Νοημοσύνη"),
        ("Διδάσκουσα:", "Δρ. Κ. Χρυσαφιάδη (kchrysafiadi@unipi.gr)"),
        ("Ακαδημαϊκό Έτος:", "2025 - 2026"),
        ("Παραδοτέα Έργου:", "1. Πηγαίος Κώδικας & Εφαρμογή Streamlit (GitHub)\n2. Τεχνική Έκθεση & Εγχειρίδιο Χρήστη (Word .docx & PDF)"),
        ("Αποθετήριο GitHub:", "https://github.com/MrMpek/Tourism-Recommendation-Fuzzy-System")
    ]
    
    for row_idx, (label, val) in enumerate(meta_info):
        row = info_table.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = col_widths[0], col_widths[1]
        set_cell_background(c0, "F8F9FA")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 100, 100, 140, 140)
        set_cell_margins(c1, 100, 100, 140, 140)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        format_run(r0, "Arial", 9.5, bold=True, color_rgb=(30, 55, 153))
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(val)
        format_run(r1, "Arial", 9.5, bold=False, color_rgb=(44, 62, 80))
        
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 1. ΕΙΣΑΓΩΓΗ & ΕΠΙΧΕΙΡΗΣΙΑΚΟ ΠΛΑΙΣΙΟ
    # -------------------------------------------------------------
    add_h1(doc, "1. Εισαγωγή & Επιχειρησιακό Πλαίσιο (B2B Travel Tech)")
    
    p = add_styled_paragraph(doc)
    p.add_run(
        "Η παρούσα εργασία υλοποιεί ένα σύγχρονο, προηγμένο Έμπειρο Σύστημα Τουριστικών Προτάσεων (FuzzyTravel AI), "
        "το οποίο αξιοποιεί συνδυαστικά τις αρχές της Ασαφούς Λογικής (Fuzzy Logic - Mamdani Inference) και της "
        "Ασαφούς Ομαδοποίησης (Fuzzy C-Means Clustering). Στον χώρο της τουριστικής βιομηχανίας, οι ταξιδιωτικές ανάγκες, "
        "οι προτιμήσεις και οι οικονομικές δυνατότητες των πελατών χαρακτηρίζονται από έντονη υποκειμενικότητα, ασάφεια και "
        "αβεβαιότητα. Οι ταξιδιώτες σπάνια σκέφτονται με αυστηρά δυαδικά όρια (π.χ. «θέλω αυστηρά 24.5°C και μέγιστο κόστος 1.150€»). "
        "Αντίθετα, διατυπώνουν τις απαιτήσεις τους με φυσικούς γλωσσικούς όρους όπως «οικονομικός προϋπολογισμός», «ήπιο προς θερμό κλίμα», "
        "«πολυήμερες διακοπές» και «υψηλό ενδιαφέρον για πολιτιστικά αξιοθέατα»."
    )
    
    p2 = add_styled_paragraph(doc)
    p2.add_run(
        "Εμπορική Διάσταση & Αρχιτεκτονική Μεταπώλησης σε Τουριστικά Γραφεία (B2B): "
    )
    format_run(p2.runs[0], bold=True, color_rgb=(30, 55, 153))
    p2.add_run(
        "Το σύστημα σχεδιάστηκε εξαρχής με αρθρωτή αρχιτεκτονική (modular decoupled architecture). "
        "Ο υπολογιστικός και μαθηματικός πυρήνας (Core Engine) είναι πλήρως διαχωρισμένος από το γραφικό περιβάλλον εργασίας (Streamlit UI). "
        "Η προσέγγιση αυτή προσφέρει άμεση εμπορική αξία:\n"
        "• Επιτρέπει σε οποιοδήποτε ταξιδιωτικό πρακτορείο να εισάγει το δικό του δυναμικό απόθεμα (inventory) ταξιδιωτικών πακέτων.\n"
        "• Παρέχει πλήρη Επεξηγησιμότητα (Explainable AI - XAI), επιτρέποντας στον ταξιδιωτικό σύμβουλο να εξηγήσει με σαφήνεια στον πελάτη "
        "τους ακριβείς λόγους για τους οποίους προτείνεται κάθε προορισμός.\n"
        "• Ενσωματώνει λειτουργία παραγωγής επίσημης Εμπορικής Προσφοράς σε PDF (B2B Quotation Export) με στοιχεία πελάτη και οικονομική ανάλυση."
    )
    
    # -------------------------------------------------------------
    # 2. ΣΧΕΔΙΑΣΜΟΣ ΑΣΑΦΟΥΣ ΣΥΣΤΗΜΑΤΟΣ (MAMDANI FIS)
    # -------------------------------------------------------------
    add_h1(doc, "2. Σχεδιασμός Ασαφούς Συστήματος (Mamdani FIS)")
    
    p = add_styled_paragraph(doc)
    p.add_run(
        "Το σύστημα υιοθετεί την κλασική αρχιτεκτονική Mamdani Fuzzy Inference System, η οποία δομείται σε τέσσερα κύρια στάδια:\n"
        "1. Ασαφοποίηση (Fuzzification): Μετατροπή των αριθμητικών τιμών εισόδου σε βαθμούς συμμετοχής μ(x) ∈ [0, 1].\n"
        "2. Αξιολόγηση Βάσης Κανόνων (Rule Evaluation): Υπολογισμός του βαθμού ενεργοποίησης (firing strength) κάθε κανόνα IF-THEN με τον τελεστή Mamdani Min.\n"
        "3. Συνένωση Συμπερασμάτων (Aggregation): Συνδυασμός των επιμέρους ενεργοποιημένων ασαφών συνόλων με τον τελεστή Max.\n"
        "4. Αποσαφοποίηση (Defuzzification): Υπολογισμός του κέντρου βάρους (Centroid) για την εξαγωγή του καθαρού ποσοστού καταλληλότητας (0 - 100%)."
    )
    
    add_h2(doc, "2.1 Μεταβλητές Εισόδου & Συναρτήσεις Συμμετοχής")
    add_styled_paragraph(doc, "Σύμφωνα με τις προδιαγραφές του Θέματος 3, ορίστηκαν 4 θεμελιώδεις κατηγορίες μεταβλητών εισόδου:")
    
    # Πίνακας Μεταβλητών Εισόδου
    t_vars = doc.add_table(rows=5, cols=4)
    t_vars.alignment = WD_TABLE_ALIGNMENT.CENTER
    v_widths = [Inches(1.5), Inches(1.1), Inches(0.8), Inches(3.1)]
    
    headers_vars = ["Μεταβλητή Εισόδου", "Πεδίο Ορισμού (U)", "Μονάδα", "Γλωσσικοί Όροι & Συναρτήσεις Συμμετοχής"]
    for col_idx, text in enumerate(headers_vars):
        cell = t_vars.rows[0].cells[col_idx]
        cell.width = v_widths[col_idx]
        set_cell_background(cell, "1E3799")
        set_cell_margins(cell, 120, 120, 120, 120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        format_run(run, "Arial", 9, bold=True, color_rgb=(255, 255, 255))
        
    data_vars = [
        ("Προϋπολογισμός\n(Budget)", "[100, 5000]", "€", "• Low: Τραπεζοειδής (100, 100, 500, 900)\n• Medium: Τριγωνική (650, 1500, 2500)\n• High: Τραπεζοειδής (2000, 3200, 5000, 5000)"),
        ("Κλίμα / Θερμοκρασία\n(Climate)", "[-10, 45]", "°C", "• Cold: Τραπεζοειδής (-10, -10, 8, 15)\n• Mild: Τριγωνική (12, 20, 27)\n• Warm: Τραπεζοειδής (24, 30, 45, 45)"),
        ("Διάρκεια Ταξιδιού\n(Duration)", "[1, 30]", "Ημέρες", "• Short: Τραπεζοειδής (1, 1, 3, 5)\n• Medium: Τριγωνική (4, 7, 12)\n• Long: Τραπεζοειδής (10, 15, 30, 30)"),
        ("Δραστηριότητες\n(Culture, Adventure,\nRelaxation, Nightlife)", "[0, 10]", "Κλίμακα\n0-10", "• Low: Τραπεζοειδής (0, 0, 2.5, 4.5)\n• Medium: Τριγωνική (3.5, 5.5, 7.5)\n• High: Τραπεζοειδής (6.5, 8.5, 10, 10)")
    ]
    
    for row_idx, row_data in enumerate(data_vars, start=1):
        for col_idx, val in enumerate(row_data):
            cell = t_vars.rows[row_idx].cells[col_idx]
            cell.width = v_widths[col_idx]
            bg = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 100, 100, 120, 120)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            format_run(r, "Arial", 8.5, bold=(col_idx == 0), color_rgb=(44, 62, 80))
            
    # Ενσωμάτωση Εικόνων Συναρτήσεων Συμμετοχής
    fig_dir = os.path.join(os.path.dirname(__file__), "figures")
    mf_budget_img = os.path.join(fig_dir, "mf_budget.png")
    mf_climate_img = os.path.join(fig_dir, "mf_climate.png")
    if os.path.exists(mf_budget_img) and os.path.exists(mf_climate_img):
        add_styled_paragraph(doc, space_before=10, space_after=4)
        t_imgs = doc.add_table(rows=1, cols=2)
        t_imgs.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_imgs.rows[0].cells[0].paragraphs[0].add_run().add_picture(mf_budget_img, width=Inches(3.1))
        t_imgs.rows[0].cells[1].paragraphs[0].add_run().add_picture(mf_climate_img, width=Inches(3.1))
        cap_p = add_styled_paragraph(doc, space_before=2, space_after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        cap_run = cap_p.add_run("Εικόνα 1: Συναρτήσεις Συμμετοχής για Προϋπολογισμό (Budget) και Κλίμα (Climate)")
        format_run(cap_run, "Arial", 8.5, italic=True, color_rgb=(127, 140, 141))
        
    add_h2(doc, "2.2 Βάση Ασαφών Κανόνων (Fuzzy Rule Base)")
    add_styled_paragraph(doc, 
        "Στο σύστημα έχουν οριστεί 18 εξειδικευμένοι κανόνες εμπειρογνώμονα (Expert IF-THEN Rules), "
        "οι οποίοι συνδέουν τις πολυδιάστατες επιθυμίες του ταξιδιώτη με συγκεκριμένα αρχέτυπα προορισμών. "
        "Ο βαθμός ενεργοποίησης κάθε κανόνα α_k υπολογίζεται μέσω του τελεστή Min:"
    )
    add_formula_box(doc, "α_k = min( μ_A1(x_1), μ_A2(x_2), ..., μ_An(x_n) )")
    
    t_rules = doc.add_table(rows=8, cols=3)
    t_rules.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_widths = [Inches(0.8), Inches(3.2), Inches(2.5)]
    
    headers_rules = ["Κανόνας", "Υπόθεση (Antecedent - IF)", "Συμπέρασμα (Consequent - THEN)"]
    for col_idx, text in enumerate(headers_rules):
        cell = t_rules.rows[0].cells[col_idx]
        cell.width = r_widths[col_idx]
        set_cell_background(cell, "1E3799")
        set_cell_margins(cell, 120, 120, 120, 120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        format_run(run, "Arial", 9, bold=True, color_rgb=(255, 255, 255))
        
    sample_rules = [
        ("Κανόνας R01", "Culture is High AND Duration is Short AND Climate is Mild", "Archetype = Cultural & Heritage City (Excellent)"),
        ("Κανόνας R04", "Relaxation is High AND Climate is Warm AND Duration is Medium", "Archetype = Coastal & Island Relaxation (Excellent)"),
        ("Κανόνας R06", "Relaxation is High AND Budget is High AND Climate is Warm", "Archetype = Luxury & Premium Wellness (Excellent)"),
        ("Κανόνας R07", "Adventure is High AND Climate is Cold", "Archetype = Alpine & Mountain Adventure (Excellent)"),
        ("Κανόνας R10", "Nightlife is High AND Duration is Short AND Budget is Low", "Archetype = Vibrant Urban & Entertainment (High)"),
        ("Κανόνας R12", "Adventure is High AND Duration is Long AND Climate is Warm", "Archetype = Exotic & Tropical Explorer (Excellent)"),
        ("Κανόνας R14", "Budget is Low AND Duration is Long", "Archetype = Luxury & Premium Wellness (Poor)")
    ]
    
    for row_idx, (r_id, r_if, r_then) in enumerate(sample_rules, start=1):
        row = t_rules.rows[row_idx]
        for col_idx, val in enumerate([r_id, r_if, r_then]):
            cell = row.cells[col_idx]
            cell.width = r_widths[col_idx]
            bg = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            format_run(r, "Arial", 8.5, bold=(col_idx == 0), color_rgb=(44, 62, 80))
            
    add_h2(doc, "2.3 Μέθοδος Αποσαφοποίησης (Centroid Defuzzification)")
    add_styled_paragraph(doc, 
        "Για τη μετατροπή του συνενωμένου ασαφούς συνόλου εξόδου σε έναν ενιαίο, κατανοητό αριθμό καταλληλότητας (0 - 100%), "
        "εφαρμόζεται η μέθοδος του Κέντρου Βάρους (Center of Gravity / Centroid):"
    )
    add_formula_box(doc, "z* = [ ∫ z · μ_A(z) dz ] / [ ∫ μ_A(z) dz ] ≈ [ Σ (z_i · μ_A(z_i)) ] / [ Σ μ_A(z_i) ]")
    add_styled_paragraph(doc, 
        "Η συνεχής συνάρτηση συμμετοχής διακριτοποιείται σε 200 ισαπέχοντα σημεία στο πεδίο [0, 100], "
        "εξασφαλίζοντας υψηλή υπολογιστική ακρίβεια και ομαλή συμπεριφορά χωρίς άλματα ή ασυνέχειες."
    )
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 3. ΕΠΕΚΤΑΣΗ: FUZZY C-MEANS (FCM)
    # -------------------------------------------------------------
    add_h1(doc, "3. Επέκταση: Fuzzy C-Means (FCM) Customer Profiling")
    
    add_styled_paragraph(doc, 
        "Η επέκταση της εργασίας προβλέπει τη χρήση του αλγορίθμου Fuzzy C-Means (FCM) για την ομαδοποίηση των χρηστών "
        "σε εξατομικευμένα τουριστικά προφίλ (Personas) και την παραγωγή εξατομικευμένων προτάσεων. "
        "Σε αντίθεση με τους κλασικούς αλγορίθμους σκληρής ομαδοποίησης (Hard Clustering όπως το K-Means), "
        "όπου ένα στοιχείο αναγκάζεται να ανήκει αποκλειστικά σε μία ομάδα (u_ij ∈ {0, 1}), το Fuzzy C-Means επιτρέπει "
        "σε έναν ταξιδιώτη να έχει μερικό βαθμό συμμετοχής u_ij ∈ [0, 1] σε πολλαπλά τουριστικά προφίλ ταυτόχρονα. "
        "Αυτό αντικατοπτρίζει απόλυτα την πραγματική ανθρώπινη συμπεριφορά (π.χ. ένας ταξιδιώτης μπορεί να είναι 60% 'Εξερευνητής Πολιτισμού' "
        "και ταυτόχρονα 35% 'Χαλαρωτής Πολυτελείας')."
    )
    
    add_h2(doc, "3.1 Μαθηματική Διατύπωση Αλγορίθμου Bezdek (1981)")
    add_styled_paragraph(doc, "Ο αλγόριθμος FCM ελαχιστοποιεί την παραμετρική αντικειμενική συνάρτηση κόστους J_m:")
    add_formula_box(doc, "J_m = Σ_{i=1}^N Σ_{j=1}^C (u_{ij})^m · || x_i - v_j ||^2")
    add_styled_paragraph(doc, 
        "όπου:\n"
        "• N: Ο αριθμός των ιστορικών ταξιδιωτικών δειγμάτων (dataset χρηστών).\n"
        "• C = 5: Ο αριθμός των τουριστικών συστάδων (clusters / personas).\n"
        "• m = 2.0: Ο συντελεστής ασαφοποίησης (fuzzification parameter).\n"
        "• x_i: Το διάνυσμα χαρακτηριστικών του ταξιδιώτη (Budget, Climate, Duration, Culture, Adventure, Relaxation, Nightlife).\n"
        "• v_j: Το κεντροειδές (prototype center) του j-οστού τουριστικού προφίλ.\n"
        "• u_{ij}: Ο βαθμός συμμετοχής του i-οστού χρήστη στο j-οστό προφίλ, με τον περιορισμό: Σ_{j=1}^C u_{ij} = 1."
    )
    
    add_styled_paragraph(doc, "Οι επαναληπτικές εξισώσεις ανανέωσης κεντροειδών και συμμετοχών ορίζονται ως εξής:")
    add_formula_box(doc, "v_j = [ Σ_{i=1}^N (u_{ij})^m · x_i ] / [ Σ_{i=1}^N (u_{ij})^m ]")
    add_formula_box(doc, "u_{ij} = 1 / [ Σ_{k=1}^C ( || x_i - v_j || / || x_i - v_k || )^( 2 / (m - 1) ) ]")
    
    add_h2(doc, "3.2 Τουριστικά Αρχέτυπα (5 Personas) & Μετρικές Επικύρωσης")
    add_styled_paragraph(doc, "Μέσω του FCM διαμορφώθηκαν 5 αναγνωρίσιμα, σταθερά αρχέτυπα ταξιδιωτών:")
    add_bullet(doc, "1. Cultural & Heritage Explorer", "Επικεντρώνεται στην ιστορία, τα μουσεία και τα μνημεία. Προτιμά ήπιο κλίμα και μεσαίο προς υψηλό budget.")
    add_bullet(doc, "2. Luxury & Wellness Relaxer", "Αναζητά πολυτέλεια, παραλίες, resorts, γαστρονομία και ευεξία. Διαθέτει υψηλό προϋπολογισμό και αναζητά θερμό κλίμα.")
    add_bullet(doc, "3. Budget Backpacker & Youth Nomad", "Νέοι ταξιδιώτες με έμφαση στην περιπέτεια, την αυθεντικότητα και την ευελιξία με χαμηλό κόστος.")
    add_bullet(doc, "4. Alpine & Nature Adventure Seeker", "Λάτρεις των ορεινών όγκων, της πεζοπορίας, του σκι και του δροσερού κλίματος.")
    add_bullet(doc, "5. Cosmopolitan & Nightlife Vibe", "Ταξιδιώτες μεγαλουπόλεων με έμφαση στη νυχτερινή διασκέδαση, τα ψώνια, τα clubs και τα events.")
    
    add_styled_paragraph(doc, "Για την επιστημονική επικύρωση της ασαφούς κατάτμησης υπολογίζονται αυτόματα οι μετρικές Bezdek:")
    add_bullet(doc, "Partition Coefficient (PC)", "PC = (1/N) · Σ Σ (u_ij)^2. Όσο πλησιέστερο στο 1.0, τόσο πιο καθαρός είναι ο διαχωρισμός των συστάδων.")
    add_bullet(doc, "Partition Entropy (PE)", "PE = - (1/N) · Σ Σ [ u_ij · ln(u_ij) ]. Όσο πλησιέστερο στο 0.0, τόσο χαμηλότερη η εντροπία και η σύγχυση.")
    
    mf_fcm_img = os.path.join(fig_dir, "fcm_convergence.png")
    if os.path.exists(mf_fcm_img):
        add_styled_paragraph(doc, space_before=6, space_after=2)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(mf_fcm_img, width=Inches(5.5))
        cap_p = add_styled_paragraph(doc, space_before=2, space_after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        cap_run = cap_p.add_run("Εικόνα 2: Καμπύλη Σύγκλισης Αντικειμενικής Συνάρτησης J_m του FCM (Σύγκλιση εντός 17 επαναλήψεων)")
        format_run(cap_run, "Arial", 8.5, italic=True, color_rgb=(127, 140, 141))
        
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 4. ΤΡΟΠΟΣ ΛΕΙΤΟΥΡΓΙΑΣ & ΜΗΧΑΝΙΣΜΟΣ ΑΝΑΔΡΑΣΗΣ
    # -------------------------------------------------------------
    add_h1(doc, "4. Τρόπος Λειτουργίας & Δυναμικός Μηχανισμός Ανάδρασης (Feedback Loop)")
    
    add_styled_paragraph(doc, 
        "Σύμφωνα με τις προδιαγραφές της εργασίας, το σύστημα δεν είναι ένας στατικός μηχανισμός υπολογισμού, "
        "αλλά διαθέτει έναν ολοκληρωμένο, κλειστό βρόχο ανάδρασης (Closed Feedback Loop). "
        "Ο μηχανισμός αυτός επιτρέπει στο σύστημα να μαθαίνει από τις αξιολογήσεις των χρηστών και των ταξιδιωτικών συμβούλων, "
        "προσαρμόζοντας δυναμικά τις μελλοντικές του συστάσεις."
    )
    
    add_h2(doc, "4.1 Αρχιτεκτονική Ροής & Ανάδρασης σε 4 Βήματα")
    add_bullet(doc, "Βήμα 1: Εισαγωγή & Fuzzification", "Ο χρήστης δηλώνει τις επιθυμίες του στην εφαρμογή (Budget, Κλίμα, Διάρκεια, Δραστηριότητες).")
    add_bullet(doc, "Βήμα 2: Υβριδική Εκτίμηση (Mamdani + FCM)", "Το σύστημα υπολογίζει το ταξιδιωτικό προφίλ (Soft Persona) και βαθμολογεί όλους τους προορισμούς.")
    add_bullet(doc, "Βήμα 3: Συλλογή Ανάδρασης (Feedback Collection)", "Για κάθε προτεινόμενο προορισμό, ο χρήστης βαθμολογεί (1-5 αστέρια), δηλώνει αποδοχή/απόρριψη και προσθέτει σχόλιο.")
    add_bullet(doc, "Βήμα 4: Προσαρμοστική Επαναστάθμιση (Adaptive Tuning)", "Το ιστορικό ανάδρασης ανατροφοδοτεί το σκορ των προορισμών σε πραγματικό χρόνο.")
    
    add_h2(doc, "4.2 Μαθηματικό Μοντέλο Προσαρμογής Ανάδρασης")
    add_styled_paragraph(doc, "Το τελικό σκορ καταλληλότητας κάθε προορισμού υπολογίζεται σύμφωνα με τον τύπο:")
    add_formula_box(doc, "FinalScore = BaseScore + Δ_feedback")
    add_formula_box(doc, "Δ_feedback = w_r · ( r̄ - 3.0 ) + w_a · ( AcceptanceRate - 0.5 )")
    add_styled_paragraph(doc, 
        "όπου:\n"
        "• r̄ ∈ [1.0, 5.0]: Η μέση ιστορική βαθμολογία αστεριών του συγκεκριμένου προορισμού.\n"
        "• AcceptanceRate ∈ [0.0, 1.0]: Το ποσοστό αποδοχής του προορισμού από τους πελάτες.\n"
        "• w_r = 4.0, w_a = 4.0: Συντελεστές στάθμισης.\n"
        "Εάν ένας προορισμός λαμβάνει σταθερά άριστες κριτικές (5 αστέρια και αποδοχή), κερδίζει πριμ καταλληλότητας έως +10%, "
        "ενώ προορισμοί με αρνητικά σχόλια υποβαθμίζονται αυτόματα στις μελλοντικές προτάσεις."
    )
    
    add_h2(doc, "4.3 Επεξηγηματική Τεχνητή Νοημοσύνη (Explainable AI - XAI)")
    add_styled_paragraph(doc, 
        "Σε αντίθεση με τα μοντέλα 'μαύρου κουτιού' (Black-Box ML), το σύστημα παρέχει διαφανή αιτιολόγηση (XAI Rationale) "
        "για κάθε πρόταση, αναλύοντας στον πελάτη:\n"
        "• Τη συμβατότητα του κόστους με τον προϋπολογισμό του.\n"
        "• Τη θερμοκρασιακή απόκλιση από το επιθυμητό κλίμα.\n"
        "• Την ταύτιση των δραστηριοτήτων με το κυρίαρχο FCM ταξιδιωτικό του προφίλ.\n"
        "• Την ιστορική ικανοποίηση άλλων ταξιδιωτών από τον προορισμό."
    )
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 5. ΕΓΧΕΙΡΙΔΙΟ ΧΡΗΣΤΗ ΕΦΑΡΜΟΓΗΣ (USER MANUAL)
    # -------------------------------------------------------------
    add_h1(doc, "5. Εγχειρίδιο Χρήστη Εφαρμογής (User Manual)")
    
    add_styled_paragraph(doc, 
        "Η εφαρμογή FuzzyTravel AI παρέχει ένα σύγχρονο, εύχρηστο γραφικό περιβάλλον (Streamlit Web GUI), "
        "ειδικά σχεδιασμένο τόσο για τον τελικό χρήστη / ταξιδιώτη όσο και για τον επαγγελματία ταξιδιωτικό πράκτορα."
    )
    
    add_h2(doc, "5.1 Οδηγίες Εγκατάστασης & Εκτέλεσης (Setup & Launch)")
    add_styled_paragraph(doc, "Η εκτέλεση του συστήματος είναι άμεση και πραγματοποιείται με δύο εναλλακτικούς τρόπους:")
    add_bullet(doc, "Μέθοδος 1 (Με ένα κλικ σε macOS)", "Κάντε διπλό κλικ στο εκτελέσιμο αρχείο run_app.command που βρίσκεται στον ριζικό φάκελο του έργου.")
    add_bullet(doc, "Μέθοδος 2 (Μέσω Τερματικού)", "Ανοίξτε το τερματικό στον φάκελο του έργου και εκτελέστε:\n"
                                                  "   source venv/bin/activate\n"
                                                  "   streamlit run ui/app.py\n"
                                                  "Η εφαρμογή ανοίγει αυτόματα στον web browser στη διεύθυνση http://localhost:8501.")
    
    add_h2(doc, "5.2 Λειτουργία 1: Σύμβουλος Προτάσεων (Travel Agent Recommender)")
    add_styled_paragraph(doc, 
        "Αποτελεί την κεντρική οθόνη εργασίας του ταξιδιωτικού πράκτορα:\n"
        "1. Πλευρική Στήλη (Sidebar): Εισαγωγή παραμέτρων ταξιδιώτη (Budget, Κλίμα, Διάρκεια) και επιλογή έντασης δραστηριοτήτων (Πολιτισμός, Περιπέτεια, Χαλάρωση, Νυχτερινή Ζωή).\n"
        "2. Ταξιδιωτικό DNA (FCM Soft Persona): Άμεση οπτικοποίηση του προφίλ του πελάτη σε διαδραστικό διάγραμμα ραντάρ (Plotly Radar Chart).\n"
        "3. Προτεινόμενοι Προορισμοί: Παρουσίαση των κορυφαίων 5 προορισμών με ποσοστό καταλληλότητας, φωτογραφία υψηλής ευκρίνειας, προτεινόμενο πακέτο γραφείου, ανάλυση κόστους και πλήρη αιτιολόγηση (XAI).\n"
        "4. Φόρμα Ανάδρασης (Feedback): Υποβολή αξιολόγησης (1-5 αστέρια και σχόλιο) κάτω από κάθε κάρτα προορισμού.\n"
        "5. Εξαγωγή Επίσημης Προσφοράς σε PDF (B2B Quotation): Ο σύμβουλος εισάγει τα στοιχεία του πελάτη και με το πάτημα ενός κουμπιού εξάγει επίσημη ταξιδιωτική προσφορά σε PDF."
    )
    
    add_h2(doc, "5.3 Λειτουργία 2: Ακαδημαϊκή Εποπτεία & Μαθηματικός Έλεγχος")
    add_styled_paragraph(doc, 
        "Σχεδιασμένη ειδικά για την αξιολόγηση του μαθήματος και τον επιστημονικό έλεγχο:\n"
        "• Προβολή Συναρτήσεων Συμμετοχής: Διαδραστικά γραφήματα με κατακόρυφη ένδειξη των τρεχουσών τιμών εισόδου.\n"
        "• Πίνακας Ενεργών Κανόνων: Εμφάνιση των 18 κανόνων με τον ακριβή βαθμό ενεργοποίησης (firing strength) σε πραγματικό χρόνο.\n"
        "• Μετρικές FCM: Εμφάνιση της καμπύλης σύγκλισης, του αριθμού επαναλήψεων και των δεικτών ποιότητας Partition Coefficient (PC) και Partition Entropy (PE).\n"
        "• Ζωντανό Ιστορικό Ανάδρασης: Πίνακας καταγεγραμμένων αξιολογήσεων και υπολογισμός μέσου όρου ικανοποίησης."
    )
    
    add_h2(doc, "5.4 Λειτουργία 3: Διαχείριση Καταλόγου & Αποθέματος (Inventory Management)")
    add_styled_paragraph(doc, 
        "Περιλαμβάνει 22 πλήρως καταγεγραμμένους προορισμούς (12 ελληνικούς και 10 διεθνείς):\n"
        "• Ελληνικοί Προορισμοί: Σαντορίνη, Χανιά, Ζαγοροχώρια, Αθήνα, Μύκονος, Πήλιο, Μετέωρα, Κέρκυρα, Νάξος, Μάνη/Μονεμβασιά, Καστοριά, Ναύπλιο.\n"
        "• Διεθνείς Προορισμοί: Ρώμη, Παρίσι, Βιέννη, Ζερμάτ, Ρέικιαβικ, Μπαλί, Βαρκελώνη, Άμστερνταμ, Τόκιο, Νέα Υόρκη.\n"
        "• Δυνατότητες: Προβολή πίνακα προορισμών, εξαγωγή σε αρχείο CSV, και φόρμα άμεσης προσθήκης νέου τουριστικού πακέτου."
    )
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 6. ΣΥΜΠΕΡΑΣΜΑΤΑ & ΕΜΠΟΡΙΚΕΣ ΠΡΟΟΠΤΙΚΕΣ
    # -------------------------------------------------------------
    add_h1(doc, "6. Συμπεράσματα, Αξιολόγηση & Εμπορικές Προοπτικές")
    
    add_styled_paragraph(doc, 
        "Η παρούσα υλοποίηση ολοκληρώνει πλήρως τόσο τις βασικές προδιαγραφές του Θέματος 3 όσο και την απαιτητική "
        "επέκταση του Fuzzy C-Means (FCM) Clustering. Τα συμπεράσματα που προκύπτουν από την υλοποίηση είναι τα ακόλουθα:"
    )
    
    add_bullet(doc, "1. Ανωτερότητα Ασαφούς Λογικής", "Η χρήση της Ασαφούς Λογικής Mamdani αποδεικνύεται ιδανική για τουριστικές συστάσεις, καθώς εξαλείφει την αυστηρότητα των κλασικών συστημάτων βάσεων δεδομένων και επιτρέπει ομαλές, φυσικές διαβαθμίσεις.")
    add_bullet(doc, "2. Προστιθέμενη Αξία του FCM", "Το FCM επιτρέπει την πολυδιάστατη χαρτογράφηση των ταξιδιωτών. Αντί να κατατάσσει τον πελάτη σε ένα άκαμπτο 'κουτάκι', δημιουργεί ένα εξατομικευμένο 'Ταξιδιωτικό DNA' (Soft Persona) που βελτιώνει θεαματικά την ακρίβεια των συστάσεων.")
    add_bullet(doc, "3. Αυτοπροσαρμογή μέσω Feedback Loop", "Ο κλειστός βρόχος ανάδρασης προσδίδει στο σύστημα αυτομάθηση. Προορισμοί με υψηλή αποδοχή ενισχύονται, ενώ μη επιτυχημένες προτάσεις υποβαθμίζονται χωρίς να απαιτείται επαναπρογραμματισμός.")
    add_bullet(doc, "4. Επιχειρηματική Ετοιμότητα (B2B Ready)", "Η παραγωγή επίσημης προσφοράς PDF, η πλήρης επεξηγησιμότητα (XAI) και η διαχείριση αποθέματος καθιστούν το σύστημα ένα άμεσα εμπορεύσιμο προϊόν (Commercial MVP) για τουριστικά γραφεία.")
    
    add_styled_paragraph(doc, space_before=10)
    add_styled_paragraph(doc, 
        "Μελλοντικές Επεκτάσεις: Περαιτέρω εξέλιξη του συστήματος μπορεί να περιλαμβάνει τη μετατροπή του μαθηματικού πυρήνα "
        "σε Cloud Microservice μέσω FastAPI, την απευθείας σύνδεση με εξωτερικά APIs κρατήσεων (Amadeus, Booking, Skyscanner) "
        "και την εκτέλεση Dynamic Online Clustering σε μεγάλα σύνολα δεδομένων πραγματικών κρατήσεων."
    )
    
    # Αποθήκευση εγγράφου Word
    doc.save(output_path)
    print(f"Academic Report Word document successfully compiled to: {output_path}")

if __name__ == "__main__":
    docx_out = os.path.join(os.path.dirname(__file__), "Fuzzy_Tourism_Recommendation_System_Report.docx")
    build_docx_report(docx_out)
