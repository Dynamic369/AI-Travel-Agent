"""
Visualize the LangGraph structure
"""
from graph import trip_graph

def visualize_graph():
    """Print the graph structure"""
    print("="*60)
    print("AI TRAVEL AGENT - GRAPH STRUCTURE")
    print("="*60)
    
    print("\nGraph Flow:")
    print("  START")
    print("    ↓")
    print("  planner")
    print("    ↓")
    print("  attraction")
    print("    ↓")
    print("  weather")
    print("    ↓")
    print("  route")
    print("    ↓")
    print("  summarizer")
    print("    ↓")
    print("  reporter")
    print("    ↓")
    print("  END")
    
    print("\n" + "="*60)
    print("NODE DESCRIPTIONS")
    print("="*60)
    
    nodes_info = {
        "planner": {
            "description": "Creates structured travel plan using LLM",
            "input": "city, days, interests, budget",
            "output": "plan_outline (JSON)",
            "api": "Groq LLM"
        },
        "attraction": {
            "description": "Fetches points of interest",
            "input": "city, plan_outline, interests",
            "output": "attractions (list)",
            "api": "OpenTripMap"
        },
        "weather": {
            "description": "Gets weather forecast",
            "input": "city, days",
            "output": "weather_data (dict)",
            "api": "Open-Meteo"
        },
        "route": {
            "description": "Optimizes route between attractions",
            "input": "attractions",
            "output": "route_plan (dict)",
            "api": "OSRM"
        },
        "summarizer": {
            "description": "Generates human-readable itinerary",
            "input": "plan_outline",
            "output": "itinerary_text (string)",
            "api": "Groq LLM"
        },
        "reporter": {
            "description": "Converts itinerary to PDF",
            "input": "itinerary_text, city, days",
            "output": "itinerary_pdf_bytes (bytes)",
            "api": "ReportLab"
        }
    }
    
    for node_name, info in nodes_info.items():
        print(f"\n{node_name.upper()}")
        print(f"  Description: {info['description']}")
        print(f"  Input:       {info['input']}")
        print(f"  Output:      {info['output']}")
        print(f"  API/Tool:    {info['api']}")
    
    print("\n" + "="*60)
    print("STATE FIELDS")
    print("="*60)
    print("""
Inputs:
  - user_id: Optional[str]
  - city: str
  - days: int
  - interests: List[str]
  - budget: str

Intermediate:
  - plan_outline: Dict
  - attractions: List[Dict]
  - weather_data: Dict
  - route_plan: Dict

Outputs:
  - itinerary_text: str
  - itinerary_pdf_bytes: bytes

Meta:
  - status: str
  - error: str
  - user_memory: Dict
  - recommendations: List[str]
    """)
    
    # Try to get the graph representation
    try:
        print("="*60)
        print("GRAPH ASCII REPRESENTATION")
        print("="*60)
        graph = trip_graph.get_graph()
        print(graph.draw_ascii())
    except Exception as e:
        print(f"Could not draw ASCII graph: {e}")

if __name__ == "__main__":
    visualize_graph()
