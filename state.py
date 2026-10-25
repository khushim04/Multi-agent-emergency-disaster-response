
from typing import TypedDict


class DisasterState(TypedDict):
    location: str

    # Weather API results
    latitude: float
    longitude: float
    observation_time: str
    temperature_c: float
    humidity_percent: float
    current_precipitation_mm: float
    rainfall_mm: float
    weather_code: int
    wind_speed_kmh: float
    weather_status: str

    # Workflow results
    risk_level: str
    recommendation: str
    shelter_options: list[str]
    agent_logs: list[str]
    summary: str
    communication_message: str
