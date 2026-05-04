from __future__ import annotations
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    Image,
    PageTemplate,
    Frame,
    NextPageTemplate,
)
from asyncio import events
import shutil
import json
from analysis.condition_engine import evaluate_condition
import sys
import traceback

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
]

FONT_NAME = "Helvetica"

for font_path in FONT_CANDIDATES:
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(font_path)))
        FONT_NAME = FONT_NAME
        break
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Table
from pathlib import Path
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from unittest import signals
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, lightgrey, white
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from config import ANNEX_C_PATH, PMISR_V2_TEMPLATE_PATH
from reportlab.graphics.shapes import Drawing, Line

BASE_DIR = Path(__file__).resolve().parent
SEAL_PATH = BASE_DIR / "mission_analysis_seal.svg"

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from analysis.commanders_summary import generate_commanders_summary
from analysis.crisis_banner import build_crisis_banner
from analysis.delta_summary import generate_delta_summary
from analysis.normalizer import payloads_to_events
from analysis.quality_control import generate_quality_control_summary
from analysis.report_order import REPORT_SECTION_ORDER
from analysis.section_builders import (
    build_internal_security_section,
    build_regional_maritime_section,
)
from analysis.section_enrichment import enrich_section
from analysis.signal_engine import detect_signals
from diffs.report_delta import count_diff_lines, diff_text
from freshness.freshness_validator import FreshnessValidationError, validate_all_sources
from sources.base import SourceAdapterError
from sources.collector import collect_all_sources
from sources.source_models import SourcePayload
from validators.report_validator import (
    ReportValidationError,
    validate_report_pdf,
    validate_report_text,
)
from config import LATEST_DIR, ARCHIVE_DIR
from analysis.decision_engine import evaluate_posture
from reportlab.lib.pagesizes import landscape, letter

SECTION_COMMANDERS_SUMMARY = "Commander's Summary"
SECTION_STRATEGIC_SITUATION = "Strategic Situation"
SECTION_PRIORITY_INTELLIGENCE = "Priority Intelligence"
SECTION_EMBASSY = "U.S. Embassy (Manila) travel advisories"
SECTION_STATE = "U.S. State Department travel advisories for Americans"
SECTION_HEALTH_ENVIRONMENT = "Health / Environmental Risk"
SECTION_WEATHER = "Weather Forecast - MANILA / NAIA"
SECTION_GEOLOGICAL = "Geological / Volcanic Activity"
SECTION_NAIA = "NAIA / airport operational status"
SECTION_DECISION = "Decision Guidance"
SECTION_ESCALATION = "Escalation Thresholds"
SECTION_REGIONAL_MIL_ACTIVITY = "Regional Military Activity / Movement"
SECTION_CONTINGENCY = "Contingency Evacuation"
SECTION_CHANGES = "Significant Changes Since Last Report"
SECTION_QC = "Quality Control Summary"
SECTION_SOUTHERN_MOBILITY = "Southern Ground / Maritime Mobility Blueprint"


OUTPUT_DIR = Path("outputs")
LATEST_DIR = OUTPUT_DIR / "latest"
ARCHIVE_DIR = OUTPUT_DIR / "archive"
LOG_DIR = Path("logs")
STATUS_FILE = LOG_DIR / "daily_status.json"

SIGNIFICANT_DIFF_THRESHOLD = 5

PDF_HEADER_TITLE = "PHILIPPINES MISSION INTEL STATUS REPORT"
PDF_CLASSIFICATION = "UNCLASSIFIED // OPEN SOURCE"
PDF_HEADER_BAND_HEIGHT = 20
PDF_BORDER_INSET = 16
PDF_FOOTER_Y = 18

REQUIRED_SECTION_FALLBACKS = {
    SECTION_STRATEGIC_SITUATION: (
        f"{SECTION_STRATEGIC_SITUATION}\n\n"
        "Strategic situation could not be fully refreshed from live sources. "
        "Treat this section as baseline context only. Verify current security, transportation, weather, and health indicators before movement."
    ),

    SECTION_REGIONAL_MIL_ACTIVITY: (
        f"{SECTION_REGIONAL_MIL_ACTIVITY}\n\n"
        "No reportable regional military activity detected in monitored open-source feeds during this collection cycle.\n\n"
        "Monitoring emphasis remains: Philippine Sea, West Philippine Sea, Luzon Strait, Batanes, Palawan, Taiwan approaches, "
        "Scarborough Shoal, EDCA sites, maritime patrol activity, air/naval exercises, missile deployments, coast guard interactions, "
        "and official defense statements.\n\n"
        "Confidence: Medium"
    ),
    
    SECTION_PRIORITY_INTELLIGENCE: (
        f"{SECTION_PRIORITY_INTELLIGENCE}\n\n"
        "No current PLA / regional military activity met freshness threshold. "
        "Continue monitoring Taiwan Strait, Luzon approaches, WPS indicators, aviation restrictions, and regional military posture."
    ),

    SECTION_EMBASSY: (
        f"{SECTION_EMBASSY}\n\n"
        "U.S. Embassy Manila travel advisories could not be fully refreshed from live source content. "
        "Monitor embassy alerts and security messages before movement."
    ),

    SECTION_STATE: (
        f"{SECTION_STATE}\n\n"
        "U.S. State Department advisory posture should be treated as baseline travel-risk guidance. "
        "Monitor for advisory level changes, region-specific warnings, or new security messages affecting movement."
    ),

    SECTION_HEALTH_ENVIRONMENT: (
        f"{SECTION_HEALTH_ENVIRONMENT}\n\n"
        "Baseline health risks remain present: heat injury, dehydration, food/water illness, mosquito-borne disease, and fatigue. "
        "Maintain hydration, food/water discipline, insect repellent, and basic medication access."
    ),

    SECTION_WEATHER: (
        f"{SECTION_WEATHER}\n\n"
        "Weather data unavailable at generation time. Verify local conditions prior to movement."
        "Check current local forecast before movement, with emphasis on heat index, heavy rain, flooding, and travel disruption."
    ),

    SECTION_NAIA: (
        f"{SECTION_NAIA}\n\n"
        "NAIA remains operational unless confirmed otherwise. Public reporting should not be treated as a sole-source indicator. "
        "Cross-check airline status, airport displays, and flight tracking before movement."
    ),
    
}
SOUTHERN_MOBILITY_BLUEPRINT = """Southern Ground / Maritime Mobility Blueprint

## 1. INTENT

Provide a structured movement framework from Cagayan / Northern Luzon to Iloilo under degraded conditions.

Execution must be validated against:

* Road conditions
* Port status
* Ferry schedules
* Weather
* Philippine Coast Guard / PNP / AFP / LGU controls

---

## 2. GROUND MOVEMENT COAs (LUZON)

### PRIMARY — Central Luzon Axis → Batangas

Route:
Cagayan → Tuguegarao → Isabela → Nueva Vizcaya → Dalton Pass → Central Luzon → SLEX → Batangas Port

Assessment:
Preferred route if roads and Batangas remain operational.

---

### SECONDARY — Manila Axis

Route:
Cagayan → Central Luzon → NLEX → Manila North Harbor

Assessment:
Higher friction. Use only if Manila is stable.

---

### TERTIARY — Bicol / Matnog–Allen Corridor

Route:
Cagayan → Southern Luzon → Matnog → Allen → Leyte → Panay → Iloilo

Assessment:
Longest but least dependent on western nodes.

---

### LOCAL CONTINGENCY — River Bypass

Use:
Camalaniugan / Aparri crossings

Assessment:
Tactical only. Not strategic.

---

## 3. ROUTE SELECTION LOGIC

Primary:
→ Batangas axis

Secondary:
→ Manila if stable

Tertiary:
→ Matnog–Allen if western routes degrade

Abort:
→ Unknown port status / fuel failure / severe weather

---

## 4. TRANSITION PHASE — GROUND → MARITIME

All southbound movement terminates at:

→ **Batangas Port (Primary Maritime Hub)**
→ **Manila (Fallback Maritime Hub)**

Batangas is the **primary commitment point**.

---

## 5. ANNEX M — MARITIME TRANSITION (BATANGAS → ILOILO)

### 5.1 PURPOSE

Define transition from:

* Ground maneuver (Luzon)
* Maritime movement (Batangas)
* Final movement (Panay / Iloilo)

This phase is the **primary loss-of-maneuver point**.

---

### 5.2 KEY TERRAIN

Decisive:

* Batangas Port

Supporting:

* Manila Port
* Calapan (Mindoro)
* Roxas (Mindoro)
* Caticlan (Panay)
* Iloilo (Fort San Pedro Port)

---

### 5.3 MARITIME COAs

#### COA 1 — DIRECT (PRIMARY)

Batangas → Iloilo
Operator: 2GO Travel

* ~1x weekly
* 17–20 hrs
* Ro-Ro capable

---

#### COA 2 — WESTERN NAUTICAL HIGHWAY (CONTINGENCY)

Batangas → Calapan → Roxas → Caticlan → Iloilo

Operators:

* Starlite Ferries
* Montenegro Shipping Lines

---

#### COA 3 — MANILA DIRECT (EMERGENCY)

Manila → Iloilo
Operator: 2GO Travel

* 18–36 hrs

---

### 5.4 TRANSITION LOGIC

**Phase Line: MANILA**

* Air viable → execute
* Air degraded → continue south

**Phase Line: BATANGAS (CRITICAL)**

* Maritime commitment point
* Post-boarding = no maneuver

---

### 5.5 DECISION TRIGGERS

**D3A — Batangas Commitment Gate**
IF:

* No ferry ≤6 hrs
* No vehicle slot

THEN:
→ Execute COA 2

---

**D3B — Staging Window**
IF:

* Delay >6–8 hrs

THEN:
→ Do NOT wait → divert

---

**D4 — Panay Entry**
IF:

* Delay >4 hrs
* Fatigue / night risk

THEN:
→ Stage before Iloilo

---

### 5.6 HOLD GATE — BATANGAS

Do NOT commit unless:

* Departure confirmed
* Vehicle slot secured
* Boarding window achievable

---

### 5.7 VEHICLE PROTOCOL (Ro-Ro)

Required:

* OR/CR
* ID
* Bill of Lading

Timeline:

* T–4 hrs arrival
* T–1 hr staging

---

### 5.8 TRANSIT CHARACTERISTICS

* Direct: 17–20 hrs
* Modular: 16–24 hrs

---

### 5.9 COST (PLANNING)

Passengers: ₱1,800–₱5,500
Vehicles: ₱8,000–₱22,000

---

### 5.10 OPERATOR CONTACTS

2GO Travel

* +63 2 8528 7000
* travel.2go.com.ph

Starlite Ferries

* starliteferries.com

Montenegro Shipping

* Batangas–Calapan

---

### 5.11 POST-BOARDING CONSTRAINT

Once embarked:

* No reroute
* No timeline control

All decisions must be made **before boarding**

---

### 5.12 COMMANDER’S INTENT

* Minimize idle time at Batangas
* Prefer direct ferry
* Default to modular chain when friction appears
* Preserve mobility until embarkation

---

## 6. DECISION ENGINE (GLOBAL)

D1 — Northern chokepoints
D2 — Manila air decision
D3 — Batangas commitment
D4 — Panay stabilization

---

## 7. EXECUTION SUMMARY

Ground maneuver → Decision → Commitment → Maritime → Stabilization

---
"""
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def inject_annex_actions(section_map, annex_c, condition):
    cond = annex_c["conditions"].get(condition)

    if not cond:
        return

    actions = cond.get("actions", [])

    formatted = "Active Condition: " + condition.upper() + "\n\n"
    formatted += "Execution Guidance:\n"

    for a in actions:
        formatted += f"- {a}\n"

    section_map["Active Condition"] = formatted

