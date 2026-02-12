# Multi-Agent Job Scraper Architecture
"""
Multi-Agent Job Scraper

A modular architecture with specialized agents:
0. CompanyDiscoveryAgent - Builds company lists for a target employment area
1. CareerFinderAgent - Finds company career page URLs
2. PageAnalyzerAgent - Analyzes page structure and creates navigation plan
3. NavigatorAgent - Navigates pages using Selenium (headless)
4. ScraperAgent - Extracts job postings from HTML
5. VerifierAgent - Verifies scrape quality, triggers re-analysis if needed
6. MatcherAgent - Matches jobs to resume based on skills/level

Usage:
    from agents import create_job_scraper

    scraper = create_job_scraper(use_local_llm=True, headless=True)
    result = scraper.search_jobs(
        company_name="Block",
        keywords="Data Scientist",
        resume_data={"skills": ["python", "machine learning"]}
    )

    for job in result.matched_jobs:
        print(f"{job['title']} - {job['match_result']['match_score']}%")
"""

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus
from .company_discovery_agent import CompanyDiscoveryAgent
from .career_finder_agent import CareerFinderAgent
from .page_analyzer_agent import PageAnalyzerAgent
from .navigator_agent import NavigatorAgent
from .scraper_agent import ScraperAgent
from .verifier_agent import VerifierAgent
from .review_agent import ReviewAgent
from .matcher_agent import MatcherAgent
from .orchestrator import JobScraperOrchestrator, create_job_scraper, OrchestratorResult

__all__ = [
    # Base classes
    'BaseAgent',
    'AgentContext',
    'AgentMessage',
    'AgentStatus',
    # Agents
    'CompanyDiscoveryAgent',
    'CareerFinderAgent',
    'PageAnalyzerAgent',
    'NavigatorAgent',
    'ScraperAgent',
    'VerifierAgent',
    'ReviewAgent',
    'MatcherAgent',
    # Orchestrator
    'JobScraperOrchestrator',
    'OrchestratorResult',
    # Factory
    'create_job_scraper',
]
