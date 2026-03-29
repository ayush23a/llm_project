"""Web Agent — performs real-time web search and synthesizes an answer."""

from agents.state import AgentState
from tools.web_search import tavily_search, duckduckgo_search
from services.llm import get_llm

WEB_SYSTEM_PROMPT = """You are a Citizen Services Assistant for Indian Government schemes.
Use the web search results below to answer the user's question.
Always cite the source URLs.

Web Search Results:
{results}
"""


def web_node(state: AgentState) -> AgentState:
    """Execute web search and generate answer from results."""
    query = state["query"]

    # Try Tavily first, fallback to DuckDuckGo
    results, sources = tavily_search(query)
    if not results:
        results, sources = duckduckgo_search(query)

    results_text = results if results else "No web results found."

    llm = get_llm(state.get("model"))
    response = llm.invoke([
        {"role": "system", "content": WEB_SYSTEM_PROMPT.format(results=results_text)},
        {"role": "user", "content": query},
    ])

    return {
        **state,
        "route": "web",
        "context": results_text,
        "sources": sources,
        "final_answer": getattr(response, "content", response),
    }