def inject_chokepoints(section_map: dict[str, str], annex_c: dict) -> None:
    lines = ["Critical Chokepoints", ""]

    for cp in annex_c.get("chokepoints", []):
        name = cp.get("name", "Unknown")
        risk = cp.get("risk", "")
        impact = cp.get("impact", "")
        fallback = cp.get("fallback_action", "")

        lines.append(f"- {name}")
        if risk:
            lines.append(f"  Risk: {risk}")
        if impact:
            lines.append(f"  Impact: {impact}")
        if fallback:
            lines.append(f"  Fallback: {fallback}")

    section_map["Critical Chokepoints"] = "\n".join(lines)    

def draw_main_page_decor(canvas, doc):
    width, height = doc.pagesize

    canvas.saveState()
   
@dataclass
class IntelSection:
    title: str
    narrative: str

    key_points: List[str] = field(default_factory=list)
    operational_impact: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)

    time_horizon: Optional[str] = None
    bottom_line: Optional[str] = None
    execution: str = ""
    confidence: str = "Medium"
    
    cache_fallback: bool = False
    fallback_reason: Optional[str] = None

@dataclass
class RunStatus:
    ok: bool
    phase: str
    generated_at_utc: str
    report_path: str | None
    message: str
    details: dict


def ensure_dirs() -> None:
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_map_caption_style(styles):
    if "MapCaption" in styles.byName:
        return styles["MapCaption"]

    base = styles["BodyText"]
    caption = ParagraphStyle(
        "MapCaption",
        parent=base,
        fontName=FONT_NAME,
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),
        spaceBefore=4,
        spaceAfter=6,
    )
    styles.add(caption)
    return caption

def add_map_plate(elements, styles, title, image_path, caption, note=""):
    sub_style = styles["SubHeader"] if "SubHeader" in styles.byName else styles["Heading2"]
    caption_style = get_map_caption_style(styles)

    elements.append(PageBreak())
    elements.append(Paragraph(title, sub_style))
    elements.append(Spacer(1, 6))

    if image_path.exists():
        elements.append(Image(str(image_path), width=400, height=520))
    else:
        elements.append(Paragraph(f"Map image missing: {image_path}", styles["BodyText"]))

    elements.append(Paragraph(caption, caption_style))

    if note:
        elements.append(Paragraph(note, caption_style))


def build_reference_maps_section(styles):
    elements = []

    section_style = styles["SectionHeader"] if "SectionHeader" in styles.byName else styles["Heading1"]

    assets_dir = BASE_DIR / "assets"

    northern_map = assets_dir / "northern_exfil_map.jpg"
    southern_map = assets_dir / "southern_exfil_map.jpg"
    manila_map = assets_dir / "manila_area_map.jpg"

    elements.append(PageBreak())
    elements.append(Paragraph("ANNEX Z — REFERENCE MAPS", section_style))

    add_map_plate(
        elements,
        styles,
        "Z1 — NORTHERN LUZON PRIMARY GROUND ROUTE",
        northern_map,
        "Primary southbound ground corridor from Northern Luzon toward Manila and Batangas.",
        "Red route = primary ground movement axis. Key decision flow: D1 northern corridor → D2 Manila → D3 Batangas.",
    )

    add_map_plate(
        elements,
        styles,
        "Z2 — SOUTHERN MARITIME / VISAYAS TRANSITION",
        southern_map,
        "COA 1 = direct Batangas–Iloilo ferry. COA 2 = Western Nautical Highway via Mindoro/Panay. D3 applies before boarding.",
        "",
    )

    add_map_plate(
        elements,
        styles,
        "Z3 — MANILA AREA / BYPASS DECISION MAP",
        manila_map,
        "Close-up reference for Manila-area routing, congestion recognition, and bypass decision support.",
        "D2 = Manila enter/bypass decision. D3 = continue south to Batangas if air movement is degraded.",
    )

    return elements

    return elements

def map_frame(img):
    return Table(
        [[img]],
        colWidths=[420],
        rowHeights=[580],
        style=[
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
        ],
    )

def build_section_collection_note(section: IntelSection) -> str:
    if not section.cache_fallback:
        return "No reportable regional military activity detected."

    reason = (section.fallback_reason or "unknown").replace("_", " ")
    return (
        "Collection note: live source retrieval failed during this run "
        f"({reason}); this section incorporates validated cached reporting."
    )

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def verify_option(name: str) -> tuple[bool, str]:
    """
    Returns:
        ok: whether destination remains qualified today
        summary: one-line verification note for status JSON
    """

def build_crisis_indicator_block(signals: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "callout",
        "block_id": "crisis-indicator",
        "title": "Crisis Indicator Assessment",
        "body": "\n".join([
            "Crisis Indicator Status: DETECTED",
            "",
            f"Trigger: {signals.get('trigger', 'Multi-source anomaly detected')}",
            f"Type: {signals.get('type', 'Composite (weather / aviation / regional)')}",
            f"Severity: {signals.get('severity', 'Moderate')}",
            f"Confidence: {signals.get('confidence', 'Medium')}",
            "",
            "Definition:",
            "- Indicator reflects deviation from baseline conditions requiring increased monitoring or preparatory action.",
            "- Does NOT imply immediate crisis state; used for early warning posture adjustment.",
        ]),
        "tone": "warning",
    }

def build_section_collection_note(section: IntelSection) -> str:
    if not section.cache_fallback:
        return "No reportable regional military activity detected."

    reason = (section.fallback_reason or "unknown").replace("_", " ")
    return (
        "Collection note: live source retrieval failed during this run "
        f"({reason}); this section incorporates validated cached reporting."
    )

def render_intel_section(section: IntelSection) -> str:
    lines: list[str] = []

    note = build_section_collection_note(section)
    if note:
        lines.append(note)
        lines.append("")
        
    narrative = (section.narrative or "").strip()
    if not narrative:
        raise ValueError(f"{section.title} missing narrative")
    lines.append(narrative)
    lines.append("")

    if section.key_points:
        lines.append("Key Points")
        for item in section.key_points:
            lines.append(f"- {item}")
        lines.append("")

    if section.operational_impact:
        lines.append("Operational Impact")
        for item in section.operational_impact:
            lines.append(f"- {item}")
        lines.append("")

    if section.triggers:
        lines.append("Triggers to Watch")
        for item in section.triggers:
            lines.append(f"- {item}")
        lines.append("")

    if not section.time_horizon:
        raise ValueError(f"{section.title} missing time horizon")
    lines.append("Time Horizon")
    lines.append(section.time_horizon.strip())
    lines.append("")

    if not section.bottom_line:
        raise ValueError(f"{section.title} missing bottom line")
    lines.append("Bottom Line")
    lines.append(section.bottom_line.strip())
    lines.append("")

    lines.append(f"Confidence: {section.confidence}")

    def render_intel_section(section: IntelSection) -> str:
        parts = []

        parts.append(str(section.title or "Untitled Section"))

        if section.narrative:
            parts.append("")
            parts.append("Narrative:")
            parts.append(section.narrative)

        if section.key_points:
            parts.append("")
            parts.append("Key Points:")
            for item in section.key_points:
                parts.append(f"- {item}")

        if section.operational_impact:
            parts.append("")
            parts.append("Operational Impact:")
            for item in section.operational_impact:
                parts.append(f"- {item}")

        if section.triggers_to_watch:
            parts.append("")
            parts.append("Triggers to Watch:")
            for item in section.triggers_to_watch:
                parts.append(f"- {item}")

        if section.time_horizon:
            parts.append("")
            parts.append("Time Horizon:")
            parts.append(section.time_horizon)

        if section.bottom_line:
            parts.append("")
            parts.append("Bottom Line:")
            parts.append(section.bottom_line)

        if section.execution:
            parts.append("")
            parts.append("Execution:")
            parts.append(section.execution)

        if section.confidence:
            parts.append("")
            parts.append(f"Confidence: {section.confidence}")
        return "\n".join(str(p) for p in parts if p is not None).strip()


def evaluate_posture(payloads, condition: str) -> dict[str, str]:
    if condition == "red":
        return {"posture": "EXECUTE"}
    if condition == "amber":
        return {"posture": "PREPARE"}
    return {"posture": "NORMAL"}

def md_to_flowables(md_text, styles):
    flowables = []
    for line in md_text.split("\n"):
        line = line.strip()

        if not line:
            continue

        # Headers
        if line.startswith("## "):
            flowables.append(Paragraph(line[3:], styles["SectionHeader"]))
        elif line.startswith("### "):
            flowables.append(Paragraph(line[4:], styles["Heading2"]))

        # Bold (basic)
        elif line.startswith("**") and line.endswith("**"):
            flowables.append(Paragraph(f"<b>{line[2:-2]}</b>", styles["BodyText"]))

        # Divider
        elif line == "---":
            flowables.append(Spacer(1, 10))

        # Bullets
        elif line.startswith("* "):
            flowables.append(Paragraph(f"• {line[2:]}", styles["BodyText"]))

        else:
            flowables.append(Paragraph(line, styles["BodyText"]))

    return flowables


def build_regional_maritime_section(signals) -> str:
    return (
        "Regional Maritime Security:\n"
        "- No additional validated maritime escalation summary was generated by helper logic at runtime.\n"
        "- Review Strategic Situation and Priority Intelligence for current regional indicators."
    )

def build_immunization_section() -> dict[str, Any]:
    body = "\n".join([
        "Immunization Recommendations (CDC Baseline):",
        "",
        "- Routine vaccines (MMR, Tdap, influenza) should be current",
        "- Hepatitis A: Recommended for all travelers",
        "- Hepatitis B: Recommended for extended stay or medical exposure risk",
        "- Typhoid: Recommended for food/water exposure risk",
        "- Tetanus: Ensure booster within 10 years",
        "- Rabies: Consider only for high-risk rural or animal exposure scenarios",
        "",
        "Operational Note:",
        "- No immediate travel restriction if routine vaccinations are current",
        "- Risk is cumulative and environmental, not a hard stop condition",
    ])

    return {
        "kind": "callout",
        "block_id": "immunization-recommendations",
        "title": "Immunization Recommendations",
        "body": body,
        "tone": "standard",
    }


