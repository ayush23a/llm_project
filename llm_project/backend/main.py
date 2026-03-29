"""Citizen Services Chatbot — FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

# Ensure API key is available
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

app = FastAPI(
    title="Citizen Services Chatbot API",
    description=(
        "Agentic Hybrid RAG system for Indian Government schemes. "
        "Features LangGraph workflow with Router → RAG / Web / Eligibility agents, "
        "document ingestion, web search, and conversation memory."
    ),
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "Citizen Services Chatbot",
        "version": "2.0.0",
        "endpoints": ["/chat", "/ingest", "/schemes", "/eligibility", "/docs"],
    }


# Import and include routes
from backend.routes import router
app.include_router(router, prefix="/api")
