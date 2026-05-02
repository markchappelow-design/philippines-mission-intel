DEFAULT_MAX_AGE_HOURS = 72


SOURCE_MAX_AGE_HOURS = {
    "US Embassy Manila": 168,
    "US State Department Philippines Travel Advisory": 168,
    "CDC Travelers Health Philippines": 720,
    "PAGASA": 24,
    "PHIVOLCS": 48,
    "NAIA": 48,
    "Maritime Security Feed": 72,
    "Aviation Disruption Feed": 72,
}


def get_source_max_age_hours(source_name: str) -> int:
    return SOURCE_MAX_AGE_HOURS.get(source_name, DEFAULT_MAX_AGE_HOURS)