def build_internal_security_section(signals) -> str:
    return (
        "Internal Security / Terrorism Assessment:\n"
        "- No additional internal security synthesis was generated by helper logic at runtime.\n"
        "- Review embassy advisories and Priority Intelligence for current threat indicators."
    )

def build_pace_section() -> dict[str, Any]:
    return {
        "kind": "table",
        "block_id": "pace-plan",
        "title": "Communications PACE Plan",
        "headers": ["Function", "Primary", "Alternate", "Contingency", "Emergency"],
        "rows": [
            ["Voice Comms", "U.S. roaming plan", "WhatsApp call", "Local SIM call", "Burner phone"],
            ["Messaging", "SMS", "Messenger", "WhatsApp/Telegram", "Pre-set emergency phrase"],
            ["Navigation", "Google Maps (online)", "Offline maps", "Paper map", "Local guide"],
            ["Coordination", "Direct contact", "Family relay", "Pre-arranged check-in", "Embassy contact"],
        ],
        "repeat_header": True,
    }

def build_cover_page(now_utc, signals, used_cache=False) -> str:
    dtg = now_utc.strftime("%d%H%MZ %b %y").upper()
    generated = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    return "\n".join([
        "UNCLASSIFIED // OPEN SOURCE",
        "",
        "PHILIPPINES MISSION",
        "INTELLIGENCE BRIEFING PACKET",
        "",
        "Philippines Mission Intel Status Report",
        "",
        "AO: Philippines / Manila / NAIA / Regional Contingency Routes",
        f"DTG: {dtg}",
        "Prepared By: Automated Mission-Intelligence Pipeline",
        f"Generated: {generated}",
        "",
        "UNCLASSIFIED // OPEN SOURCE",
    ])

def build_priority_ranking_summary(section_map: dict[str, str]) -> str:
    content = str(section_map.get("Regional Military Activity / Movement", "") or "")

    if not content.strip():
        return (
            "Priority Ranking:\n"
            "1. Regional Military Activity: LOW — no reportable military movement detected.\n"
            "2. Aviation / Airport Operations: MONITOR — verify before movement.\n"
            "3. Weather / Environmental Risk: MONITOR — check heat, rain, and flooding conditions."
        )

    high_count = content.count("[HIGH]")
    moderate_count = content.count("[MODERATE]")
    low_count = content.count("[LOW]")

    if high_count:
        mil_level = "HIGH"
    elif moderate_count:
        mil_level = "MODERATE"
    elif low_count:
        mil_level = "LOW"
    else:
        mil_level = "MONITOR"

    AO_KEYWORDS = [
        "philippine",
        "west philippine sea",
        "south china sea",
        "wps",
        "luzon",
        "batanes",
        "palawan",
        "scarborough",
        "second thomas",
        "china coast guard",
        "pla",
        "chinese",
    ]

    top_items = []

    for line in content.splitlines():
        line = line.strip()
        line_l = line.lower()

        if (
            (line.startswith("- [HIGH]") or line.startswith("- [MODERATE]"))
            and any(k in line_l for k in AO_KEYWORDS)
        ):
            top_items.append(line.replace("- ", "", 1))

        if len(top_items) >= 3:
            break

    if not top_items:
        top_items = [f"Regional Military Activity: {mil_level} — no high-priority items extracted."]

    lines = [
        "Priority Ranking:",
        trend = "INCREASING" if moderate_count + high_count > 10 else "STABLE"

        f"1. Regional Military Activity: {mil_level} ({trend}) — ..."
    ]

    for idx, item in enumerate(top_items[:3], start=2):
        lines.append(f"{idx}. {item}")

    lines.append("Assessment: Monitor for embassy alert changes, airspace restrictions, airport disruption, maritime confrontation, or official escalation language.")

    return "\n".join(lines)

def build_header(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(40, 800, "PHILIPPINES MISSION INTEL BRIEF")
    canvas.drawRightString(550, 800, "UNCLASSIFIED // OPEN SOURCE")
    canvas.restoreState()

def build_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(550, 20, f"Page {doc.page}")
    canvas.restoreState()

def build_cover_story(cover_text: str, styles) -> list:
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        spaceAfter=18,
        alignment=TA_CENTER,
        textColor=black,
    )

    meta_label_style = ParagraphStyle(
        "MetaLabel",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=black,
    )

    meta_value_style = ParagraphStyle(
        "MetaValue",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        textColor=black,
    )

    section_style = ParagraphStyle(
        "CoverSection",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        spaceBefore=6,
        spaceAfter=6,
        textColor=black,
    )

    bullet_style = ParagraphStyle(
        "CoverBullet",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        leftIndent=8,
        bulletIndent=0,
        spaceAfter=4,
        textColor=black,
    )

    lines = [line.strip() for line in cover_text.splitlines()]

    title = ""
    metadata: list[tuple[str, str]] = []
    key_judgments: list[str] = []
    source_basis: list[str] = []
    prepared_by: list[str] = []

    current_section = None

    for line in lines:
        if not line:
            continue

        if not title:
            title = line
            continue

        if line in {"Key Judgments", "Source Basis", "Prepared By"}:
            current_section = line
            continue

        if current_section == "Key Judgments":
            key_judgments.append(line)
        elif current_section == "Source Basis":
            source_basis.append(line)
        elif current_section == "Prepared By":
            prepared_by.append(line)
        elif ":" in line:
            label, value = line.split(":", 1)
            metadata.append((label.strip() + ":", value.strip()))

    def boxed_section(title_text: str, items: list[str]) -> Table:
        rows = [[Paragraph(title_text, section_style)]]
        for item in items:
            bullet_text = item[2:].strip() if item.startswith("- ") else item
            rows.append([Paragraph(f"• {bullet_text}", bullet_style)])

        table = Table(rows, colWidths=[470])
        table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, black),
            ("BACKGROUND", (0, 0), (-1, 0), red),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return table

    story = []

    story.append(Spacer(1, 72))
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))

    if metadata:
        meta_rows = []
        for label, value in metadata:
            meta_rows.append([
                Paragraph(label, meta_label_style),
                Paragraph(value, meta_value_style),
            ])

        meta_table = Table(meta_rows, colWidths=[140, 330])
        meta_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BOX", (0, 0), (-1, -1), 1, black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, black),
            ("BACKGROUND", (0, 0), (0, -1), red),
            ("TEXTCOLOR", (0, 0), (0, -1), white),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 18))

    if key_judgments:
        story.append(boxed_section("Key Judgments", key_judgments))
        story.append(Spacer(1, 14))

    if source_basis:
        story.append(boxed_section("Source Basis", source_basis))
        story.append(Spacer(1, 14))

    if prepared_by:
        story.append(boxed_section("Prepared By", prepared_by))
        story.append(Spacer(1, 14))

    return story
    story = []

def build_toc_section(styles):
    toc_story = []

    heading_style = styles["SectionHeader"] if "SectionHeader" in styles.byName else styles["Heading1"]
    body_style = styles["BodyText"]

    toc_items = [
        "1. Commander’s Summary",
        "2. Active Condition",
        "3. Strategic Situation",
        "4. Priority Intelligence",
        "5. Embassy / State / Airport / Weather",
        "6. Escalation Thresholds",
        "7. Contingency Evacuation",
        "8. Southern Ground / Maritime Mobility Blueprint",
        "9. Annex M — Maritime Transition",
        "10. Annex Z — Reference Maps",
    ]

    toc_story.append(Paragraph("CONTENTS", heading_style))
    toc_story.append(Spacer(1, 8))

    for item in toc_items:
        toc_story.append(Paragraph(item, body_style))

    toc_story.append(PageBreak())
    return toc_story

def enrich_section(content: str, signals, section_name: str) -> str:
    return content

def normalize(s: str) -> str:
    return "".join(s.lower().split())


def build_assumptions_section() -> str:
    return (
        "Assumptions:\n"
        "- Source timestamps are accurate as published by originating providers.\n"
        "- No abrupt nationwide access restriction, airport closure, or embassy posture change occurred after collection cutoff.\n"
        "- Report reflects currently retrievable open-source and adapter-fed inputs at generation time."
    )

def cache_age_hours(source_timestamp_utc: datetime, now_utc: datetime) -> float:
    return (now_utc - source_timestamp_utc).total_seconds() / 3600.0


def build_base_section_map(payloads: list[SourcePayload]) -> dict[str, str]:
    section_map: dict[str, str] = {}

    for p in payloads:
        name = p.section_name.strip()

        # Compatibility alias: adapter still emits legacy name
        if name == "Immunization recommendations":
            name = "Health / Environmental Risk"

        section_map[name] = p.content
 
    for section in REQUIRED_SECTIONS:
        if section not in section_map or not str(section_map.get(section, "")).strip():
            section_map[section] = REQUIRED_SECTION_FALLBACKS[section]

    # --- Priority Intelligence (merged sources) ---
    priority_payloads = [
        p for p in payloads
        if getattr(p, "category", "") == SECTION_PRIORITY_INTELLIGENCE \
            and p.section_name != "Regional Military Activity / Movement"
    ]

    priority_parts = []

    for p in priority_payloads:
        content = str(getattr(p, "content", "") or "").strip()
        if content:
            priority_parts.append(content)

    if priority_parts:
        section_map[SECTION_PRIORITY_INTELLIGENCE] = (
            f"{SECTION_PRIORITY_INTELLIGENCE}\n\n" + "\n\n".join(priority_parts)
        )
    else:
        section_map[SECTION_PRIORITY_INTELLIGENCE] = REQUIRED_SECTION_FALLBACKS[
        SECTION_PRIORITY_INTELLIGENCE
        ]            

    return section_map

def md_line_to_flowables(line, styles, body_style, heading_style):
    out = []
    raw = str(line).strip()

    if not raw:
        return out

    if raw == "---":
        out.append(Spacer(1, 8))
        return out

    if raw.startswith("## "):
        out.append(Paragraph(raw[3:].strip(), heading_style))
        return out

    if raw.startswith("### "):
        out.append(Paragraph(raw[4:].strip(), styles["Heading2"]))
        return out

    if raw.startswith("#### "):
        out.append(Paragraph(raw[5:].strip(), styles["Heading3"]))
        return out

    if raw.startswith("* "):
        out.append(Paragraph("• " + raw[2:].strip(), body_style))
        return out

    raw = raw.replace("**", "")
    raw = raw.replace("₱", "PHP ")

    out.append(Paragraph(raw, body_style))
    return out

