"""Router Agent — classifies user intent and sets the route in AgentState."""

from langchain_core.messages import HumanMessage
from agents.state import AgentState
from services.llm import get_llm

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for a Citizen Services Chatbot that answers questions about Indian Government schemes.

Given the user's query, classify it into ONE of these categories:
- "rag" — if the query is about a government scheme, policy, benefits, documents required, or application process and can likely be answered from stored documents.
- "web" — if the query asks for latest news, current events, real-time information, or something that likely needs a web search.
- "eligibility" — if the query specifically asks whether someone is eligible for a scheme, or asks to check eligibility based on criteria like age, income, caste, state, etc.

Reply with ONLY the single word: rag, web, or eligibility. Nothing else."""


def router_node(state: AgentState) -> AgentState:
    """Classify query intent and populate state['route']."""
    llm = get_llm(state.get("model"))
    query = state["query"]

    response = llm.invoke([
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ])

    content = getattr(response, "content", response)
    route = content.strip().lower()
    if route not in ("rag", "web", "eligibility"):
        route = "rag"  # default fallback

    return {**state, "route": route}
