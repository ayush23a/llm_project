"""API routes for the Citizen Services Chatbot."""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_core.messages import HumanMessage

from backend.schema import (
    ChatRequest, ChatResponse,
    IngestRequest, IngestResponse,
    EligibilityRequest, EligibilityResponse,
)
from agents.graph import app_graph
from agents.state import AgentState
from rag.ingest import ingest_documents
from tools.scheme_tools import scheme_search
from services.memory import memory

router = APIRouter()


# ──────────────────────────── /chat ────────────────────────────

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Routes query through the LangGraph workflow
    (router → rag_agent | web_agent | eligibility_agent).
    """
    # Record user message in memory
    memory.add_user_message(request.session_id, request.query)
    history = memory.get_history(request.session_id)

    # Build initial state
    initial_state: AgentState = {
        "messages": history,
        "query": request.query,
        "route": None,
        "context": None,
        "sources": None,
        "tool_output": None,
        "final_answer": None,
        "fallback_to_web": False,
        "model": request.model,
    }

    try:
        result = app_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)[:200]}")

    answer = result.get("final_answer", "I could not process your request.")
    route = result.get("route", "unknown")
    sources = result.get("sources", [])

    # Record AI response in memory
    memory.add_ai_message(request.session_id, answer)

    return ChatResponse(
        answer=answer,
        route=route,
        sources=sources,
        session_id=request.session_id,
    )


# ──────────────────────────── /ingest ────────────────────────────

@router.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_file(file: UploadFile = File(None), url: str = None):
    """
    Ingest a document (PDF/TXT) or web URL into the vector store.
    Send either a file upload or a URL query param.
    """
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".pdf", ".txt", ".md"):
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        # Save to temp file
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = ingest_documents(file_path=tmp_path)
        finally:
            os.unlink(tmp_path)

        return IngestResponse(**result)

    elif url:
        try:
            result = ingest_documents(url=url)
            return IngestResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Provide a file or url parameter.")


@router.post("/ingest/url", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_url(request: IngestRequest):
    """Ingest a web URL into the vector store (JSON body)."""
    try:
        result = ingest_documents(url=request.url)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ──────────────────────────── /schemes ────────────────────────────

@router.get("/schemes", tags=["Schemes"])
async def list_schemes(q: str = "list all government schemes"):
    """
    Search for government schemes. Pass a query string for filtered results.
    """
    results = scheme_search(q)
    return {"query": q, "results": results}


# ──────────────────────────── /eligibility ────────────────────────────

@router.post("/eligibility", response_model=EligibilityResponse, tags=["Eligibility"])
async def check_eligibility(request: EligibilityRequest):
    """
    Direct eligibility check — bypasses the router and goes straight
    to the eligibility agent.
    """
    # Build query string from structured fields
    parts = [request.query]
    if request.scheme_name:
        parts.append(f"Scheme: {request.scheme_name}")
    if request.age:
        parts.append(f"Age: {request.age}")
    if request.income:
        parts.append(f"Annual Income: {request.income}")
    if request.state:
        parts.append(f"State: {request.state}")
    if request.category:
        parts.append(f"Category: {request.category}")

    full_query = ". ".join(parts)

    initial_state: AgentState = {
        "messages": [HumanMessage(content=full_query)],
        "query": full_query,
        "route": "eligibility",
        "context": None,
        "sources": None,
        "tool_output": None,
        "final_answer": None,
        "fallback_to_web": False,
        "model": request.model,
    }

    # Run only the eligibility agent (bypass router)
    from agents.eligibility_agent import eligibility_node
    result = eligibility_node(initial_state)

    return EligibilityResponse(
        answer=result.get("final_answer", "Could not check eligibility."),
        tools_used=["scheme_search", "eligibility_checker", "documents_required",
                     "application_steps", "benefits_info", "nearest_center"],
        sources=result.get("sources", []),
    )
