import os
import google.generativeai as genai
from config.settings import GEMINI_API_KEY

class GeminiService:
    """
    Service wrapper for Google Gemini API.
    Handles authentication, models setup, and queries execution.
    """
    def __init__(self):
        # Configure Gemini API key from settings or environment directly
        self.api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = "gemini-1.5-flash"
        self.is_configured = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.is_configured = True
            except Exception as e:
                self.is_configured = False
                
    def generate_text(self, prompt: str, system_instruction: str = None, temperature: float = 0.2) -> str:
        """
        Generates text based on prompt and system instructions.
        Uses low temperature (0.2) for predictable, analytical financial text.
        """
        if not self.is_configured:
            return (
                "⚠️ Gemini API is not configured. Please supply a valid `GEMINI_API_KEY` "
                "in your `.env` file to enable GenAI recovery features."
            )
            
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": temperature},
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini API Call failed: {str(e)}"
            
    def get_embeddings(self, text: str) -> list:
        """
        Retrieves embedding vector (768 dimensions) using Gemini's embedding service.
        Useful for RAG indexing and search.
        """
        if not self.is_configured:
            raise ValueError("Gemini API is not configured.")
        try:
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return response["embedding"]
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")
