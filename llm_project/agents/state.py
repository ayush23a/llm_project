"""Shared LangGraph state definition for the Citizen Services Chatbot."""

from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State flowing through the LangGraph workflow."""
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    route: Optional[str]  # "rag" | "web" | "eligibility"
    context: Optional[str]
    sources: Optional[List[dict]]
    tool_output: Optional[str]
    final_answer: Optional[str]
    fallback_to_web: Optional[bool]
    model: Optional[str]
