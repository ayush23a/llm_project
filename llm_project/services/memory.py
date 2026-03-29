"""Conversation memory service — manages per-session message history."""

from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class ConversationMemory:
    """Simple in-memory conversation store keyed by session_id."""

    def __init__(self, max_history: int = 20):
        self._store: Dict[str, List[BaseMessage]] = {}
        self._max_history = max_history

    def get_history(self, session_id: str) -> List[BaseMessage]:
        """Return message history for a session."""
        return self._store.get(session_id, [])

    def add_user_message(self, session_id: str, content: str) -> None:
        """Append a user message to the session history."""
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append(HumanMessage(content=content))
        self._trim(session_id)

    def add_ai_message(self, session_id: str, content: str) -> None:
        """Append an AI message to the session history."""
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append(AIMessage(content=content))
        self._trim(session_id)

    def clear(self, session_id: str) -> None:
        """Clear history for a session."""
        self._store.pop(session_id, None)

    def _trim(self, session_id: str) -> None:
        """Keep only the last max_history messages."""
        if len(self._store[session_id]) > self._max_history:
            self._store[session_id] = self._store[session_id][-self._max_history:]


# Singleton instance
memory = ConversationMemory()
