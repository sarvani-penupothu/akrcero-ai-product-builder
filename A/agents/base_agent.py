"""Base agent definition for the Akcero AI Product Builder."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Abstract base class for all agents in the product builder pipeline."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with the provided payload and return structured data."""


AgentPayload = Dict[str, Any]
AgentResponse = Dict[str, Any]
