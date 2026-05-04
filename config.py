from pathlib import Path
import os

OUTPUT_DIR = Path(r"C:\Users\mchap\My Drive\Philippines Mission Intel\outputs")
LATEST_DIR = OUTPUT_DIR / "latest"
ARCHIVE_DIR = OUTPUT_DIR / "archive"

BASE_DIR = Path(__file__).resolve().parent

ANNEXES_DIR = BASE_DIR / "annexes"
TEMPLATES_DIR = BASE_DIR / "templates"

ANNEX_C_PATH = ANNEXES_DIR / "annex_c_complete.json"
ANNEX_C_SCHEMA_PATH = ANNEXES_DIR / "annex_c.schema.json"
PMISR_V2_TEMPLATE_PATH = TEMPLATES_DIR / "pmisr_v2_template.json"

LATEST_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

USE_LIVE_WEATHER = os.getenv("USE_LIVE_WEATHER", "1") == "1"
WEATHER_API_URL = os.getenv(
    "WEATHER_API_URL",
    "https://api.open-meteo.com/v1/forecast",
).strip()
WEATHER_TIMEOUT_SEC = int(os.getenv("WEATHER_TIMEOUT_SEC", "15"))

USE_LIVE_STATE_DEPT = os.getenv("USE_LIVE_STATE_DEPT", "1") == "1"
STATE_DEPT_URL = os.getenv(
    "STATE_DEPT_URL",
    "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/philippines-travel-advisory.html",
).strip()
STATE_DEPT_TIMEOUT_SEC = int(os.getenv("STATE_DEPT_TIMEOUT_SEC", "15"))

USE_LIVE_EMBASSY = os.getenv("USE_LIVE_EMBASSY", "1") == "1"
EMBASSY_URL = os.getenv(
    "EMBASSY_URL",
    "https://ph.usembassy.gov/category/alert/",
).strip()
EMBASSY_TIMEOUT_SEC = int(os.getenv("EMBASSY_TIMEOUT_SEC", "15"))

USE_LIVE_NAIA = os.getenv("USE_LIVE_NAIA", "1") == "1"
NAIA_URL = os.getenv(
    "NAIA_URL",
    "https://newnaia.com.ph/about-us/news",
).strip()
NAIA_API_URL = os.getenv(
    "NAIA_API_URL",
    "https://newnaia.com.ph/api/v1/page/news/data-list",
).strip()
NAIA_TIMEOUT_SEC = int(os.getenv("NAIA_TIMEOUT_SEC", "15"))

USE_LIVE_IMMUNIZATION = os.getenv("USE_LIVE_IMMUNIZATION", "1") == "1"
IMMUNIZATION_URL = os.getenv(
    "IMMUNIZATION_URL",
    "https://wwwnc.cdc.gov/travel/destinations/traveler/none/philippines",
).strip()
IMMUNIZATION_TIMEOUT_SEC = int(os.getenv("IMMUNIZATION_TIMEOUT_SEC", "15"))

USE_LIVE_PRIORITY_INTEL = os.getenv("USE_LIVE_PRIORITY_INTEL", "1") == "1"
REGIONAL_SECURITY_URL = os.getenv(
    "REGIONAL_SECURITY_URL",
    "https://www.mnd.gov.tw/en/news/PlaactList",
).strip()
REGIONAL_SECURITY_TIMEOUT_SEC = int(os.getenv("REGIONAL_SECURITY_TIMEOUT_SEC", "15"))

LIVE_MILITARY_SOURCES = [
    {
        "name": "Taiwan MND PLA Activity",
        "url": "https://www.mnd.gov.tw/en/news/PlaactList",
        "priority": "PRIMARY",
        "ttl_days": 2,
        "watch_terms": ["PLA aircraft", "PLAN ships", "median line", "ADIZ", "Taiwan Strait"],
    },
    {
        "name": "Focus Taiwan / CNA",
        "url": "https://focustaiwan.tw/politics",
        "priority": "PRIMARY",
        "ttl_days": 7,
        "watch_terms": ["China", "PLA", "Taiwan Strait", "live-fire", "drills", "gray-zone"],
    },
    {
        "name": "USNI News",
        "url": "https://news.usni.org/",
        "priority": "PRIMARY",
        "ttl_days": 14,
        "watch_terms": ["Philippines", "Luzon", "Taiwan", "China", "PLA", "Balikatan", "Bashi Channel"],
    },
    {
        "name": "GMA News",
        "url": "https://www.gmanetwork.com/news/",
        "priority": "SECONDARY",
        "ttl_days": 7,
        "watch_terms": ["China", "Luzon", "Taiwan", "live-fire", "West Philippine Sea", "Bashi Channel"],
    },
{
    "name": "Philstar",
    "url": "https://www.philstar.com/",
    "priority": "medium",
    "watch_terms": [
        "South China Sea",
        "West Philippine Sea",
        "China Coast Guard",
        "Armed Forces of the Philippines",
        "Philippine Navy",
        "military exercise",
        "patrol",
        "Scarborough Shoal",
    ],
},
{
    "name": "Inquirer",
    "url": "https://www.inquirer.net/",
    "priority": "medium",
    "watch_terms": [
        "West Philippine Sea",
        "South China Sea",
        "China Coast Guard",
        "Philippine Navy",
        "AFP",
        "military exercise",
        "patrol",
    ],
},
{
    "name": "Rappler",
    "url": "https://www.rappler.com/",
    "priority": "medium",
    "watch_terms": [
        "West Philippine Sea",
        "South China Sea",
        "China Coast Guard",
        "Philippine Navy",
        "Armed Forces of the Philippines",
        "military exercise",
        "patrol",
        "Scarborough Shoal",
        "Batanes",
        "Palawan",
    ],
},
{
    "name": "Manila Bulletin",
    "url": "https://mb.com.ph/",
    "priority": "medium",
    "watch_terms": [
        "West Philippine Sea",
        "South China Sea",
        "China Coast Guard",
        "Philippine Navy",
        "AFP",
        "military exercise",
        "patrol",
    ],
},
]