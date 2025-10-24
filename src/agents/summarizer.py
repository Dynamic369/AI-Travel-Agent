import json
from model import TravelState
from typing import Dict, Any
from src.utils.groq_client import GroqClient

groq = GroqClient(model='llama-3.1-8b-instant')

summarize_prompt_template = """ 
        You are a travel itinerary writer. Based on the following JSON plan:
        {plan_json}

        Create a human-readable day-by-day itinerary. Include morning/afternoon/evening suggestions.
        Return only the text.
"""

def summarize_node(state:TravelState) ->Dict[str, Any]:
    if not state.plan_outline:
        return {"error": "summarizer: missing plan-outline"}
    
    plan_json = json.dumps(state.plan_outline)
    prompt = summarize_prompt_template.format(plan_json=plan_json)

    resp_text  = groq.invoke(prompt)
    itinerary = resp_text.strip()
    return {"itinerary_text": itinerary, "status": "summarizer_completed"}

