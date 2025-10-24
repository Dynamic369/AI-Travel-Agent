import requests
from typing import Dict, Any

def fetch_weather_by_coords(lat:float, lon:float, days:int=7) -> Dict[str,Any]:
    """
    Open-Meteo free API. Returns daily forecasts for the nexts days.
    """
    params = {
        "latitude":lat,
        "longitude":lon,
        "daily":"weathercode,temperature_2m_max,temperature_2m_min",
        "timezone":"UTC",
        "forecast_days":days
    }
    r = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    r.raise_for_status()
    return r.json()