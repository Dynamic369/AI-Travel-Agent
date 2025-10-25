# import os
# import requests
# from typing import List, Dict

# OTM_KEY = os.getenv("OPENTRIPMAP_KEY")

# BASE_URL = "https://api.opentripmap.com/0.1/en/places"

# def bbox_from_city(city:str) ->Dict:
#     """
#     A minimal helper: use geocoding to get lat/lon and bbox.
#     Here we'll use OpenTripMap geoname endpoint.
#     """
#     # If multiple cities are provided (comma-separated), use only the first one
#     city_name = city.split(',')[0].strip() if ',' in city else city.strip()
    
#     r = requests.get(f"{BASE_URL}/geoname", params={"name": city_name, "apikey":OTM_KEY})
#     r.raise_for_status()
#     data = r.json()
    
#     # Validate that we got valid coordinates
#     if not isinstance(data, dict) or 'lat' not in data or 'lon' not in data:
#         raise ValueError(f"Geoname lookup failed for city: {city_name}. Response: {data}")
    
#     return data ## contains lat/lon and population etc.

# def fetch_attraction(city:str, radius_m:int = 10000, kinds:str="interesting_places",limit:int=30) ->List[Dict]:
#     """
#     Fetch POIs via OpenTripMAp.
#     kinds: comma seprated categorieas. We'll filter by interests downstream.
#     """
#     geo = bbox_from_city(city)
#     lat = geo.get("lat")
#     lon = geo.get("lon")
    
#     if lat is None or lon is None:
#         raise ValueError(f"Could not get coordinates for city: {city}. Geo response: {geo}")
    
#     params = {
#         "radius": radius_m,
#         "lon": lon,
#         "lat": lat,
#         "kinds": kinds,
#         "rate": 2,
#         "format": "json",
#         "limit": limit,
#         "apikey": OTM_KEY
#     }
#     r = requests.get(f"{BASE_URL}/radius",params=params)
#     r.raise_for_status()
#     places = r.json()
#     # Normalize keys
#     result = []
#     for p in places:
#         result.append({
#             "xid": p.get("xid"),
#             "name": p.get("name"),
#             "kinds": p.get("kinds"),
#             "lat": p.get("point", {}).get("lat"),
#             "lon": p.get("point", {}).get("lon"),
#             "dist": p.get("dist")
#         })
#     return result


import os
import requests
from typing import List, Dict, Any

OTM_KEY = os.getenv("OPENTRIPMAP_KEY")
BASE_URL = "https://api.opentripmap.com/0.1/en/places"

