    def __init__(self, api_url: str = WEATHER_API_URL, timeout_sec: int = WEATHER_TIMEOUT_SEC) -> None:
        self.api_url = api_url
        self.timeout_sec = timeout_sec