from __future__ import annotations
from config import WEATHER_API_URL, WEATHER_TIMEOUT_SEC

from sources.embassy_adapter import EmbassyManilaAdapter
from sources.immunization_adapter import ImmunizationAdapter
from sources.live_military_adapter import LiveMilitaryAdapter
from sources.naia_adapter import NAIAAdapter
from sources.state_department_adapter import StateDepartmentAdapter
from sources.strategic_adapter import StrategicIntelAdapter
from sources.weather_adapter import WeatherAdapter
from sources.source_models import SourcePayload
from sources.priority_adapter import PriorityIntelAdapter
from sources.regional_maritime_adapter import RegionalMaritimeAdapter
from sources.terrorism_adapter import TerrorismAdapter
from sources.aviation_adapter import AviationAdapter
from sources.visa_adapter import VisaAdapter
from sources.contingency_entry_adapter import ContingencyEntryAdapter
from sources.phivolcs_adapter import PHIVOLCSAdapter


def collect_all_sources() -> list[SourcePayload]:
    weather_api_url = WEATHER_API_URL
    weather_timeout_sec = WEATHER_TIMEOUT_SEC

    adapters = [
        StrategicIntelAdapter(),
        PriorityIntelAdapter(),
        RegionalMaritimeAdapter(),
        TerrorismAdapter(),
        EmbassyManilaAdapter(),
        StateDepartmentAdapter(),
        ImmunizationAdapter(),
        WeatherAdapter(api_url=weather_api_url, timeout_sec=weather_timeout_sec),
        PHIVOLCSAdapter(),
        AviationAdapter(),
        NAIAAdapter(),
        VisaAdapter(),
        ContingencyEntryAdapter(),
        LiveMilitaryAdapter(timeout_sec=15),
    ]

    return [adapter.fetch() for adapter in adapters]

  