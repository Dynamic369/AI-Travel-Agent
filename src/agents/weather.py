from model import TravelState
from typing import Dict, Any
from src.utils.opentripmap import bbox_from_city
from src.utils.open_meteo import fetch_weather_by_coords

def weather_node(state:TravelState)->Dict[str, Any]:
    if not state.city:
        return {"error":"weather: no city provided"}
    
    try:
        geo = bbox_from_city(state.city)
        lat = geo.get('lat')
        lon = geo.get('lon')
        weather = fetch_weather_by_coords(lat, lon, days=state.days or 7)

        #Compact relevant forecast (daily)
        daily = weather.get("daily",{})
        return {"weather_data":daily, 'status':"Weather_completed"}
    
    except Exception as e:
        return {"error":f"Weather_node's error {e}"}

                                          