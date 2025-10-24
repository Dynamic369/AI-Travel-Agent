from typing import Dict, Any
from model import TravelState
from src.utils.opentripmap import fetch_attraction, bbox_from_city

def attraction_node(state:TravelState) -> Dict[str,Any]:
    if not state.plan_outline or not state.city:
        return {"error": "attraction: missing plan_outline or city"}
    
    try:
        #fetch many POIs around the city
        raw_places = fetch_attraction(city=state.city,radius_m=12000, limit=60)

        # filter by interests: simple keyword match on 'kinds'
        interests = [i.lower() for i in state.interests or []]
        filtered = []
        for p in raw_places:
            kinds = p.get('kinds','')
            if any(interests in kinds for interest in interests):
                filtered.append(p)
        
        #If filtered is empty, fallback to top N places
        if not filtered:
            filtered = raw_places[:20]

        return {"attractions":filtered, "status":"attraction_completed"}
    except Exception as e:
        return {"error":f"attraction_node error:{e}"}
