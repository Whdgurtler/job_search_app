"""
Base Agent class for the multi-agent job scraper architecture.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_RETRY = "needs_retry"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    recipient: str
    action: str
    data: Dict[str, Any] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "action": self.action,
            "data": self.data,
            "status": self.status.value,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, d: Dict) -> 'AgentMessage':
        return cls(
            sender=d["sender"],
            recipient=d["recipient"],
            action=d["action"],
            data=d.get("data", {}),
            status=AgentStatus(d.get("status", "idle")),
            error=d.get("error")
        )


@dataclass
class AgentContext:
    """Shared context between agents."""
    company_name: str = ""
    career_url: str = ""
    employment_area: str = ""
    company_filters: Dict = field(default_factory=dict)
    company_list: List[str] = field(default_factory=list)
    keywords: str = ""
    location: str = ""
    resume_data: Dict = field(default_factory=dict)
    page_html: str = ""
    page_structure: Dict = field(default_factory=dict)
    navigation_plan: Dict = field(default_factory=dict)
    raw_jobs: list = field(default_factory=list)
    verified_jobs: list = field(default_factory=list)
    matched_jobs: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    intercepted_api_data: list = field(default_factory=list)
    retry_strategy: str = ""
    ats_platform: str = ""
    page_diagnosis: str = ""
    known_job_urls: set = field(default_factory=set)
    known_job_keys: set = field(default_factory=set)


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent architecture.

    Each agent has a specific responsibility and communicates
    through messages with other agents via the orchestrator.
    """

    def __init__(self, name: str, llm=None):
        self.name = name
        self.llm = llm
        self.status = AgentStatus.IDLE
        self.last_error: Optional[str] = None

    @abstractmethod
    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """
        Execute the agent's task.

        Args:
            context: Shared context with all relevant data
            message: Input message from orchestrator or another agent

        Returns:
            AgentMessage with results or error
        """
        pass

    def _create_response(
        self,
        recipient: str,
        action: str,
        data: Dict = None,
        status: AgentStatus = AgentStatus.SUCCESS,
        error: str = None
    ) -> AgentMessage:
        """Helper to create a response message."""
        return AgentMessage(
            sender=self.name,
            recipient=recipient,
            action=action,
            data=data or {},
            status=status,
            error=error
        )

    def _call_llm(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Call the LLM for analysis tasks."""
        if not self.llm:
            return None
        try:
            return self.llm.analyze(prompt, max_tokens=max_tokens)
        except Exception as e:
            self.last_error = str(e)
            return None

    def log(self, message: str):
        """Log a message with agent name prefix."""
        print(f"[{self.name}] {message}")
