from langgraph.graph import START,END, StateGraph
from model import TravelState
from src.agents.planner import planner_node
from src.agents.attraction import attraction_node
from src.agents.weather import weather_node
from src.agents.route import route_node
from src.agents.summarizer import summarize_node
from src.agents.reporter import reporter_node


def build_graph():
    graph = StateGraph(TravelState)
    graph.add_node("planner",planner_node)
    graph.add_node("attraction",attraction_node)
    graph.add_node("weather", weather_node)
    graph.add_node("route", route_node)
    graph.add_node("summarizer", summarize_node)
    graph.add_node("reporter", reporter_node)

    #define the edges
    graph.add_edge(START,'planner')
    graph.add_edge("planner", "attraction")
    graph.add_edge("attraction", "weather")
    graph.add_edge("weather", "route")
    graph.add_edge("route", "summarizer")
    graph.add_edge("summarizer", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()

# instantiate compiled graph for import elsewhere
trip_graph = build_graph()