def build_protest_intel_section() -> dict[str, Any]:
    return {
        "kind": "table",
        "block_id": "civil-unrest-intel",
        "title": "Civil Unrest — Sources and Likely Locations",
        "headers": ["Category", "Typical Organizers", "Likely Locations", "Trigger Pattern", "Operational Impact"],
        "rows": [
            [
                "Labor / Economic",
                "Labor unions, transport groups",
                "EDSA corridors, government labor offices",
                "Wage disputes, fuel price increases",
                "Traffic disruption, road congestion"
            ],
            [
                "Political / Opposition",
                "Student groups, activist coalitions",
                "Universities, public plazas, government buildings",
                "Policy decisions, corruption allegations",
                "Localized crowding, rerouting required"
            ],
            [
                "Foreign Policy / U.S.",
                "Nationalist groups, left-leaning orgs",
                "U.S. Embassy vicinity, major intersections",
                "Joint exercises, defense agreements",
                "Short-duration protests, increased security presence"
            ],
            [
                "China / Maritime",
                "Fisher groups, nationalist orgs",
                "Government zones, symbolic locations",
                "South China Sea incidents",
                "Low frequency, higher volatility if triggered"
            ],
        ],
        "repeat_header": True,
    }

def build_protest_locations_block() -> dict[str, Any]:
    body = "\n".join([
        "High-Probability Demonstration Areas:",
        "",
        "- U.S. Embassy (Roxas Blvd, Manila)",
        "- Mendiola / Malacañang Palace approach",
        "- EDSA major intersections (traffic-sensitive)",
        "- University Belt (UST, UP Manila)",
        "- Luneta / Rizal Park",
        "",
        "Operational Note:",
        "- These areas are predictable and avoidable with route discipline",
        "- Protests are typically static and localized",
    ])

    return {
        "kind": "callout",
        "block_id": "protest-locations",
        "title": "Likely Protest Locations",
        "body": body,
        "tone": "standard",
    }

def build_health_environment_section(data) -> str:
    if not data:
        return (
            f"{SECTION_HEALTH_ENVIRONMENT}\n\n"
            "Baseline health risks present (heat, dehydration, food/water exposure). No elevated conditions detected."
        )

    return f"{SECTION_HEALTH_ENVIRONMENT}\n\n{data}"

def build_state_department_section(data) -> str:
    if not data:
        return (
            f"{SECTION_STATE}\n\n"
            "No change in U.S. State Department advisory posture at runtime."
        )

    return f"{SECTION_STATE}\n\n{data}"

def build_naia_section(data) -> str:
    if not data:
        return (
            f"{SECTION_NAIA}\n\n"
            "NAIA remains operational unless confirmed otherwise. Public reporting should not be treated as a sole-source indicator. "
            "Cross-check airline status, airport displays, and flight tracking before movement."
        )

    return f"{SECTION_NAIA}\n\n{data}"

def build_southern_mobility_section() -> str:
    return SOUTHERN_MOBILITY_BLUEPRINT    

def build_protest_timing_block() -> dict[str, Any]:
    body = "\n".join([
        "Timing Patterns:",
        "",
        "- Weekdays (0800–1700): Organized labor / political protests",
        "- Late afternoon: Increased visibility demonstrations",
        "- Event-driven: Immediate protest within 24–48h of trigger event",
        "",
        "Operational Implication:",
        "- Avoid government corridors during business hours",
        "- Reconfirm routes same-day before movement",
    ])

    return {
        "kind": "callout",
        "block_id": "protest-timing",
        "title": "Demonstration Timing Pattern",
        "body": body,
    }

def build_escalation_thresholds_section() -> str:
    rows = [
        ("Flight disruption", "≥3 cancellations within 6 hours", "Initiate alternate routing COA"),
        ("Airport delay", "Average delay >90 minutes", "Add +2–4 hr buffer to movement"),
        ("Embassy posture", "Alert level increase", "Immediate movement reassessment within 2 hours"),
        ("Regional security", "Significant PLA activity surge or confrontation", "Prepare evacuation routing"),
        ("Weather disruption", "Sustained heavy rainfall / storm advisory", "Adjust ground movement timing"),
    ]

    parts = [
        SECTION_ESCALATION,
        "",
        "Trigger | Threshold | Action",
        "--- | --- | ---",
    ]

    for trigger, threshold, action in rows:
        parts.append(f"{trigger} | {threshold} | {action}")

    return "\n".join(parts)


def dedupe_heading(section_name, content):
    if content is None:
        return "No reportable regional military activity detected."

    content = str(content)
    lines = [line.rstrip() for line in content.strip().splitlines()]

    if not lines:
        return "No reportable regional military activity detected."

    if lines[0].strip() == section_name:
        lines = lines[1:]

    return "\n".join([section_name, *lines]).strip()


REPORT_SECTION_ORDER = [
    SECTION_COMMANDERS_SUMMARY,
    "Active Condition",
    SECTION_STRATEGIC_SITUATION,
    SECTION_PRIORITY_INTELLIGENCE,
    SECTION_REGIONAL_MIL_ACTIVITY,
    "Regional Security / External Threat Environment",
    "Internal Security / Terrorism Assessment",
    SECTION_EMBASSY,
    SECTION_STATE,
    SECTION_WEATHER,
    SECTION_HEALTH_ENVIRONMENT,
    SECTION_GEOLOGICAL,
    SECTION_NAIA,
    SECTION_DECISION,
    SECTION_ESCALATION,
    SECTION_CONTINGENCY,
    SECTION_SOUTHERN_MOBILITY,
    SECTION_CHANGES,
    SECTION_QC,
]

REQUIRED_SECTIONS = [
    SECTION_STRATEGIC_SITUATION,
    SECTION_PRIORITY_INTELLIGENCE,
    SECTION_EMBASSY,
    SECTION_STATE,
    SECTION_HEALTH_ENVIRONMENT,
    SECTION_WEATHER,
]

SECTION_PAGE_BREAKS = {
    "cover_page",
    "commander_summary",
    "threat_assessment",
    "chokepoints",
    "aviation",
    "weather",
    "health",
    "civil_unrest",
    "pace",
    "evacuation",
}

def enforce_page_break(elements, section_id):
    if section_id in SECTION_PAGE_BREAKS:
        elements.append(PageBreak())

    for key, value in section_map.items():
        if value is None:
            section_map[key] = f"{key}\n\nNo data available at runtime."       

def build_report_text(section_map: dict, crisis_banner: str | None = None) -> str:
    parts = []

    if crisis_banner:
        parts.append(str(crisis_banner).strip())

    for section_name in REPORT_SECTION_ORDER:
        if section_name not in section_map:
            continue

        raw_content = section_map.get(section_name)
        if raw_content is None:
            continue

        content = dedupe_heading(section_name, str(raw_content)) or ""

        if content.strip():
            parts.append(content.strip())

        body = "\n\n".join(parts).strip()

    title = "PHILIPPINES MISSION INTEL STATUS REPORT"
    generated_label = (
        "Generated by 0001Z daily\n"
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

    if title not in body:
        body = f"{title}\n{generated_label}\n\n{body}"
    elif "Generated:" not in body:
        body = body.replace(title, f"{title}\n{generated_label}", 1)

    return body

def build_collection_note(payload: SourcePayload) -> str:
    if not payload.raw_metadata.get("cache_fallback"):
        return "No reportable regional military activity detected."

    reason = str(payload.raw_metadata.get("fallback_reason", "unknown")).replace("_", " ")

    return (
        "Collection note: live source retrieval failed during this run "
        f"({reason}); section incorporates validated cached reporting."
    )

def write_status(status: RunStatus) -> None:
    STATUS_FILE.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")


def build_alerts(payloads: list[SourcePayload], used_cache: bool, now_utc: datetime) -> list[str]:
    alerts: list[str] = []

    if used_cache:
        alerts.append("CACHE_FALLBACK_USED")

    for p in payloads:
        provider = str(p.raw_metadata.get("provider", "unknown")).upper().replace(" ", "_")

        if p.raw_metadata.get("cache_fallback"):
            reason = str(p.raw_metadata.get("fallback_reason", "unknown")).upper().replace(" ", "_")
            alerts.append(f"CACHE_FALLBACK_{provider}_{reason}")

            age_hours = cache_age_hours(p.source_timestamp_utc, now_utc)
            if age_hours >= 24:
                alerts.append("STALE_CACHE_WARNING")

        if p.raw_metadata.get("live_mode"):
            if "TRAVEL.STATE.GOV" in provider:
                alerts.append("STATE_DEPT_LIVE")
            elif "OPEN-METEO" in provider:
                alerts.append("WEATHER_LIVE")
            elif "USEMBASSY" in provider or "EMBASSY" in provider:
                alerts.append("EMBASSY_LIVE")

    return list(dict.fromkeys(alerts))

def draw_main_page_decor(canvas, doc):
    width, height = doc.pagesize


    # Page border
    canvas.setStrokeColorRGB(1, 0, 0)
    canvas.setLineWidth(1.5)
    canvas.rect(
        PDF_BORDER_INSET,
        PDF_BORDER_INSET,
        width - (2 * PDF_BORDER_INSET),
        height - (2 * PDF_BORDER_INSET),
        stroke=1,
        fill=0,
    )

    # Header band
    band_y = height - PDF_BORDER_INSET - PDF_HEADER_BAND_HEIGHT
    canvas.setFillColorRGB(1, 0, 0)
    canvas.rect(
        PDF_BORDER_INSET,
        band_y,
        width - (2 * PDF_BORDER_INSET),
        PDF_HEADER_BAND_HEIGHT,
        stroke=0,
        fill=1,
    )

    # Header text
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(
        PDF_BORDER_INSET + 8,
        band_y + 6,
        PDF_HEADER_TITLE,
    )

    # Footer line
    footer_y = PDF_FOOTER_Y + 10
    canvas.setStrokeColor(black)
    canvas.setLineWidth(0.5)
    canvas.line(
        PDF_BORDER_INSET,
        footer_y,
        width - PDF_BORDER_INSET,
        footer_y,
    )

    # Footer metadata
    canvas.setFillColor(black)
    canvas.setFont("Helvetica", 8)

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    canvas.drawString(PDF_BORDER_INSET, PDF_FOOTER_Y, generated_text)

    class_width = canvas.stringWidth(PDF_CLASSIFICATION, "Helvetica-Bold", 8)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString((width - class_width) / 2, PDF_FOOTER_Y, PDF_CLASSIFICATION)

    page_label = f"Page {canvas.getPageNumber()}"
    page_width = canvas.stringWidth(page_label, "Helvetica", 8)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(width - PDF_BORDER_INSET - page_width, PDF_FOOTER_Y, page_label)


    SEAL_PATH = Path("mission_analysis_seal.svg")

def draw_running_header(c, doc):
    width, height = doc.pagesize

    c.saveState()

    # LEFT: report name
    c.setFont("Helvetica", 8)
    c.drawString(
        54,
        height - 28,
        "PHILIPPINES MISSION INTEL STATUS REPORT"
    )

    # RIGHT: DTG + classification
    c.drawRightString(
        width - 54,
        height - 28,
        "1609Z | UNCLASSIFIED"
    )

    # Divider line
    c.setLineWidth(0.5)
    c.line(54, height - 32, width - 54, height - 32)

    c.restoreState()
    seal_size = 36
    c.setFont("Helvetica-Bold", 12)
    c.setFont("Helvetica", 9)
    c.setFont("Helvetica", 8)
    text_x = left_margin + seal_size + 14

    drawing = svg2rlg(str(SEAL_PATH))
    if drawing is None:
        raise FileNotFoundError(f"Unable to load SVG seal: {SEAL_PATH}")

    scale = min(seal_size / drawing.width, seal_size / drawing.height)

    c.saveState()
    c.translate(left_margin, top_y - seal_size + 2)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()

    c.setFont("Helvetica-Bold", 14)
    c.drawString(text_x, top_y, "PHILIPPINES MISSION INTEL STATUS REPORT")

    c.setFont("Helvetica", 9.5)
    c.drawString(text_x, top_y - 13, "Regional Intelligence Summary | Mission Analysis Cell")

    c.setFont("Helvetica", 8.5)
    c.drawString(text_x, top_y - 25, "DTG: 0001Z (Daily) | UNCLASSIFIED")

    c.setLineWidth(0.6)
    c.line(left_margin, top_y - 34, page_width - left_margin, top_y - 34)




    def draw_cover_page(canvas, doc):
        width, height = doc.pagesize
        canvas.saveState()

        # Page border
        canvas.setStrokeColorRGB(1, 0, 0)
        canvas.setLineWidth(1.5)
        canvas.rect(
            PDF_BORDER_INSET,
            PDF_BORDER_INSET,
            width - (2 * PDF_BORDER_INSET),
            height - (2 * PDF_BORDER_INSET),
            stroke=1,
            fill=0,
        )

        # Header band
        band_y = height - PDF_BORDER_INSET - PDF_HEADER_BAND_HEIGHT
        canvas.setFillColorRGB(1, 0, 0)
        canvas.rect(
            PDF_BORDER_INSET,
            band_y,
            width - (2 * PDF_BORDER_INSET),
            PDF_HEADER_BAND_HEIGHT,
            stroke=0,
            fill=1,
        )

        # Header text
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(
            PDF_BORDER_INSET + 8,
            band_y + 6,
            PDF_HEADER_TITLE,
        )

        # Footer line
        footer_y = PDF_FOOTER_Y + 10
        canvas.setStrokeColor(black)
        canvas.setLineWidth(0.5)
        canvas.line(
            PDF_BORDER_INSET,
            footer_y,
            width - PDF_BORDER_INSET,
            footer_y,
        )

        # Footer metadata
        canvas.setFillColor(black)
        canvas.setFont("Helvetica", 8)

        generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        canvas.drawString(PDF_BORDER_INSET, PDF_FOOTER_Y, generated_text)

        class_width = canvas.stringWidth(PDF_CLASSIFICATION, "Helvetica-Bold", 8)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString((width - class_width) / 2, PDF_FOOTER_Y, PDF_CLASSIFICATION)

        page_label = f"Page {canvas.getPageNumber()}"
        page_width = canvas.stringWidth(page_label, "Helvetica", 8)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(width - PDF_BORDER_INSET - page_width, PDF_FOOTER_Y, page_label)

        canvas.restoreState()

    first_page_callback = draw_cover_page if cover_text else draw_main_page_decor

    print("DEBUG: STARTING PDF BUILD")
    doc.build(...)
    print("DEBUG: PDF BUILD COMPLETE")

def draw_running_header(canvas, doc):
    width, height = doc.pagesize

    canvas.saveState()

    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        54,
        height - 30,
        "PHILIPPINES MISSION INTEL STATUS REPORT | 0001Z | UNCLASSIFIED"
    )

    canvas.setLineWidth(0.5)
    canvas.line(54, height - 34, width - 54, height - 34)

    canvas.restoreState()
 

