"""
Debug script for LangGraph Travel Agent
Run this to test your graph step-by-step
"""
from graph import trip_graph
from model import TravelState
import json
from dotenv import load_dotenv

load_dotenv()

def debug_graph():
    """Run the graph with debug output"""
    
    # Test state
    initial_state = TravelState(
        city="Paris",
        days=2,
        interests=["culture", "food"],
        budget="medium"
    )
    
    print("="*60)
    print("INITIAL STATE")
    print("="*60)
    print(f"City: {initial_state.city}")
    print(f"Days: {initial_state.days}")
    print(f"Interests: {initial_state.interests}")
    print(f"Budget: {initial_state.budget}")
    print("\n")
    
    print("="*60)
    print("STARTING GRAPH EXECUTION")
    print("="*60)
    
    # Run the graph with streaming to see each step
    try:
        for i, step in enumerate(trip_graph.stream(initial_state.dict())):
            print(f"\n--- Step {i+1} ---")
            for node_name, node_output in step.items():
                print(f"Node: {node_name}")
                
                # Print key information from each node
                if isinstance(node_output, dict):
                    if "error" in node_output:
                        print(f"  ❌ ERROR: {node_output['error']}")
                    if "status" in node_output:
                        print(f"  ✅ Status: {node_output['status']}")
                    
                    # Print specific fields based on node
                    if "plan_outline" in node_output:
                        print(f"  📋 Plan outline created")
                    if "attractions" in node_output or "attraction" in node_output:
                        attractions = node_output.get("attractions") or node_output.get("attraction")
                        print(f"  🎯 Attractions found: {len(attractions) if attractions else 0}")
                    if "weather_data" in node_output:
                        print(f"  🌤️ Weather data retrieved")
                    if "route_plan" in node_output:
                        print(f"  🗺️ Route plan created")
                    if "itinerary_text" in node_output:
                        text = node_output["itinerary_text"]
                        print(f"  📄 Itinerary text: {len(text)} chars")
                    if "itinerary_pdf_bytes" in node_output:
                        print(f"  📑 PDF generated")
            print("-" * 60)
        
        print("\n" + "="*60)
        print("GRAPH EXECUTION COMPLETED")
        print("="*60)
        
        # Get final state
        final_state = trip_graph.invoke(initial_state.dict())
        
        print("\nFINAL STATE SUMMARY:")
        print(f"  Plan outline: {'✅' if final_state.get('plan_outline') else '❌'}")
        print(f"  Attractions: {'✅' if final_state.get('attractions') or final_state.get('attraction') else '❌'}")
        print(f"  Weather data: {'✅' if final_state.get('weather_data') else '❌'}")
        print(f"  Route plan: {'✅' if final_state.get('route_plan') else '❌'}")
        print(f"  Itinerary text: {'✅' if final_state.get('itinerary_text') else '❌'}")
        print(f"  PDF bytes: {'✅' if final_state.get('itinerary_pdf_bytes') else '❌'}")
        
        if final_state.get("error"):
            print(f"\n❌ FINAL ERROR: {final_state['error']}")
        else:
            print("\n✅ SUCCESS: All steps completed")
            
            if final_state.get('itinerary_text'):
                print("\n" + "="*60)
                print("GENERATED ITINERARY")
                print("="*60)
                print(final_state['itinerary_text'])
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ EXCEPTION DURING EXECUTION: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_graph()