# City to Coordinates
def bbox_from_city(city: str) -> Dict[str, Any]:
    """
    Try to get city coordinates using:
    1. OpenStreetMap (Nominatim)
    2. Fallback: OpenTripMap /geoname endpoint
    """
    city_name = city.split(',')[0].strip() if ',' in city else city.strip()

    # ---- Try Nominatim first (more reliable globally)
    try:
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city_name, "format": "json", "limit": 1}
        headers = {"User-Agent": "AI-Travel-Agent/1.0"}
        r = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        if data and "lat" in data[0] and "lon" in data[0]:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "source": "nominatim"
            }
    except Exception as e:
        print(f"[WARN] OSM lookup failed for {city_name}: {e}")

    # ---- Fallback to OpenTripMap geoname
    try:
        r = requests.get(f"{BASE_URL}/geoname", params={"name": city_name, "apikey": OTM_KEY}, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "lat" in data and "lon" in data:
            return {
                "lat": float(data["lat"]),
                "lon": float(data["lon"]),
                "source": "opentripmap"
            }
        else:
            raise ValueError(f"Geoname lookup failed for city: {city_name}. Response: {data}")
    except Exception as e:
        raise ValueError(f"[ERROR] City coordinate lookup failed for '{city_name}': {e}")
# Fetch Attractions (with progressive broadening if nothing is found)
def fetch_attraction(
    city: str,
    radius_m: int = 10000,
    kinds: str = "interesting_places,historic,architecture,cultural,museums,natural,urban_environment,fortifications,monuments,temples,castles",
    limit: int = 30,
) -> List[Dict]:
    """
    Fetch points of interest (POIs) near a city using OpenTripMap.
    Uses fallback coordinate lookup (OSM → OpenTripMap).

    If no results are found from OpenTripMap, progressively broadens the search by:
      1) Removing the 'rate' filter
      2) Broadening 'kinds'
      3) Increasing 'radius'
      4) Final attempt without 'kinds' or 'rate'

    Final fallback: query OpenStreetMap Overpass API for common tourism/historic POIs.
    """
    geo = bbox_from_city(city)
    lat = geo.get("lat")
    lon = geo.get("lon")

    if lat is None or lon is None:
        raise ValueError(f"Could not get coordinates for city: {city}. Geo response: {geo}")

    def query(params: Dict[str, Any]) -> List[Dict]:
        try:
            r = requests.get(f"{BASE_URL}/radius", params=params, timeout=15)
            # Some combinations (e.g., invalid kinds/rate) may return 400. Treat as empty and fallback.
            r.raise_for_status()
            places = r.json() or []
        except requests.HTTPError as http_err:
            # Log-lite to stdout and continue with next attempt
            print(f"[opentripmap] HTTPError for params={params}: {http_err}")
            places = []
        except Exception as e:
            print(f"[opentripmap] Request error for params={params}: {e}")
            places = []

        out: List[Dict] = []
        for p in places:
            out.append({
                "xid": p.get("xid"),
                "name": p.get("name"),
                "kinds": p.get("kinds"),
                "lat": p.get("point", {}).get("lat"),
                "lon": p.get("point", {}).get("lon"),
                "dist": p.get("dist")
            })
        return out

    # Attempt 1: as requested (kinds + min_rate=2)
    params = {
        "radius": radius_m,
        "lon": lon,
        "lat": lat,
        "kinds": kinds,
        # some deployments prefer "min_rate" over "rate"; try this first to avoid 400s
        "min_rate": 2,
        "format": "json",
        "limit": limit,
        "apikey": OTM_KEY,
    }
    results = query(params)
    if results:
        return results

    # Attempt 2: remove rate filter
    params.pop("min_rate", None)
    params.pop("rate", None)
    results = query(params)
    if results:
        return results

    # Attempt 3: broaden kinds significantly
    params["kinds"] = "interesting_places,tourist_facilities,historic,architecture,cultural,museums,urban_environment,natural,monuments,fortifications,temples,bridges,other"
    results = query(params)
    if results:
        return results

    # Attempt 4: increase radius
    params["radius"] = max(radius_m, 20000)
    results = query(params)
    if results:
        return results

    # Attempt 5: last resort — no kinds filter
    params.pop("kinds", None)
    results = query(params)
    if results:
        return results

    # Still nothing from OpenTripMap — try Overpass (OSM) as a last resort
    try:
        osm_results = _fetch_attraction_overpass(lat, lon, radius_m=radius_m, limit=limit)
        if osm_results:
            return osm_results
    except Exception as e:
        print(f"[overpass] Fallback failed: {e}")

    # Nothing found
    return []


def _fetch_attraction_overpass(lat: float, lon: float, radius_m: int = 10000, limit: int = 30) -> List[Dict]:
    """
    Query OpenStreetMap via Overpass API for tourism/historic POIs around lat/lon.
    This is a conservative fallback when OpenTripMap has no results or errors.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    R = max(1000, min(radius_m, 30000))  # cap radius to avoid heavy queries

    q = f"""
    [out:json][timeout:25];
    (
      node(around:{R},{lat},{lon})[tourism];
      node(around:{R},{lat},{lon})[historic];
      way(around:{R},{lat},{lon})[tourism];
      way(around:{R},{lat},{lon})[historic];
      relation(around:{R},{lat},{lon})[tourism];
      relation(around:{R},{lat},{lon})[historic];
    );
    out center {limit};
    """

    r = requests.post(overpass_url, data={"data": q}, timeout=30)
    r.raise_for_status()
    data = r.json()
    elements = data.get("elements", [])

    results: List[Dict] = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or "POI"
        # Node has lat/lon, ways/relations have center
        if el.get("type") == "node":
            lat_el = el.get("lat")
            lon_el = el.get("lon")
        else:
            center = el.get("center", {})
            lat_el = center.get("lat")
            lon_el = center.get("lon")

        if lat_el is None or lon_el is None:
            continue

        kind_labels = []
        if "tourism" in tags:
            kind_labels.append(f"tourism:{tags['tourism']}")
        if "historic" in tags:
            kind_labels.append(f"historic:{tags['historic']}")

        results.append({
            "xid": f"osm:{el.get('type')}:{el.get('id')}",
            "name": name,
            "kinds": ",".join(kind_labels) if kind_labels else "osm_poi",
            "lat": lat_el,
            "lon": lon_el,
            "dist": None,
        })

        if len(results) >= limit:
            break

    return results