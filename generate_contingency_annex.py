import os
from datetime import datetime
from PIL import Image as PILImage
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, Image

# --- PATH & DIRECTORY LOGIC ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "outputs")
EMBLEM_SRC = os.path.join(BASE_DIR, "emblem.jpg")
FINAL_REPORT_PATH = os.path.join(TARGET_DIR, "PMISR_Annex_C_Complete.pdf")
EMBLEM_TRANS_PATH = os.path.join(TARGET_DIR, "emblem_transparent.png")

def process_emblem(src, dest):
    if not os.path.exists(src): return False
    try:
        img = PILImage.open(src).convert("RGBA")
        img.thumbnail((350, 350)) 
        new_img = PILImage.new("RGBA", img.size)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                r, g, b, a = img.getpixel((x, y))
                if r > 230 and g > 230 and b > 230:
                    new_img.putpixel((x, y), (255, 255, 255, 0))
                else:
                    new_img.putpixel((x, y), (r, g, b, a))
        new_img.save(dest, "PNG")
        return True
    except: return False

def generate_report():
    if not os.path.exists(TARGET_DIR): os.makedirs(TARGET_DIR)
    has_emblem = process_emblem(EMBLEM_SRC, EMBLEM_TRANS_PATH)

    doc = SimpleDocTemplate(FINAL_REPORT_PATH, pagesize=LETTER, 
                            rightMargin=75, leftMargin=75, topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    
    # --- STYLE REFINEMENT ---
    title_style = ParagraphStyle('Title', fontSize=24, leading=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    sub_title_style = ParagraphStyle('Sub', fontSize=13, leading=18, alignment=TA_CENTER, fontName='Helvetica-Bold')
    class_style = ParagraphStyle('Class', fontSize=12, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.darkgreen)
    h2_style = ParagraphStyle('H2', fontSize=12, leading=18, fontName='Helvetica-Bold', spaceBefore=35, spaceAfter=20, underline=True)
    body_style = ParagraphStyle('Body', fontSize=10, leading=16, spaceAfter=15)
    warn_style = ParagraphStyle('Warn', fontSize=10, leading=16, textColor=colors.red, fontName='Helvetica-Bold', spaceAfter=15)

    elements = []

    # --- PAGE 1: TITLE PAGE ---
    elements.append(Paragraph("UNCLASSIFIED // OPEN SOURCE", class_style))
    elements.append(Spacer(1, 100))
    if has_emblem:
        elements.append(Image(EMBLEM_TRANS_PATH, width=115, height=115))
        elements.append(Spacer(1, 40))
    elements.append(Paragraph("STRATEGIC GLOBAL INTELLIGENCE COMMAND", sub_title_style))
    elements.append(Spacer(1, 70))
    elements.append(Paragraph("PHILIPPINES MISSION INTEL STATUS REPORT", title_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("ANNEX C: TOTAL EXFILTRATION PLAN (NORTH LUZON TO ILOILO)", sub_title_style))
    elements.append(Spacer(1, 130))
    
    meta_table = Table([
        ["DATE GENERATED:", datetime.now().strftime("%d %b %Y")],
        ["AREA OF OPERATIONS:", "NORTH LUZON / MANILA / ILOILO"],
        ["PREPARED BY:", "INTELLIGENCE SECTION"],
        ["COORD (NAMUAC):", "18.5714, 121.2319"]
    ], colWidths=[150, 250])
    meta_table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'), ('BOTTOMPADDING', (0,0), (-1,-1), 18)]))
    elements.append(meta_table)
    elements.append(PageBreak())

    # --- PAGE 2: CONDITIONS & INDICATORS ---
    elements.append(Paragraph("SECTION 1: INTELLIGENCE INDICATORS & COA", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=25))
    
    elements.append(Paragraph("<b>CONDITION AMBER (PREPARATORY PHASE)</b>", body_style))
    elements.append(Paragraph("This condition represents a significant departure from regional stability norms. Indicators include PLA mobilization in the Southern Theater Command, increased naval activity in the Bashi Channel, or gray-zone disruptions to national infrastructure.", body_style))
    elements.append(Paragraph("<b>Actions:</b> Verify Iloilo property status; source and test backup generator; stage 60L diesel in jerry cans; synchronize PACE plan with family members.", body_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>CONDITION RED (EXECUTION PHASE)</b>", warn_style))
    elements.append(Paragraph("This condition represents imminent or active kinetic hostility. Indicators include strikes on EDCA sites, confirmed amphibious task force movement toward Luzon, or the closure of national civilian airspace.", warn_style))
    elements.append(Paragraph("<b>Actions:</b> Immediate 'No-Notice' departure. Execute primary air egress if available; otherwise, transition to ground egress via AH26. Priority is 'Getting off the X' and clearing the northern coast.", warn_style))
    elements.append(PageBreak())

    # --- PAGE 3: PHASE I - DEPARTURE (AIR/GROUND) ---
    elements.append(Paragraph("SECTION 2: PHASE I - DEPARTURE LOGISTICS (NAMUAC TO MANILA)", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=20))
    
    elements.append(Paragraph("<b>2.1 AIR EGRESS CONTINGENCY (LAOAG)</b>", body_style))
    elements.append(Paragraph("If the Luzon Strait is not contested, Laoag International Airport (LAO) is the preferred rapid-egress point. Movement must be coordinated via the Pan-Philippine Hwy (3-hour ground transit).", body_style))
    
    air_data = [
        ["CARRIER", "WEBSITE", "HOTLINE"],
        ["Philippine Airlines", "philippineairlines.com", "(+632) 8855-8888"],
        ["Cebu Pacific Air", "cebupacificair.com", "(+632) 8702-0888"]
    ]
    t_air = Table(air_data, colWidths=[130, 160, 160])
    t_air.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_air)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>2.2 GROUND EGRESS CONTINGENCY (AH26)</b>", body_style))
    elements.append(Paragraph("If air assets are grounded or Laoag is compromised, the high-occupancy van (15-pax load) will utilize the Cagayan Valley Road (AH26).", body_style))
    
    route_data = [
        ["SECTOR", "COORD / KEY POINT", "EST. TIME"],
        ["Namuac-Aparri", "18.3583, 121.6311", "1.5h"],
        ["Magapit Bridge", "18.1219, 121.6744", "0.5h"],
        ["Dalton Pass", "16.1311, 120.9322", "2.0h"],
        ["Manila Pier 4", "14.6144, 120.9536", "3.0h"]
    ]
    t_route = Table(route_data, colWidths=[110, 260, 80])
    t_route.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_route)
    elements.append(PageBreak())

    # --- PAGE 4: PHASE II - MARITIME ---
    elements.append(Paragraph("SECTION 3: PHASE II - MARITIME TRANSIT (MANILA TO ILOILO)", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=20))
    
    elements.append(Paragraph("Ground movement terminates at Manila North Harbor. Personnel and assets will transfer to a ROPAX ferry for Visayas transit. 2GO Travel is the primary provider for this leg.", body_style))
    
    maritime_data = [
        ["OPERATOR", "2GO Travel (Pier 4, Manila North Harbor)"],
        ["HOTLINE", "(+632) 8528-7000"],
        ["SEA TRANSIT", "Manila North Harbor to Iloilo Port (Fort San Pedro)"],
        ["DURATION", "20 - 24 Hours Transit Window"],
        ["DESTINATION", "Iloilo City Port (Lapuz District) - 10.6908, 122.5833"]
    ]
    t_mar = Table(maritime_data, colWidths=[130, 320])
    t_mar.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), ('PADDING', (0,0), (-1,-1), 14)]))
    elements.append(t_mar)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Coordination:</b> Family Head must utilize cellular connectivity during Phase I (Isabela sector) to verify vessel departure times and manifest space for 15 personnel.", body_style))
    elements.append(PageBreak())

    # --- PAGE 5: PACE & MEDICAL ---
    elements.append(Paragraph("SECTION 4: PACE PLAN (TRANS & COMMS)", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=20))
    
    pace_data = [
        ["LEVEL", "TRANSPORTATION", "COMMUNICATIONS"],
        ["PRIMARY", "Air (Laoag -> Manila) + Ferry", "Garmin InReach (Satellite)"],
        ["ALTERNATE", "Ground (AH26) + Ferry", "GSM / Cellular (LTE)"],
        ["CONTINGENCY", "Ground (AH26) -> Batangas Port", "Local Radio / Shortwave"],
        ["EMERGENCY", "Small Craft (Maritime Bypass)", "Courier / Signal Signs"]
    ]
    t_pace = Table(pace_data, colWidths=[100, 175, 175])
    t_pace.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_pace)

    elements.append(Paragraph("SECTION 5: MEDICAL SUPPORT (ROUTE HOSPITALS)", h2_style))
    med_data = [
        ["REGION", "FACILITY NAME", "CAPABILITY"],
        ["Cagayan", "Cagayan Valley Medical Center", "Level-3 / Trauma"],
        ["Laoag", "Laoag City General Hospital", "Secondary / Surgical"],
        ["N. Ecija", "Premiere Medical Center", "Regional Trauma"],
        ["Manila", "Manila Doctors Hospital", "Tertiary / Specialized"]
    ]
    t_med = Table(med_data, colWidths=[100, 175, 175])
    t_med.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_med)
    elements.append(PageBreak())

    # --- PAGE 6: CHOKEPOINTS & BYPASS ---
    elements.append(Paragraph("SECTION 6: KEY CHOKEPOINTS & EMERGENCY BYPASSES", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=25))

    elements.append(Paragraph("<b>6.1 MAGAPIT BRIDGE (Lal-lo):</b>", warn_style))
    elements.append(Paragraph("Interdiction at this point severs ground egress from the northern coast. <b>Action:</b> Divert to Camalaniugan Port. Secure small boat charter ('Banca') for personnel river ferry. Abandon primary vehicle; coordinate secondary pickup on the East Bank.", warn_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>6.2 DALTON PASS (Santa Fe):</b>", warn_style))
    elements.append(Paragraph("Single mountain link between Cagayan and Central Luzon. <b>Action:</b> If blocked by landslide or blockade, hold at Santiago, Isabela. Secure residential cover; avoid unpaved mountain trails in overloaded van.", warn_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>6.3 PORT FALLBACK (BATANGAS):</b>", warn_style))
    elements.append(Paragraph("If Manila North Harbor is seized or unusable, redirect the group to Batangas Port (2 hrs south of Manila). Batangas serves as the secondary RORO/ROPAX hub for Visayas-bound exfiltration.", warn_style))
    elements.append(Spacer(1, 60))
 
    elements.append(Paragraph("SECTION 7: COMMAND, CONTROL, & AUTHENTICATION", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=20))

    elements.append(Paragraph("<b>7.1 IN-TRANSIT SITREP (Garmin InReach Template):</b>", body_style))
    elements.append(Paragraph("To be transmitted every 4 hours or upon crossing major chokepoints:", body_style))
    elements.append(Paragraph("• <b>POS:</b> [Current Landmark/Coord] <br/>• <b>STAT:</b> [Green/Amber/Red] + [Fuel %] <br/>• <b>INT:</b> [Next Waypoint]", body_style))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>7.2 AUTHENTICATION (Condition Red Only):</b>", body_style))
    auth_data = [
        ["TYPE", "CHALLENGE", "REPLY"],
        ["Fixed Password", "STORM", "SHELTER"],
        ["Running Password", "ARROW", "N/A"],
        ["Recognition Signal", "Orange Cloth", "N/A"]
    ]
    t_auth = Table(auth_data, colWidths=[120, 165, 165])
    t_auth.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_auth)
    elements.append(PageBreak())

    # --- PAGE 8: BAILOUT & SUSTAINMENT ---
    elements.append(Paragraph("SECTION 8: BAILOUT & SUSTAINMENT DRILLS", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=20))

    elements.append(Paragraph("<b>8.1 VEHICLE BAILOUT PROTOCOL:</b>", warn_style))
    elements.append(Paragraph("If the primary vehicle is immobilized or interdicted, the Family Head initiates 'Bailout.'", body_style))
    elements.append(Paragraph("• <b>Immediate Action:</b> Passengers exit via the side opposite of the threat. Rally at a minimum distance of 50m behind cover.", body_style))
    elements.append(Paragraph("• <b>Accountability:</b> Perform a head-count (15 pax). Do not move until 100% accountability is confirmed.", body_style))
    
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("<b>8.2 SECTOR-SPECIFIC SUSTAINMENT:</b>", body_style))
    sust_data = [
        ["ITEM", "SPECIFICATION", "QTY / PAX"],
        ["Water", "Potable / Sealed", "3 Liters"],
        ["Rations", "High-Calorie / No-Cook", "72 Hours"],
        ["First Aid", "IFAK / Trauma Kit", "1 per vehicle"],
        ["Documentation", "Physical ID + Property Deeds", "Originals"]
    ]
    t_sust = Table(sust_data, colWidths=[120, 210, 120])
    t_sust.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_sust)

    elements.append(Spacer(1, 60))
    elements.append(Paragraph("<b>END OF ANNEX C</b>", sub_title_style))

    try:
        doc.build(elements)
        print(f"[*] Success! All-in-One Tactical Plan saved to: {FINAL_REPORT_PATH}")
    except PermissionError:
        print(f"\n[!] ERROR: Permission Denied. Close the PDF and try again.\n")

if __name__ == "__main__":
    generate_report()