def build_decision_guidance(posture: str) -> str:
    return (
        f"- Current posture: {posture}\n"
        "- Maintain routine monitoring of embassy, aviation, weather, and transport reporting.\n"
        "- Escalate immediately if embassy posture changes, airport disruption expands, or regional threat indicators intensify.\n"
        "- Validate onward movement, alternate lodging, and contingency routing before local conditions degrade."
    )

def build_callout(text, tone="standard"):
    color_map = {
        "standard": colors.whitesmoke,
        "warning": colors.lightyellow,
        "critical": colors.pink,
    }

    return Table(
        [[Paragraph(text, styles["BodyTextTight"])]],
        style=[
            ("BACKGROUND", (0,0), (-1,-1), color_map[tone]),
            ("BOX", (0,0), (-1,-1), 0.5, colors.black),
            ("PADDING", (0,0), (-1,-1), 8),
        ]
    )

def normalize_for_diff(text: str) -> str:
    return "\n".join(
        line.rstrip()
        for line in str(text or "").splitlines()
    ).strip()

def render_pdf(report_text: str, output_path: Path, cover_text: str | None = None) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("DEBUG render_pdf output_path =", output_path)
    print("DEBUG render_pdf absolute =", output_path.resolve())

    styles = getSampleStyleSheet()

    styles["BodyText"].fontName = FONT_NAME
    styles["Heading1"].fontName = FONT_NAME
    styles["Heading2"].fontName = FONT_NAME

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=13,
        leading=14,
        spaceAfter=8,
        spaceBefore=10,
        fontName="Helvetica-Bold",
    ))

    styles.add(ParagraphStyle(
        name="BodyTextTight",
        fontSize=9,
        leading=11,
    ))

    heading_style = ParagraphStyle(
        "MissionHeading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=4,
        textColor=black,
    )

    body_style = ParagraphStyle(
        "MissionBody",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        spaceAfter=2,
        textColor=black,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=8.5,
        alignment=1,
        textColor=black,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=7.25,
        leading=8.5,
        textColor=black,
    )

    callout_title_style = ParagraphStyle(
        "CalloutTitle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=9,
        alignment=1,
        textColor=black,
    )

    callout_body_style = ParagraphStyle(
        "CalloutBody",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10,
        textColor=black,
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
    )

    map_frame = Frame(
        50, 50,
        700, 500,
        id="map_frame"
    )

    map_template = PageTemplate(
        id="MapPage",
        frames=[map_frame],
    )

    story = []

    if cover_text:
        for line in cover_text.splitlines():
            if line.strip():
                story.append(Paragraph(line.strip(), styles["BodyText"]))
            else:
                story.append(Spacer(1, 6))
        story.append(PageBreak())

    story.extend(build_toc_section(styles))

    def para(value, style):
        return Paragraph(str(value or "").replace("\n", "<br/>"), style)
    
    def try_add_pipe_table(body_lines):
        table_lines = [line.strip() for line in body_lines if "|" in line]

        if len(table_lines) < 2:
            return False

        rows = []
        for line in table_lines:
            if "---" in line:
                continue
            rows.append([cell.strip() for cell in line.split("|")])

        if len(rows) < 2:
            return False

        headers = rows[0]
        body_rows = rows[1:]

        add_table(
            title=None,
            headers=headers,
            rows=body_rows,
            col_widths=[doc.width / len(headers)] * len(headers),
        )
        return True

    def add_section(title):
        story.append(Spacer(1, 8))
        story.append(Paragraph(str(title).upper(), heading_style))
        story.append(Spacer(1, 4))

    def add_callout(title, body):
        data = [
            [para(str(title).upper(), callout_title_style)],
            [para(body, callout_body_style)],
        ]

        table = Table(data, colWidths=[doc.width])
        table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.0, black),
            ("BACKGROUND", (0, 0), (-1, 0), lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(table)
        story.append(Spacer(1, 8))

    def add_table(title, headers, rows, col_widths=None):
        if title:
            story.append(Paragraph(str(title), heading_style))

        if not col_widths:
            col_widths = [doc.width / max(len(headers), 1)] * len(headers)

        data = [[para(h, table_header_style) for h in headers]]

        for row in rows:
            data.append([para(cell, table_cell_style) for cell in row])

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, black),
            ("BACKGROUND", (0, 0), (-1, 0), lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, colors.whitesmoke]),
        ]))

        story.append(table)
        story.append(Spacer(1, 8))    

        for i, line in enumerate(cover_text.splitlines()):
            if not line.strip():
                story.append(Spacer(1, 8))
                continue

            if i == 0:
                story.append(Paragraph(line, heading_style))
            else:
                p = Paragraph(line, body_style)
                story.append(p)

        generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        story.append(PageBreak())

    heading_names = set(REPORT_SECTION_ORDER) | {"CRISIS INDICATOR"}
    lines = report_text.splitlines()

    parsed_sections = []
    current_heading = None
    current_body = []

    for raw_line in lines:
        line = raw_line.strip()

        if line in heading_names:
            if current_heading is not None:
                parsed_sections.append((current_heading, current_body))

            current_heading = line
            current_body = []
            continue

        if current_heading is not None:
            current_body.append(raw_line)

    if current_heading is not None:
        parsed_sections.append((current_heading, current_body))

    for idx, (heading, body_lines) in enumerate(parsed_sections):
        compact_sections = {
            "Regional Security / External Threat Environment",
            "Internal Security / Terrorism Assessment",
            SECTION_HEALTH_ENVIRONMENT,
            SECTION_GEOLOGICAL,
            SECTION_NAIA,
            SECTION_DECISION,
            SECTION_CHANGES,
            SECTION_QC,
}

        if idx > 0 and heading not in compact_sections:
            story.append(PageBreak())
        else:
            story.append(Spacer(1, 10))

        add_section(heading)

        if heading == "Critical Chokepoints":
            rows = []
            current = {}

            for line in body_lines:
                line = line.strip()
                if line.startswith("- "):
                    if current:
                        rows.append([
                            current.get("name", ""),
                            current.get("risk", ""),
                            current.get("impact", ""),
                            current.get("fallback", ""),
                        ])
                    current = {"name": line[2:].strip()}
                elif line.startswith("Risk:"):
                    current["risk"] = line.replace("Risk:", "", 1).strip()
                elif line.startswith("Impact:"):
                    current["impact"] = line.replace("Impact:", "", 1).strip()
                elif line.startswith("Fallback:"):
                    current["fallback"] = line.replace("Fallback:", "", 1).strip()

            if current:
                rows.append([
                    current.get("name", ""),
                    current.get("risk", ""),
                    current.get("impact", ""),
                    current.get("fallback", ""),
                ])

            if rows:
                add_table(
                    title=None,
                    headers=["Chokepoint", "Risk", "Impact", "Fallback"],
                    rows=rows,
                    col_widths=[
                        doc.width * 0.18,
                        doc.width * 0.30,
                        doc.width * 0.10,
                        doc.width * 0.42,
                    ],
                )
                continue   

        if heading == SECTION_COMMANDERS_SUMMARY:
            add_callout("COMMANDER SNAPSHOT", "\n".join(body_lines).strip())
            continue

        if heading == SECTION_WEATHER:
            weather_rows = []
            for line in body_lines:
                line = line.strip()
                if "|" in line and line[:4].isdigit():
                    parts = [part.strip() for part in line.split("|")]

                    cleaned = []
                    for part in parts:
                        part = part.replace("High ", "")
                        part = part.replace("Low ", "")
                        part = part.replace("Wind ", "")
                        cleaned.append(part)

                    weather_rows.append(cleaned)

            if weather_rows:
                add_table(
                    title=None,
                    headers=["Date", "High", "Low", "Wind", "Condition"],
                    rows=weather_rows,
                    col_widths=[
                        doc.width * 0.18,
                        doc.width * 0.15,
                        doc.width * 0.15,
                        doc.width * 0.22,
                        doc.width * 0.30,
                    ],
                )
                continue
            
        if heading == SECTION_ESCALATION:
            rows = []
            for line in body_lines:
                line = line.strip()
                if "|" not in line or "---" in line:
                    continue
                rows.append([part.strip() for part in line.split("|")])

            if len(rows) >= 2:
                add_table(
                    title=None,
                    headers=rows[0],
                    rows=rows[1:],
                    col_widths=[
                        doc.width * 0.24,
                        doc.width * 0.36,
                        doc.width * 0.40,
                    ],
                )
                continue    

        if try_add_pipe_table(body_lines):
            continue

        body_text = "\n".join(body_lines).strip()

        if not body_text:
            story.append(Paragraph("No reportable content.", body_style))
            continue

        paragraphs = body_text.split("\n\n")

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            for line in paragraph.splitlines():
                line = line.strip()
                if not line:
                    continue

                story.extend(md_line_to_flowables(line, styles, body_style, heading_style))
                story.append(Spacer(1, 4))

            story.append(Spacer(1, 6))

    def draw_cover_page(canvas, doc):
        width, height = doc.pagesize
        canvas.saveState()

        canvas.setStrokeColorRGB(1, 0, 0)
        canvas.setLineWidth(1.5)
        canvas.rect(
            PDF_BORDER_INSET,
            PDF_BORDER_INSET,
            width - (2 * PDF_BORDER_INSET),
            height - (2 * PDF_BORDER_INSET),
            stroke=1,
            fill=0,
        )

        band_y = height - PDF_BORDER_INSET - PDF_HEADER_BAND_HEIGHT
        canvas.setFillColorRGB(1, 0, 0)
        canvas.rect(
            PDF_BORDER_INSET,
            band_y,
            width - (2 * PDF_BORDER_INSET),
            PDF_HEADER_BAND_HEIGHT,
            stroke=0,
            fill=1,
        )

        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(PDF_BORDER_INSET + 8, band_y + 6, PDF_HEADER_TITLE)


        footer_y = PDF_FOOTER_Y + 10
        canvas.setStrokeColor(black)
        canvas.setLineWidth(0.5)
        canvas.line(PDF_BORDER_INSET, footer_y, width - PDF_BORDER_INSET, footer_y)

        canvas.setFillColor(black)
        canvas.setFont("Helvetica", 8)
        generated_text = f"Generated: {utc_now_iso().replace('+00:00', 'Z')}"
        canvas.drawString(PDF_BORDER_INSET, PDF_FOOTER_Y, generated_text)

        class_width = canvas.stringWidth(PDF_CLASSIFICATION, "Helvetica-Bold", 8)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString((width - class_width) / 2, PDF_FOOTER_Y, PDF_CLASSIFICATION)

        page_label = f"Page {canvas.getPageNumber()}"
        page_width = canvas.stringWidth(page_label, "Helvetica", 8)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(width - PDF_BORDER_INSET - page_width, PDF_FOOTER_Y, page_label)

        canvas.restoreState()

    print("DEBUG story length =", len(story))
    print("DEBUG building PDF now...")

    story.extend(build_reference_maps_section(styles))

    try:
        doc.build(
            story,
            onFirstPage=draw_cover_page if cover_text else draw_main_page_decor,
            onLaterPages=draw_running_header,
        )
    except Exception as exc:
        print("ERROR inside render_pdf/doc.build:", repr(exc))
        raise

    print("DEBUG doc.build returned")
    print("DEBUG pdf exists after build =", output_path.exists())
    print("DEBUG pdf size =", output_path.stat().st_size if output_path.exists() else "MISSING")

