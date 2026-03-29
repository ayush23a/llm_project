"""Scheme tools — domain-specific tools for Indian Government scheme queries.

These tools use a combination of RAG retrieval and structured lookup.
In production, these would query a dedicated schemes database.
For now, they use the RAG vector store as their data source.
"""

from rag.retriever import get_retriever


def _retrieve_for_tool(query: str, prefix: str = "") -> str:
    """Helper: retrieve top docs and format them for tool output."""
    try:
        retriever = get_retriever(k=3)
        docs = retriever.invoke(f"{prefix} {query}".strip())
        if not docs:
            return "No information found in the knowledge base for this query."
        return "\n\n".join(
            f"[{i+1}] {doc.page_content}" for i, doc in enumerate(docs)
        )
    except Exception as e:
        return f"Tool error: {str(e)}"


def scheme_search(query: str) -> str:
    """Search for government schemes matching the query."""
    return _retrieve_for_tool(query, prefix="government scheme")


def eligibility_checker(query: str) -> str:
    """Check eligibility criteria for a scheme based on the query."""
    return _retrieve_for_tool(query, prefix="eligibility criteria requirements")


def documents_required(query: str) -> str:
    """List documents required for a scheme application."""
    return _retrieve_for_tool(query, prefix="documents required for application")


def application_steps(query: str) -> str:
    """Get step-by-step application process for a scheme."""
    return _retrieve_for_tool(query, prefix="application process steps how to apply")


def benefits_info(query: str) -> str:
    """Get information about benefits provided by a scheme."""
    return _retrieve_for_tool(query, prefix="benefits amount financial assistance")


def nearest_center(query: str) -> str:
    """Find the nearest service center or office for a scheme."""
    return _retrieve_for_tool(query, prefix="nearest center office CSC location")
