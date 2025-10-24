from model import TravelState
from typing import Dict, Any
from src.utils.osrm_client import compute_route_order

def route_node(state:TravelState)->Dict[str,Any]:
    if not state.attractions:
        return {'error':"route: no attractions"}
    
    try:
        coords=[]
        for p in state.attractions:
            coords.append({
                "lat":p.get("lat"),
                "lon": p.get("lon")
            })
        route = compute_route_order(coords)
        return {'route_plan':route, "status":"Route_completed"}
    except Exception as e:
        return {'error':f"route-node error {e}"}
        
        
    
    
    