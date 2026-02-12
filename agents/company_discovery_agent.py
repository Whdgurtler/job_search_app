"""Agent for discovering companies by employment area or sector."""
from typing import Dict

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus
from company_discovery import CompanyDiscovery


class CompanyDiscoveryAgent(BaseAgent):
    """Use curated data and optional LLM expansion to build company lists."""

    def __init__(self, llm=None):
        super().__init__("CompanyDiscoveryAgent", llm)
        self.discovery = CompanyDiscovery(llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        self.status = AgentStatus.RUNNING
        payload: Dict = message.data or {}

        employment_area = (
            payload.get("employment_area")
            or context.employment_area
            or context.company_name
            or ""
        ).strip()
        filters: Dict = payload.get("filters") or context.company_filters or {}
        max_companies = int(payload.get("max_companies", 25))
        use_llm = bool(payload.get("use_llm", False))

        if not employment_area:
            error_msg = "employment_area is required to discover companies"
            self.log(error_msg)
            self.status = AgentStatus.FAILED
            return self._create_response(
                "orchestrator",
                "discovery_failed",
                status=AgentStatus.FAILED,
                error=error_msg,
            )

        try:
            companies = self.discovery.discover_companies(
                sector=employment_area,
                characteristics=filters if filters else None,
                max_companies=max_companies,
                use_llm=use_llm,
            )
        except Exception as exc:
            error_msg = f"Company discovery failed: {exc}"
            self.log(error_msg)
            self.status = AgentStatus.FAILED
            return self._create_response(
                "orchestrator",
                "discovery_failed",
                status=AgentStatus.FAILED,
                error=error_msg,
            )

        context.employment_area = employment_area
        context.company_filters = filters
        context.company_list = companies

        if not companies:
            error_msg = f"No companies found for employment area '{employment_area}'"
            self.log(error_msg)
            self.status = AgentStatus.FAILED
            return self._create_response(
                "orchestrator",
                "no_companies_found",
                {
                    "employment_area": employment_area,
                    "filters": filters,
                    "max_companies": max_companies,
                },
                AgentStatus.FAILED,
                error_msg,
            )

        self.status = AgentStatus.SUCCESS
        return self._create_response(
            "orchestrator",
            "companies_discovered",
            {
                "companies": companies,
                "employment_area": employment_area,
                "filters": filters,
                "max_companies": max_companies,
                "use_llm": use_llm,
            },
            AgentStatus.SUCCESS,
        )
