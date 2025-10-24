from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DayPlan(BaseModel):
    day: int
    theme: str
    activities: List[str]
    descriptions: Optional[str] = None

class TravelState(BaseModel):
    # Inputs
    user_id: Optional[str] = None
    city: Optional[str] = None
    days: Optional[int] = None
    interests: Optional[List[str]] = None
    budget: Optional[str] = None

    # Planner output
    plan_outline: Optional[Dict[str, Any]] = None

    # Data fetched
    attractions: Optional[List[Dict[str, Any]]] = None
    weather_data: Optional[Dict[str, Any]] = None
    route_plan: Optional[List[Dict[str, Any]]] = None

    # Final outputs
    itinerary_text: Optional[str] = None
    itinerary_pdf_bytes: Optional[bytes] = None

    # Memory & meta
    user_memory: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None

    status: Optional[str] = "initialized"
    error: Optional[str] = None