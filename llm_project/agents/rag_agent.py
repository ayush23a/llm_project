"""RAG Agent — retrieves context from the vector store and generates an answer."""

from agents.state import AgentState
from rag.retriever import get_retriever
from services.llm import get_llm

RAG_SYSTEM_PROMPT = """You are a Citizen Services Assistant for Indian Government schemes.
Use ONLY the provided context to answer the user's question.
If the context does not contain the answer, say "I don't have enough information about this in my knowledge base."

Always:
- Cite the source document when available.
- Format your answer clearly with bullet points or numbered steps where appropriate.
- Be specific about eligibility criteria, benefits, required documents, and application steps.

Context:
{context}
"""


def rag_node(state: AgentState) -> AgentState:
    """Retrieve relevant chunks and generate a grounded answer."""
    query = state["query"]
    retriever = get_retriever()

    docs = retriever.invoke(query)

    context_parts = []
    sources = []
    for i, doc in enumerate(docs):
        context_parts.append(f"[{i+1}] {doc.page_content}")
        sources.append({
            "chunk_index": i + 1,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", None),
            "content_preview": doc.page_content[:200],
        })

    if not context_parts:
        # No relevant documents found -> trigger web fallback
        return {
            **state,
            "fallback_to_web": True,
            "route": "web", # Prevents "Knowledge Base" UI badge
        }

    context = "\n\n".join(context_parts)
    llm = get_llm(state.get("model"))
    response = llm.invoke([
        {"role": "system", "content": RAG_SYSTEM_PROMPT.format(context=context)},
        {"role": "user", "content": query},
    ])
    
    answer = getattr(response, "content", response)
    
    # If the LLM indicates the context lacks the answer, trigger web fallback
    if "don't have enough information" in answer.lower() or "do not have enough information" in answer.lower():
        return {
            **state,
            "fallback_to_web": True,
            "route": "web",
        }

    return {
        **state,
        "context": context,
        "sources": sources,
        "final_answer": answer,
        "fallback_to_web": False,
    }
