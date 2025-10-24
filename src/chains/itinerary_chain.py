from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.config.config import GROQ_API_KEY


llm = ChatGroq(
                model="llama-3.1-8b-instant",
                api_key=GROQ_API_KEY,
                temperature=0.7
                    
)
itinerary_promt = ChatPromptTemplate([
    ("system","You are a helpful travel assistant. Create a day trip itinerary for {city} based on user's intereset: {interests}>Provide a brief in bullet itinerary."),
    ("human","Create a itinerary for my day trip"),
])

def generate_itinerary(city:str, interests:list[str]) ->str:
    response = llm.invoke(

        itinerary_promt.format_messages(city=city, interests=', '.join(interests))
    )
    return response.content