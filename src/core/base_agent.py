"""
Base Agent - common interface for all pipeline agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseAgent(ABC):
    """Abstract base for all workflow agents."""

    AGENT_NAME: str = "base_agent"
    VERSION: str = "0.1.0"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"awa.{self.AGENT_NAME}")

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the agent's primary task."""
        ...

    def health_check(self) -> dict:
        return {
            "agent": self.AGENT_NAME,
            "version": self.VERSION,
            "llm_connected": self.llm_client is not None,
        }
