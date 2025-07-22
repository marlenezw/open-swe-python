"""State management for the agent system."""

from typing import List, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state across all agents."""
    
    messages: List[BaseMessage]
    current_request: str
    plan: Optional[str]
    code_changes: List[dict]  
    status: Literal["planning", "programming", "complete", "error"]
    next_agent: Optional[str]
    iteration_count: int
    created_files: List[str]
    error_message: Optional[str]