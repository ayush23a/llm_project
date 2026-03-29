"""LangGraph workflow — compiles the StateGraph connecting all agents."""

from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.router_agent import router_node
from agents.rag_agent import rag_node
from agents.web_agent import web_node
from agents.eligibility_agent import eligibility_node


def route_decision(state: AgentState) -> str:
    """Conditional edge: route to the correct agent based on state['route']."""
    return state.get("route", "rag")


def build_graph() -> StateGraph:
    """Build and compile the citizen services agent graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("rag_agent", rag_node)
    graph.add_node("web_agent", web_node)
    graph.add_node("eligibility_agent", eligibility_node)

    # Entry point
    graph.set_entry_point("router")

    # Conditional edges from router
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "rag": "rag_agent",
            "web": "web_agent",
            "eligibility": "eligibility_agent",
        },
    )

    def rag_decision(state: AgentState) -> str:
        """Route from RAG to Web if context was insufficient."""
        if state.get("fallback_to_web"):
            return "web_agent"
        return END

    graph.add_conditional_edges(
        "rag_agent", 
        rag_decision, 
        {"web_agent": "web_agent", END: END}
    )

    # Other agents terminate after execution
    graph.add_edge("web_agent", END)
    graph.add_edge("eligibility_agent", END)

    return graph.compile()


# Singleton compiled graph
app_graph = build_graph()
