import requests
from typing import List, Dict

OSRM_BASE = "http://router.project-osrm.org"  # public demo server, acceptable for prototyping

def compute_route_order(coords:List[Dict[str, float]]) -> Dict:
    """
    coords: list of {"lat":..., "lon":...}
    We'll use OSRM "table" or "route" to compute distances/times.
    Here we do a simple approach: call OSRM /table to get durations matrix, then do a naive TSP greedy order.
    """
    if not coords:
        return {'ordered':[], "distance":0}
    
    locs = ["{lon},{lat}".format(lat=c['lat'], lon=c['lon']) for c in coords]
    coords_str = ";".join(locs)
    r = requests.get(f"{OSRM_BASE}/table/v1/driving/{coords_str}?annotations=duration,distance")
    r.raise_for_status()
    table = r.json()
    durations = table.get("durations")

    # Naive greedy ordering starting from index 0
    n = len(coords)
    visited = [0]
    remaining = set(range(1, n))
    while remaining:
        last = visited[-1]
        next_idx = min(remaining, key=lambda x: durations[last][x] if durations[last][x] is not None else float('inf'))
        visited.append(next_idx)
        remaining.remove(next_idx)

    ordered = [coords[i] for i in visited]
    return {"ordered": ordered, "order_indices": visited}