import json
from typing import Dict, Any
from model import TravelState
from src.utils.groq_client import GroqClient

groq = GroqClient(model='llama-3.1-8b-instant')

planner_prompt_template = """ 
    Create a structured travel itinerary for the user.

    City: {city},
    Duration (days): {days},
    Interests: {interests},
    Budget level: {budget},

    Rules:
    1) Output ONLY valid JSON.
    2) The JSON must have keys:
    "trip_overview": string,
    "days": list of objects with keys: "day" (int), "theme" (string),
        "activities" (list of string), "description" (string)
    3) Provide 2-3 activities per day, aligned to interests.
    4) Do not mention hotel/flight details.
    5) Use concise descriptions.           
"""

def planner_node(state:TravelState) ->Dict[str, Any]:
    if not state.city or not state.days or not state.interests:
        return{'error': "planner: missing required inputs(city/days/interests)"}
    
    prompt = planner_prompt_template.format(
        city= state.city,
        days=state.days,
        interests= ','.join(state.interests),
        budget = state.budget or "medium"
    )

    resp_text = groq.invoke(prompt=prompt)

    try:
        #attempt to extract json
        start = resp_text.find("{")
        end = resp_text.rfind('}') + 1 
        json_str = resp_text[start:end]
        plan = json.loads(json_str)

    except Exception as e:
        return{
            "error": f"planner: failed to parse json output- {e}",
            "llm_output": resp_text
        }
    return {"plan_outline":plan, "status":"planner_completed"}
