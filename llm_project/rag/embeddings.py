"""Embeddings configuration — uses Google Generative AI embeddings."""

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a configured embedding model instance."""
    model_name = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    return GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
