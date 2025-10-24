from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

class GroqClient:
    def __init__(self, model: str = "llama-3-8b-8192", temperature: float = 0.0, max_tokens: int = 512):
        load_dotenv()
        self.llm = ChatGroq(
            model=model, 
            temperature=temperature, 
            max_tokens=max_tokens,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def invoke(self, prompt: str, max_tokens: int = 512):
        # Build messages
        messages = [
            ("system", "You are a travel planning expert assistant."),
            ("user", prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content
