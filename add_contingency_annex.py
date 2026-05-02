import os
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# --- CONFIGURATION ---
OUTPUT_DIR = "outputs"
BASE_REPORT = "philippines_mission_intel_status_report_latest.pdf"
ANNEX_FILENAME = "Annex_C_Evacuation.pdf"
FINAL_REPORT = "philippines_mission_intel_status_report_COMPLETE.pdf"

def create_annex_pdf():
    """Generates the Annex C PDF page."""
    doc = SimpleDocTemplate(ANNEX_FILENAME, pagesize=LETTER)
    styles = getSampleStyleSheet()
    
    # Matching the PMISR aesthetic (All-caps headers, bold identifiers)
    h1 = ParagraphStyle('H1', fontSize=14, leading=16, alignment=1, spaceAfter=12, fontName='Helvetica-Bold')
    h2 = ParagraphStyle('H2', fontSize=12, leading=14, spaceAfter=10, fontName='Helvetica-Bold')
    body = ParagraphStyle('Body', fontSize=10, leading=12, spaceAfter=6)
    warn = ParagraphStyle('Warn', fontSize=10, leading=12, textColor=colors.red, fontName='Helvetica-Bold')

    elements = []

    # Header - Reference to Strategic Global Intelligence Command
    elements.append(Paragraph("STRATEGIC GLOBAL INTELLIGENCE COMMAND", h1))
    elements.append(Paragraph("ANNEX C: NORTHERN LUZON (NAMUAC) EVACUATION PLAN", h2))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))

    # Tactical Data Table
    table_data = [
        ["OP-NAME", "EXODUS-ILOILO"],
        ["EVACUEE COUNT", "15 Pax (Max)"],
        ["PRIMARY ASSET", "Private Minivan / Florida Bus (Backup)"],
        ["COMMS PATH", "PACE: Garmin InReach (Primary) / GSM (Contingency)"],
        ["DESTINATION", "Iloilo City Property (3-BR/Single Family)"]
    ]
    t = Table(table_data, colWidths=[120, 330])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    # Phase Breakdown
    elements.append(Paragraph("1. CONDITION TRIGGERS", h2))
    elements.append(Paragraph("<b>AMBER:</b> Initial movement Prep. Source/Install Backup Generator in Iloilo. Full fuel status (60L reserve).", body))
    elements.append(Paragraph("<b>RED:</b> Immediate Ground Egress via AH26 toward Manila.", body))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("2. ROUTE & VULNERABILITIES", h2))
    elements.append(Paragraph("• <b>Primary Route:</b> AH26 (Cagayan Valley Rd) to Manila North Harbor.", body))
    elements.append(Paragraph("• <b>CHOKEPOINT:</b> Magapit Bridge (Lal-lo). If compromised, egress is SEVERED.", warn))
    elements.append(Paragraph("• <b>SECURITY:</b> Asset protection currently UNPLANNED. High visibility risk for 15-pax group.", warn))

    doc.build(elements)
    return ANNEX_FILENAME

def merge_to_master():
    """Appends the Annex to the latest master report."""
    base_path = os.path.join(OUTPUT_DIR, BASE_REPORT)
    if not os.path.exists(base_path):
        print(f"Error: {BASE_REPORT} not found in {OUTPUT_DIR}")
        return

    writer = PdfWriter()
    
    # Add existing report
    with open(base_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    
    # Add Annex
    with open(ANNEX_FILENAME, "rb") as f:
        annex_reader = PdfReader(f)
        writer.add_page(annex_reader.pages[0])

    with open(os.path.join(OUTPUT_DIR, FINAL_REPORT), "wb") as f_out:
        writer.write(f_out)
    
    print(f"Successfully integrated Annex C into {FINAL_REPORT}")
    # Cleanup temporary annex file
    os.remove(ANNEX_FILENAME)

if __name__ == "__main__":
    create_annex_pdf()
    merge_to_master()