from __future__ import annotations

from datetime import datetime, timezone

from sources.base import BaseSourceAdapter
from sources.source_models import SourcePayload


class VisaAdapter(BaseSourceAdapter):
    CACHE_KEY = "visa_baseline"

    def _build_payload(self) -> SourcePayload:
        now = datetime.now(timezone.utc)

        content = (
            "Regional Visa-Free Travel Overview\n\n"
            "The following nearby Asia-Pacific destinations represent generally accessible regional travel options "
            "for U.S. and/or Philippine passport holders under normal conditions. This section is a broad awareness "
            "overview only.\n\n"
            "These destinations may require additional entry steps such as arrival cards, onward travel proof, "
            "or digital registration systems.\n\n"
            "- Japan\n"
            "- South Korea\n"
            "- Singapore\n"
            "- Hong Kong\n"
            "- Macau\n"
            "- Thailand\n"
            "- Malaysia\n"
            "- Brunei\n"
            "- Indonesia\n"
            "- Vietnam\n"
            "- Taiwan\n\n"
            "Interpretation:\n"
            "- This section is NOT intended for immediate contingency execution.\n"
            "- Entry conditions vary between U.S. and Philippine passport holders.\n"
            "- Use the contingency diversion footnote for strict, verified fallback options.\n"
        )

        return SourcePayload(
            source_name="Regional Visa-Free Overview",
            section_name="Visa-free diversion baseline",
            content=content,
            source_type="DOCUMENT",
            required=True,
            retrieved_at_utc=now,
            source_timestamp_utc=now,
            max_age_hours=24,
            notes="Broad awareness only; not operational fallback list.",
        )

    def fetch(self) -> SourcePayload:
        return self._build_payload()