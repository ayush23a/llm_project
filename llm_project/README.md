# 🇮🇳 Citizen Services Chatbot

> Agentic Hybrid RAG system for Indian Government schemes — powered by LangGraph, ChromaDB, and multi-LLM support.

## Architecture

```
User Query → FastAPI → LangGraph StateGraph
                              │
                        ┌─────┴─────┐
                        │  Router   │
                        │  Agent    │
                        └─────┬─────┘
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ┌──────────┐ ┌──────┐ ┌────────────┐
              │RAG Agent │ │ Web  │ │Eligibility │
              │(ChromaDB)│ │Agent │ │   Agent    │
              └──────────┘ └──────┘ └────────────┘
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                      Structured JSON
                        Response
```

## Project Structure

```
llm_project/
├── backend/
│   ├── main.py          # FastAPI entrypoint
│   ├── routes.py        # /chat, /ingest, /schemes, /eligibility
│   └── schema.py        # Pydantic models
├── agents/
│   ├── state.py         # AgentState TypedDict
│   ├── graph.py         # LangGraph StateGraph
│   ├── router_agent.py  # Intent classifier
│   ├── rag_agent.py     # Vector search + answer
│   ├── web_agent.py     # Tavily/DDG search
│   └── eligibility_agent.py
├── rag/
│   ├── embeddings.py    # Google embeddings
│   ├── ingest.py        # PDF/TXT/URL ingestion
│   └── retriever.py     # ChromaDB retriever
├── tools/
│   ├── web_search.py    # Tavily + DuckDuckGo
│   └── scheme_tools.py  # 6 domain tools
├── services/
│   ├── llm.py           # Multi-LLM factory
│   └── memory.py        # Conversation memory
├── vector_db/           # ChromaDB storage
├── data/schemes/        # Sample scheme data
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env
└── requirements.txt
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
cp .env.example .env  # Edit with your API keys

# 3. Run the server
uvicorn backend.main:app --reload --port 8000

# 4. Ingest sample data
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@data/schemes/sample_schemes.txt"

# 5. Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is PM Kisan scheme?", "session_id": "test"}'
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat` | POST | Main chat — routes through LangGraph |
| `/api/ingest` | POST | Upload PDF/TXT or pass URL |
| `/api/ingest/url` | POST | Ingest via JSON body URL |
| `/api/schemes` | GET | Search schemes |
| `/api/eligibility` | POST | Direct eligibility check |

## Docker

```bash
cd docker
docker-compose up --build
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Google AI API key |
| `TAVILY_API_KEY` | No | Tavily search API key |
| `LLM_MODEL` | No | Default LLM (default: `gemini-2.0-flash`) |
| `LLM_TEMPERATURE` | No | Temperature (default: `0.3`) |
| `CHROMA_PERSIST_DIR` | No | ChromaDB path |
| `EMBEDDING_MODEL` | No | Embedding model name |
