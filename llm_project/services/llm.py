"""LLM service — multi-LLM factory supporting Gemini, Llama, and Gemma."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

load_dotenv()

# Pre-built model map — resolves shorthand to full model IDs
MODEL_MAP = {
    "gemini": "gemini-2.5-flash",
    "llama": "llama3.2:1b",
    "gemma": "gemma2:2b",
}


def get_llm(model_name: str = None):
    """
    Return an LLM instance based on model_name.
    Accepts shorthand ('gemini', 'llama', 'gemma') or full model IDs.
    Defaults to env var LLM_MODEL or 'gemini-2.5-flash'.
    """
    if model_name is None:
        model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")

    model_name = model_name.lower().strip()

    # Resolve shorthand names to full model IDs
    if model_name in MODEL_MAP:
        model_name = MODEL_MAP[model_name]

    temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    api_key = os.getenv("GOOGLE_API_KEY")

    if "gemini" in model_name:
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key,
        )
    elif "llama" in model_name or "gemma" in model_name:
        return OllamaLLM(
            model=model_name,
            temperature=temperature,
        )
    else:
        # Fallback to Gemini
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=temperature,
            google_api_key=api_key,
        )