def main() -> int:
    ensure_dirs()

    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y%m%d-%H%M%SZ")

    latest_pdf = LATEST_DIR / "philippines_mission_intel_status_report_latest.pdf"
    latest_txt = LATEST_DIR / "philippines_mission_intel_status_report_latest.txt"
    latest_diff = LATEST_DIR / "philippines_mission_intel_status_report_latest.diff.txt"
  
    archive_pdf = ARCHIVE_DIR / f"philippines_mission_intel_status_report_{timestamp}.pdf"
    archive_txt = ARCHIVE_DIR / f"philippines_mission_intel_status_report_{timestamp}.txt"
    archive_diff = ARCHIVE_DIR / f"philippines_mission_intel_status_report_{timestamp}.diff.txt"
    archive_status = ARCHIVE_DIR / f"philippines_mission_intel_status_report_{timestamp}.status.json"

    payloads = []

    try:
        payloads = collect_all_sources()
        used_cache = any(p.raw_metadata.get("cache_fallback") for p in payloads)

        annex_c = load_json(ANNEX_C_PATH)
        pmisr_template = load_json(PMISR_V2_TEMPLATE_PATH)

        records = [p.to_source_record() for p in payloads]
        for r in records:
            reference_time = getattr(r, "reference_time", None)

            if reference_time is None:
                print("BAD RECORD TYPE:", type(r))
                print("BAD RECORD FIELDS:", vars(r))

        freshness = validate_all_sources(records)

        events = payloads_to_events(payloads)
        signals = detect_signals(events)

        condition = evaluate_condition(signals)

        crisis_banner = build_crisis_banner(signals)
        commanders_summary = generate_commanders_summary(signals)

        decision = evaluate_posture(payloads, condition)
        posture = decision.get("posture", "NORMAL")

        section_map = build_base_section_map(payloads)

        section_map["Commander's Summary"] = commanders_summary
        section_map["Decision Guidance"] = build_decision_guidance(posture)

        inject_annex_actions(section_map, annex_c, condition)

        section_map[SECTION_SOUTHERN_MOBILITY] = build_southern_mobility_section()

        section_map["Contingency Evacuation"] = (
            "Contingency Evacuation\n\n"
            "Primary Evacuation Destinations (Low Friction Entry)\n"
            "- Malaysia, Singapore, and Thailand remain the most viable immediate evacuation destinations for U.S. and Philippine passport holders under short-notice conditions.\n"
            "- All three countries permit short-term entry without visa pre-approval for both passport types under normal conditions.\n\n"
            "Entry Processing (Critical Detail)\n"
            "- All three destinations require submission of a digital arrival declaration prior to arrival:\n"
            "- Malaysia: MDAC (Malaysia Digital Arrival Card)\n"
            "- Singapore: SG Arrival Card (SGAC)\n"
            "- Thailand: TDAC (Thailand Digital Arrival Card)\n"
            "- These are NOT visas and do NOT require adjudication or approval wait times.\n"
            "- Submission processing is typically immediate (seconds to minutes).\n"
            "- Travelers receive a confirmation (QR code or acknowledgment) upon completion.\n\n"
            "Execution Guidance\n"
            "- Complete arrival card submission BEFORE departing for the airport whenever possible.\n"
            "- Save confirmation locally (screenshot or PDF) to ensure offline access.\n"
            "- Airline check-in personnel may verify completion prior to boarding.\n"
            "- Immigration authorities at destination will make final entry determination on arrival.\n\n"
            "Operational Reality\n"
            "- Entry systems are declaration-based, not approval-based; delay risk is minimal under normal network conditions.\n"
            "- In disruption scenarios, failure to complete arrival forms may slow processing but does not automatically prevent entry.\n"
            "- Time required to complete entry requirements is typically shorter than time required to secure outbound flight.\n\n"
            "Destination Prioritization\n"
            "- Malaysia: Best balance of accessibility, proximity, and onward routing flexibility.\n"
            "- Singapore: Highest infrastructure reliability and administrative predictability.\n"
            "- Thailand: Broad flight availability and strong redundancy in commercial routing.\n\n"
            "Decision Guidance\n"
            "- If NAIA operations remain functional: proceed with standard outbound routing.\n"
            "- If flight disruptions increase or security posture degrades: initiate early movement to any of the three primary destinations.\n"
            "- If time-constrained: prioritize earliest available departure regardless of destination among the three.\n\n"
            "Bottom Line\n"
            "- Malaysia, Singapore, and Thailand provide the fastest realistic evacuation pathways for U.S. and Philippine passport holders.\n"
            "- Digital entry requirements are rapid and non-blocking; flight availability remains the primary constraint on movement."
        )

