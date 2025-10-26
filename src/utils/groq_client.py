from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from .cache import TTLCache, make_key

class GroqClient:
    def __init__(self, model: str = "llama-3-8b-8192", temperature: float = 0.0, max_tokens: int = 512):
        load_dotenv()
        self.llm = ChatGroq(
            model=model, 
            temperature=temperature, 
            max_tokens=max_tokens,
            api_key=os.getenv("GROQ_API_KEY")
        )
        # 30 min cache to avoid recomputing similar prompts
        self._cache = TTLCache(ttl_seconds=1800, max_size=256)
        self._model = model

    def invoke(self, prompt: str, max_tokens: int = 512):
        # Build messages
        messages = [
            ("system", "You are a travel planning expert assistant."),
            ("user", prompt)
        ]
        # cache lookup
        key = make_key(self._model, max_tokens, prompt)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        response = self.llm.invoke(messages)
        content = response.content
        # store
        self._cache.set(key, content)
        return content
