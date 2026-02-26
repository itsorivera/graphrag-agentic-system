"""Agent response model for standardized agent output."""

from pydantic import BaseModel
from typing import Any, Dict, Optional


class AgentResponse(BaseModel):
    """Standardized response from an agent."""

    message: str
    thread_id: str
    metadata: Optional[Dict[str, Any]] = None
    status: str = "success"