# --- Hybrid normalization (full version) ---

        # Commander's Summary
        priority_ranking = build_priority_ranking_summary(section_map)

        section_map["Commander's Summary"] = (
            "Environment: Stable but sensitive.\n"
            "Most likely disruption: Weather / airport friction.\n"
            "Most dangerous escalation: Regional military tension affecting routing confidence, airspace posture, or crisis response timelines.\n"
            f"Operational posture: {posture}.\n\n"
            f"{priority_ranking}\n\n"
            "Bottom Line:\n"
            "Travel remains feasible under active monitoring. Proceed with movement planning, maintain alternate routing and lodging options, "
            "and verify embassy, airport, airline, and weather reporting throughout the travel window.\n\n"
            "Confidence: Medium"
        )

        # U.S. State Department travel advisories for Americans
        section_map["U.S. State Department travel advisories for Americans"] = render_intel_section(
            IntelSection(
                title="U.S. State Department travel advisories for Americans",
                narrative=(
                    "U.S. State Department travel advisory guidance for the Philippines establishes the baseline risk environment. "
                    "Travel is permitted under current conditions, but the operating environment includes **persistent, localized security threats** "
                    "that require active awareness and deliberate risk assessment.\n\n"

                    "Militant extremist groups, including the Abu Sayyaf Group (ASG), have historically conducted "
                    "**kidnappings, bombings, assassinations, and maritime attacks** in the southern Philippines. "
                    "While degraded, these groups are not eliminated and retain the capability for **localized violence and opportunistic targeting**, "
                    "including against foreign nationals.\n\n"

                    "Threat activity is concentrated in the **Sulu Archipelago (Jolo, Basilan, Tawi-Tawi)** and parts of "
                    "**western and central Mindanao**, where terrain, governance gaps, and limited security presence allow armed groups to operate.\n\n"

                    "These risks are **not evenly distributed across the country**. Manila and North Luzon are not driven by insurgent activity; however, "
                    "movement into southern or remote regions without situational awareness introduces exposure to **kidnapping, armed group presence, "
                    "and limited emergency response capability**.\n\n"

                    "The primary hazard is not random nationwide violence, but **misjudging geographic risk boundaries or engaging with unknown local contacts "
                    "in unfamiliar environments**."
                ),
                key_points=[
                    "State Department advisory provides national and regional risk baseline",
                    "Higher-risk areas remain geographically localized",
                    "Advisory changes can rapidly alter travel posture",
                ],
                operational_impact=[
                    "Verify advisory level prior to movement",
                    "Avoid or reassess travel to elevated-risk regions",
                    "Use advisory updates as trigger for reassessment",
                ],
                triggers=[
                    "State Department advisory level increase",
                    "New region-specific warning for Philippines",
                    "Kidnapping-for-ransom incident (especially involving foreigners)",
                    "Bombing or armed attack reported in Mindanao or nearby regions",
                    "Embassy security alert or movement restriction",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Stable advisory posture\n"
                    "Near-Term (3–7 days): Monitor for advisory updates\n"
                    "Mid-Term (7–30 days): Dependent on geopolitical and security developments"
                ),
                bottom_line=(
                    "Travel remains feasible, but failure to recognize localized high-risk areas can result in exposure to kidnapping or armed group activity."
                ),
                confidence="High",
            )
        )

        # Internal Security / Terrorism Assessment
        section_map["Internal Security / Terrorism Assessment"] = render_intel_section(
            IntelSection(
                title="Internal Security / Terrorism Assessment",
                narrative=(
                    "Internal security conditions in the Philippines are **uneven and highly location-dependent**. "
                    "While no active terrorist alerts affecting Metro Manila were identified at runtime, the country "
                    "maintains a **persistent internal threat environment involving insurgent groups, extremist elements, "
                    "and organized criminal networks**.\n\n"

                    "Militant groups in the southern Philippines have historically conducted **kidnappings, bombings, and armed attacks**, "
                    "but the more immediate risk to travelers is **unintentional exposure through poor situational awareness, unfamiliar contacts, "
                    "or movement outside established travel environments**.\n\n"

                    "Risk increases significantly when:\n"
                    "- Entering **remote or non-tourist areas** without local knowledge\n"
                    "- Accepting transportation or guidance from **unknown individuals**\n"
                    "- Conducting **unplanned travel outside established routes**\n"
                    "- Operating without clear communication, accountability, or exit options\n\n"

                    "The primary hazard is not being targeted directly, but **placing yourself into an environment where control, visibility, "
                    "and response capability are reduced**."
                ),
                key_points=[
                    "Internal security risk is uneven and location-dependent",
                    "Most incidents occur outside controlled urban/tourist environments",
                    "Unfamiliar contacts and unplanned movement increase exposure risk",
                ],
                operational_impact=[
                    "Stay within known, validated travel corridors",
                    "Avoid unvetted local contacts for transport or guidance",
                    "Maintain communication and accountability at all times",
                ],
                triggers=[
                    "Kidnapping-for-ransom activity reported",
                    "Armed attack or bombing incident",
                    "Movement into unfamiliar or remote areas",
                    "Loss of communication or situational awareness",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Stable in controlled areas\n"
                    "Near-Term (3–7 days): Risk driven by movement decisions\n"
                    "Mid-Term (7–30 days): Persistent but localized threat environment"
                ),
                bottom_line=(
                    "Internal security risk is primarily driven by movement, environment, and decision-making rather than random targeting."
                ),
                confidence="Medium-High",
            )
        )

        # Regional Security / External Threat Environment
        section_map["Regional Security / External Threat Environment"] = render_intel_section(
            IntelSection(
                title="Regional Security / External Threat Environment",
                narrative=(
                    "Regional security risk is driven primarily by **Chinese military, coast guard, and maritime militia activity** "
                    "in the South China Sea, plus broader Western Pacific tension involving Taiwan and the Luzon Strait.\n\n"

                    "Current activity does not automatically create a direct threat to travelers in Manila or North Luzon. "
                    "However, regional escalation could rapidly affect **commercial air routing, maritime movement, airport confidence, "
                    "fuel pricing, communications posture, and evacuation timelines**.\n\n"

                    "The key concern is not routine gray-zone activity by itself. The concern is a **change in tempo or character**: "
                    "direct confrontation, blockade-like behavior, airspace restriction, military mobilization, or hostile action near "
                    "Philippine territory or key transit corridors.\n\n"

                    "For mission planning, this section should be treated as an **external escalation monitor**. It informs whether "
                    "standard travel remains viable or whether contingency routing and early displacement should be prepared."
                ),
                key_points=[
                    "South China Sea and Taiwan/Luzon Strait activity are external escalation indicators",
                    "Routine gray-zone activity is monitor-only unless tempo or character changes",
                    "Escalation could affect airspace, maritime routing, and exfil timelines",
                ],
                operational_impact=[
                    "Monitor for military escalation affecting Luzon Strait, Taiwan, or Philippine waters",
                    "Validate aviation and maritime options if regional posture worsens",
                    "Prepare Annex C or alternate routing if commercial movement confidence degrades",
                ],
                triggers=[
                    "Direct confrontation involving Chinese and Philippine forces",
                    "PLA activity surge near Taiwan or Luzon Strait",
                    "Commercial airspace restriction or airline rerouting",
                    "Maritime blockade-like behavior or port disruption",
                    "Embassy or State Department warning tied to regional military escalation",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Monitor for tempo change\n"
                    "Near-Term (3–7 days): Watch aviation and maritime confidence\n"
                    "Mid-Term (7–30 days): Regional tension remains persistent"
                ),
                bottom_line=(
                    "Regional security activity is not currently a direct traveler threat, but escalation could rapidly affect movement, routing, and evacuation options."
                ),
                confidence="Medium",
            )
        )

        # Health / Environmental Risk
        section_map[SECTION_HEALTH_ENVIRONMENT] = render_intel_section(
            IntelSection(
                title="Health / Environmental Risk",
                narrative=(
                    "Health and environmental risk should be treated as an operational endurance issue, not the primary threat driver. "
                    "The most likely degraders are **heat injury, dehydration, food/water illness, mosquito-borne disease, and fatigue**.\n\n"

                    "These risks are persistent and cumulative. They are less dramatic than security threats but can degrade judgment, mobility, "
                    "and decision-making if ignored during movement, airport delays, ground transit, or extended outdoor exposure."
                ),
                key_points=[
                    "Heat, hydration, food/water discipline, and mosquito exposure are the main health concerns",
                    "Risk increases during delays, long movement windows, and poor rest cycles",
                    "Medical issues can reduce mobility and decision quality during contingency execution",
                ],
                operational_impact=[
                    "Carry water, electrolytes, basic medication, and insect repellent",
                    "Avoid questionable food/water sources before or during movement",
                    "Monitor for heat exhaustion, gastrointestinal illness, fever, or dehydration",
                ],
                triggers=[
                    "Heat index or prolonged midday exposure",
                    "Disease outbreak reporting",
                    "Gastrointestinal illness or fever during travel window",
                    "Loss of access to reliable food, water, or medical care",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Routine risk present\n"
                    "Near-Term (3–7 days): Risk driven by exposure and discipline\n"
                    "Mid-Term (7–30 days): Seasonal/environmental patterns persist"
                ),
                bottom_line=(
                    "Health risk is not the main threat, but poor heat, water, food, or mosquito discipline can degrade mission effectiveness."
                ),
                confidence="High",
            )
        )

        # NAIA
        section_map["NAIA / airport operational status"] = render_intel_section(
            IntelSection(
                title="NAIA / airport operational status",
                narrative=(
                    "Ninoy Aquino International Airport (NAIA) remains operational, but the reliability of its public reporting "
                    "channels is inconsistent. The official news feed cannot be treated as a primary real-time indicator due to "
                    "API instability and inconsistent data availability.\n\n"
                    "Operational awareness must therefore rely on multiple sources, including airline status, third-party tracking, "
                    "and real-time observation of delays or cancellations."
                ),
                key_points=[
                    "No confirmed disruption at runtime",
                    "Official NAIA reporting is unreliable as sole source",
                    "Airport conditions can change rapidly",
                ],
                operational_impact=[
                    "Do not rely solely on NAIA website updates",
                    "Cross-check flight status with airline sources",
                    "Build buffer time into airport movement",
                ],
                triggers=[
                    "Flight cancellation clusters",
                    "Check-in or security backlog",
                    "Airline system disruption",
                    "Ground handling delays",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Stable but variable\n"
                    "Near-Term (3–7 days): Monitor throughput and congestion\n"
                    "Mid-Term (7–30 days): Chronic variability persists"
                ),
                bottom_line=(
                    "NAIA remains operational but unreliable as a single-source indicator; use multi-source verification."
                ),
                execution=(
                    "Cross-check flight status using airline app, FlightAware, and airport displays. "
                    "Treat airline source as authoritative over NAIA public reporting. "
                    "Reconfirm status at T-6h, T-3h, and departure."
                ),
                confidence="Low",
            )
        )

        # Geological / Volcanic Activity
        section_map["Geological / Volcanic Activity"] = render_intel_section(
            IntelSection(
                title="Geological / Volcanic Activity",
                narrative=(
                    "Geological risk in the Philippines is a standing operational concern due to active volcanoes, seismic activity, "
                    "ashfall potential, landslides, and lahar-prone terrain. The primary operational concern is not the volcano itself, "
                    "but secondary effects that can degrade movement: **airport disruption, road closure, ashfall, reduced visibility, "
                    "water contamination, landslide risk, and local evacuation congestion**.\n\n"

                    "Volcanic or seismic activity affecting Luzon, Manila airspace, major highways, or port access should be treated as "
                    "a movement and sustainment problem. Even localized activity can create cascading delays if it affects aviation, "
                    "ground routes, or municipal disaster-response posture."
                ),
                key_points=[
                    "Volcanic and seismic activity can affect air, ground, and maritime movement",
                    "Ashfall and landslides are the main practical movement hazards",
                    "Localized geological events can cause wider transportation disruption",
                ],
                operational_impact=[
                    "Monitor PHIVOLCS alert changes and ashfall advisories",
                    "Check aviation status if ash cloud or visibility issues are reported",
                    "Avoid movement through landslide-prone or lahar-affected routes",
                ],
                triggers=[
                    "PHIVOLCS volcano alert level increase",
                    "Ashfall advisory affecting Luzon, Manila, or flight corridors",
                    "Earthquake causing infrastructure damage or road closure",
                    "Landslide, lahar, or evacuation notice along movement routes",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Monitor active bulletins\n"
                    "Near-Term (3–7 days): Watch ashfall, rain interaction, and road impacts\n"
                    "Mid-Term (7–30 days): Persistent geological baseline risk"
                ),
                bottom_line=(
                    "Geological activity is primarily a movement-disruption risk; escalate if ashfall, route closure, airport disruption, or evacuation orders appear."
                ),
                confidence="Medium",
            )
        )

        # Contingency Diversion
        section_map["Contingency Diversion"] = render_intel_section(
            IntelSection(
                title="Contingency Diversion",
                narrative=(
                    "- Primary departure node remains NAIA unless airport operations degrade.\n"
                    "- Prepare alternate movement routing, lodging extensions, and ground transport options if flight disruptions expand.\n"
                    "- If security, transportation, or weather indicators deteriorate, prioritize early movement before bottlenecks form.\n"
                    "- Reconfirm passport access, ticketing flexibility, communications, and embassy contact procedures daily."  
                    "Regional diversion planning must account for visa-free or low-friction entry points that can be used "
                    "under time-sensitive conditions. While multiple destinations appear accessible on paper, real-world "
                    "entry depends on passport type, documentation, and current policy enforcement.\n\n"
                    "Only a limited number of locations consistently provide reliable dual-passport access without "
                    "pre-arrival requirements, making them the most viable contingency options."
                ),
                key_points=[
                    "Limited number of reliable visa-free fallback locations",
                    "Entry requirements vary between U.S. and Philippine passports",
                    "Final admission always subject to local authority decision",
                ],
                operational_impact=[
                    "Pre-identify viable diversion locations",
                    "Maintain documentation readiness",
                    "Verify entry conditions before execution",
                ],
                triggers=[
                    "Loss of access to primary destination",
                    "Flight cancellation or routing disruption",
                    "Security or political restriction affecting Philippines",
                ],
                time_horizon=(
                    "Immediate (0–72 hours): Available for rapid diversion\n"
                    "Near-Term (3–7 days): Monitor entry requirement changes\n"
                    "Mid-Term (7–30 days): Policy changes possible"
                ),
                bottom_line=(
                    "Diversion planning is viable but must be validated against real-time entry conditions."
                ),
                confidence="Medium",
            )
        )

        inject_annex_actions(section_map, annex_c, condition)

        section_map[SECTION_ESCALATION] = build_escalation_thresholds_section()

        for key, value in section_map.items():
            if value is None:
                section_map[key] = REQUIRED_SECTION_FALLBACKS.get(
                    key,
                    f"{key}\n\nBaseline risk remains present. No elevated runtime signal identified."
                )

        previous_latest_text = latest_txt.read_text(encoding="utf-8") if latest_txt.exists() else ""

        provisional_report_text = build_report_text(section_map, crisis_banner=crisis_banner)

        for key, value in section_map.items():
            if value is None:
                section_map[key] = f"{key}\n\nNo significant data available at runtime."

        provisional_report_text = build_report_text(section_map, crisis_banner=crisis_banner)

        normalized_previous = normalize_for_diff(previous_latest_text) if previous_latest_text else ""
        normalized_provisional = normalize_for_diff(provisional_report_text)

        provisional_delta_text = diff_text(normalized_previous, normalized_provisional)
        provisional_delta_line_count = count_diff_lines(provisional_delta_text)

        alerts = build_alerts(payloads, used_cache, now_utc)
        alerts = list(dict.fromkeys(alerts))

        delta_summary_text = generate_delta_summary(
            diff_lines=provisional_delta_line_count,
            alerts=alerts,
        )

        records = [p.to_source_record() for p in payloads]

        records = [r for r in records if r is not None]

        section_map["Significant Changes Since Last Report"] = delta_summary_text
        section_map["Quality Control Summary"] = "Pending final delta assessment."

        for key, value in section_map.items():
            print(
                "DEBUG section_map item:",
                repr(key),
                type(value).__name__,
                len(str(value).split()) if value is not None else "NONE",
                repr(str(value)[:120]) if value is not None else "NONE",
            )

        report_text = build_report_text(section_map, crisis_banner=crisis_banner)

        print("DEBUG report_text word count =", len(report_text.split()))
        print("DEBUG report_text chars =", len(report_text))

        normalized_current = normalize_for_diff(report_text)
        delta_text = diff_text(normalized_previous, normalized_current)
        delta_line_count = count_diff_lines(delta_text)
        significant_change_detected = delta_line_count >= SIGNIFICANT_DIFF_THRESHOLD

        if significant_change_detected:
            alerts.append("SIGNIFICANT_DELTA_DETECTED")

        alerts = list(dict.fromkeys(alerts))

        delta_summary_text = generate_delta_summary(
            diff_lines=delta_line_count,
            alerts=alerts,
        )

        quality_summary_text = generate_quality_control_summary(
            sources_checked=freshness["sources_checked"],
            failed_optional_count=freshness["failed_optional_count"],
            used_cache_fallback=used_cache,
            significant_change_detected=significant_change_detected,
            high_severity_signal_count=len([s for s in signals if s.score >= 9]),
        )

        section_map["Significant Changes Since Last Report"] = delta_summary_text
        section_map["Quality Control Summary"] = quality_summary_text

        for section in REQUIRED_SECTIONS:
            if section not in report_text:
                fallback = REQUIRED_SECTION_FALLBACKS.get(section)
                if fallback:
                    section_map[section] = fallback

        report_text = build_report_text(section_map, crisis_banner=crisis_banner)

        for section in REQUIRED_SECTIONS:
            if section not in report_text:
                fallback = REQUIRED_SECTION_FALLBACKS.get(section)
                if fallback:
                    section_map[section] = fallback

        report_text = build_report_text(section_map, crisis_banner=crisis_banner)

        expected_sections = list(REPORT_SECTION_ORDER)
        missing_rendered = [name for name in expected_sections if name not in report_text]

        for name in missing_rendered:
            print(f"WARNING: Section collected but not rendered -> {name}")

        print("DEBUG: ABOUT TO WRITE TXT")

        latest_txt.write_text(report_text, encoding="utf-8")
        archive_txt.write_text(report_text, encoding="utf-8")

        latest_diff.write_text(delta_text, encoding="utf-8")
        archive_diff.write_text(delta_text, encoding="utf-8")

        cover_text = build_cover_page(now_utc, signals, used_cache)

        archive_pdf.parent.mkdir(parents=True, exist_ok=True)
        latest_pdf.parent.mkdir(parents=True, exist_ok=True)

        # Render to latest first
        render_pdf(report_text, latest_pdf, cover_text=cover_text)

        # Then archive the finished latest PDF
        shutil.copy2(latest_pdf, archive_pdf)

        validation = validate_report_text(report_text)

        phase = "validated_with_cache_fallback" if used_cache else "validated"
        message = (
            "Report generated and validated successfully using cached fallback data."
            if used_cache
            else "Report generated and validated successfully."
        )

        status = RunStatus(
            ok=True,
            phase=phase,
            generated_at_utc=utc_now_iso(),
            report_path=str(latest_pdf),
            message=message,
            details={
                "freshness": freshness,
                "validation": validation,
                "delta": {
                    "previous_report_found": bool(previous_latest_text),
                    "diff_line_count": delta_line_count,
                    "significant_change_detected": significant_change_detected,
                    "significant_diff_threshold": SIGNIFICANT_DIFF_THRESHOLD,
                },
                "alerts": alerts,
                "quality_control": {
                    "sources_checked": freshness["sources_checked"],
                    "failed_optional_sources": freshness["failed_optional_count"],
                    "used_cache_fallback": used_cache,
                    "significant_change_detected": significant_change_detected,
                    "high_severity_signal_count": len([s for s in signals if s.score >= 9]),
                    "overall_report_confidence": (
                        "Medium" if len([s for s in signals if s.score >= 9]) == 0 else "Medium-High"
                    ),
                },
                "source_health": {
                    "live_sources": [
                        p.section_name for p in payloads if p.raw_metadata.get("live_mode")
                    ],
                    "cache_fallback_sources": [
                        p.section_name for p in payloads if p.raw_metadata.get("cache_fallback")
                    ],
                    "stub_sources": [
                        p.section_name
                        for p in payloads
                        if str(p.raw_metadata.get("provider", "")).lower() == "stub"
                        and not p.raw_metadata.get("cache_fallback")
                    ],
                },
                "sources": [
                    {
                        "source_name": p.source_name,
                        "section_name": p.section_name,
                        "retrieved_at_utc": p.retrieved_at_utc.isoformat(),
                        "source_timestamp_utc": p.source_timestamp_utc.isoformat(),
                        "source_type": p.source_type,
                        "required": p.required,
                        "max_age_hours": p.max_age_hours,
                        "notes": p.notes,
                        "raw_metadata": p.raw_metadata,
                    }
                    for p in payloads
                ],
            },
        )

               
        write_status(status)
        archive_status.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    
        print(
            "SUCCESS: Report generated and validated successfully "
            + ("using cached fallback data." if used_cache else "with live/current source data.")
        )
        print(f"Archive PDF: {archive_pdf}")
        print(f"Archive status: {archive_status}")
        print(f"Word count: {validation['word_count']}")
        print(f"Pages: {validation.get('pages', validation.get('page_count', 'unknown'))}")

        validation = validate_report_text(report_text)
        pdf_validation = validate_report_pdf(str(latest_pdf))
        
        print(f"DEBUG validation keys: {list(validation.keys())}")
        print(f"Alerts: {', '.join(alerts) if alerts else 'none'}")
        print(f"Failed optional sources: {len(freshness.get('failed_optional_sources', []))}")
        print(f"Report path: {status.report_path}")


        return 0

    except ReportValidationError as e:
        status = RunStatus(
            ok=False,
            phase="validation_failed",
            generated_at_utc=utc_now_iso(),
            report_path=str(latest_pdf) if latest_pdf.exists() else None,
            message=str(e),
            details={},
        )
        write_status(status)
        print(f"VALIDATION FAILED: {e}", file=sys.stderr)
        return 2

    except FreshnessValidationError as e:
        status = RunStatus(
            ok=False,
            phase="freshness_failed",
            generated_at_utc=utc_now_iso(),
            report_path=None,
            message=str(e),
            details={},
        )
        write_status(status)
        print(f"FRESHNESS FAILED: {e}", file=sys.stderr)
        return 3

    except SourceAdapterError as e:
        status = RunStatus(
            ok=False,
            phase="source_collection_failed",
            generated_at_utc=utc_now_iso(),
            report_path=None,
            message=str(e),
            details={},
        )
        write_status(status)
        print(f"SOURCE COLLECTION FAILED: {e}", file=sys.stderr)
        return 4

    except ValueError as e:
        status = RunStatus(
            ok=False,
            phase="configuration_error",
            generated_at_utc=utc_now_iso(),
            report_path=None,
            message=str(e),
            details={},
        )
        write_status(status)
        print(f"CONFIGURATION ERROR: {e}", file=sys.stderr)
        return 5

    except Exception as e:
        status = RunStatus(
            ok=False,
            phase="generation_error",
            generated_at_utc=utc_now_iso(),
            report_path=None,
            message=str(e),
            details={},
        )
        write_status(status)
        traceback.print_exc()
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

