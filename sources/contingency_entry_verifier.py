from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import certifi
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class VerificationResult:
    ok: bool
    summary: str
    source_url: str
    last_checked_utc: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fetch_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, verify=certifi.where())
        r.raise_for_status()
        return r.text
    except Exception:
        r = requests.get(url, timeout=10, verify=False)
        r.raise_for_status()
        return r.text


def verify_singapore() -> VerificationResult:
    url = "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements"
    text = _fetch_text(url)

    sg_arrival_not_visa = "SG Arrival Card is not a visa" in text
    philippines_not_listed = "Philippines" not in text[text.find("Travel Documents by Countries and Places"):]
    ok = sg_arrival_not_visa and philippines_not_listed

    return VerificationResult(
        ok=ok,
        summary="Singapore verified." if ok else "Singapore verification failed.",
        source_url=url,
        last_checked_utc=_now_iso(),
    )



def verify_malaysia() -> VerificationResult:
    url = "https://imigresen-online.imi.gov.my/mdac/main"
    text = _fetch_text(url)

    mdac_present = "MALAYSIA DIGITAL ARRIVAL CARD" in text.upper() or "MDAC" in text
    ok = mdac_present

    return VerificationResult(
        ok=ok,
        summary="Malaysia verified." if ok else "Malaysia verification failed.",
        source_url=url,
        last_checked_utc=_now_iso(),
    )


def verify_thailand() -> VerificationResult:
    url = "https://tdac.immigration.go.th/arrival-card/#/home"
    text = _fetch_text(url)

    tdac_present = "Thailand Digital Arrival Card" in text or "TDAC" in text
    ok = tdac_present

    return VerificationResult(
        ok=ok,
        summary="Thailand verified." if ok else "Thailand verification failed.",
        source_url=url,
        last_checked_utc=_now_iso(),
    )