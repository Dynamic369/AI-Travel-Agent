import os
import requests
from typing import List, Dict

OTM_KEY = os.getenv("OPENTRIPMAP_KEY")

BASE_URL = "https://api.opentripmap.com/0.1/en/places"

def bbox_from_city(city:str) ->Dict:
    """
    A minimal helper: use geocoding to get lat/lon and bbox.
    Here we'll use OpenTripMap geoname endpoint.
    """
    # If multiple cities are provided (comma-separated), use only the first one
    city_name = city.split(',')[0].strip() if ',' in city else city.strip()
    
    r = requests.get(f"{BASE_URL}/geoname", params={"name": city_name, "apikey":OTM_KEY})
    r.raise_for_status()
    data = r.json()
    
    # Validate that we got valid coordinates
    if not isinstance(data, dict) or 'lat' not in data or 'lon' not in data:
        raise ValueError(f"Geoname lookup failed for city: {city_name}. Response: {data}")
    
    return data ## contains lat/lon and population etc.

def fetch_attraction(city:str, radius_m:int = 10000, kinds:str="interesting_places",limit:int=30) ->List[Dict]:
    """
    Fetch POIs via OpenTripMAp.
    kinds: comma seprated categorieas. We'll filter by interests downstream.
    """
    geo = bbox_from_city(city)
    lat = geo.get("lat")
    lon = geo.get("lon")
    
    if lat is None or lon is None:
        raise ValueError(f"Could not get coordinates for city: {city}. Geo response: {geo}")
    
    params = {
        "radius": radius_m,
        "lon": lon,
        "lat": lat,
        "kinds": kinds,
        "rate": 2,
        "format": "json",
        "limit": limit,
        "apikey": OTM_KEY
    }
    r = requests.get(f"{BASE_URL}/radius",params=params)
    r.raise_for_status()
    places = r.json()
    # Normalize keys
    result = []
    for p in places:
        result.append({
            "xid": p.get("xid"),
            "name": p.get("name"),
            "kinds": p.get("kinds"),
            "lat": p.get("point", {}).get("lat"),
            "lon": p.get("point", {}).get("lon"),
            "dist": p.get("dist")
        })
    return result

