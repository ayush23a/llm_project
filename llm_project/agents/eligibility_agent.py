"""Eligibility Agent — uses scheme tools to check eligibility and provide info."""

from agents.state import AgentState
from tools.scheme_tools import (
    scheme_search,
    eligibility_checker,
    documents_required,
    application_steps,
    benefits_info,
    nearest_center,
)
from services.llm import get_llm

ELIGIBILITY_SYSTEM_PROMPT = """You are a Citizen Services Eligibility Checker for Indian Government schemes.
Use the tool results below to give a precise answer about the user's eligibility and related scheme information.

Tool Results:
{tool_output}

Always:
- Clearly state whether the user appears eligible or not.
- List required documents.
- Explain how to apply.
- Mention the nearest service center if available.
"""


def eligibility_node(state: AgentState) -> AgentState:
    """Run eligibility tools and synthesize response."""
    query = state["query"]

    # Run all relevant tools
    tool_outputs = []

    schemes = scheme_search(query)
    tool_outputs.append(f"**Matching Schemes:**\n{schemes}")

    eligibility = eligibility_checker(query)
    tool_outputs.append(f"**Eligibility Check:**\n{eligibility}")

    docs = documents_required(query)
    tool_outputs.append(f"**Documents Required:**\n{docs}")

    steps = application_steps(query)
    tool_outputs.append(f"**Application Steps:**\n{steps}")

    benefits = benefits_info(query)
    tool_outputs.append(f"**Benefits:**\n{benefits}")

    center = nearest_center(query)
    tool_outputs.append(f"**Nearest Center:**\n{center}")

    combined = "\n\n".join(tool_outputs)

    llm = get_llm(state.get("model"))
    response = llm.invoke([
        {"role": "system", "content": ELIGIBILITY_SYSTEM_PROMPT.format(tool_output=combined)},
        {"role": "user", "content": query},
    ])

    return {
        **state,
        "tool_output": combined,
        "sources": [{"type": "tools", "tools_used": [
            "scheme_search", "eligibility_checker", "documents_required",
            "application_steps", "benefits_info", "nearest_center"
        ]}],
        "final_answer": getattr(response, "content", response),
    }
