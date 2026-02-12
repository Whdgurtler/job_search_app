"""
Orchestrator: Coordinates all agents in the multi-agent job scraper.
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .base_agent import AgentContext, AgentMessage, AgentStatus
from .company_discovery_agent import CompanyDiscoveryAgent
import db as jobs_db
from .career_finder_agent import CareerFinderAgent
from .page_analyzer_agent import PageAnalyzerAgent
from .navigator_agent import NavigatorAgent
from .scraper_agent import ScraperAgent, JobPosting
from .verifier_agent import VerifierAgent
from .review_agent import ReviewAgent
from .matcher_agent import MatcherAgent


@dataclass
class OrchestratorResult:
    """Final result from the orchestrator."""
    success: bool
    company: str
    jobs_found: int
    matched_jobs: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    agent_log: List[str] = field(default_factory=list)


class JobScraperOrchestrator:
    """
    Coordinates the multi-agent job scraping workflow.

    Workflow:
    0. (Optional) CompanyDiscoveryAgent -> Build company lists by employment area
    1. CareerFinderAgent -> Find career page URL
    2. NavigatorAgent -> Load page (initial)
    3. PageAnalyzerAgent -> Analyze page structure
    4. NavigatorAgent -> Navigate based on analysis
    5. ScraperAgent -> Extract jobs
    6. VerifierAgent -> Verify results (may loop back to step 3)
    7. MatcherAgent -> Match jobs to resume

    The orchestrator handles:
    - Agent initialization with shared LLM
    - Message passing between agents
    - Retry logic when verification fails
    - Error handling and logging
    """

    def __init__(self, llm=None, headless: bool = True):
        """
        Initialize the orchestrator with all agents.

        Args:
            llm: Shared LLM instance for all agents
            headless: Whether to run browser in headless mode
        """
        self.llm = llm
        self.headless = headless

        # Initialize agents
        self.company_discovery = CompanyDiscoveryAgent(llm)
        self.career_finder = CareerFinderAgent(llm)
        self.page_analyzer = PageAnalyzerAgent(llm)
        self.navigator = NavigatorAgent(llm, headless=headless)
        self.scraper = ScraperAgent(llm)
        self.verifier = VerifierAgent(llm)
        self.review = ReviewAgent(llm)
        self.matcher = MatcherAgent(llm)

        self.log_entries: List[str] = []

    def search_jobs(
        self,
        company_name: str,
        keywords: str = "",
        location: str = "",
        resume_data: Dict = None
    ) -> OrchestratorResult:
        """
        Execute the full job search workflow.

        Args:
            company_name: Company to search
            keywords: Job keywords to filter (e.g., "Data Scientist")
            location: Location filter (optional)
            resume_data: Resume data for matching (optional)

        Returns:
            OrchestratorResult with jobs and metadata
        """
        start_time = time.time()
        self.log_entries = []

        self._log(f"Starting job search for {company_name}")
        if keywords:
            self._log(f"Keywords: {keywords}")

        # Initialize context
        context = AgentContext(
            company_name=company_name,
            keywords=keywords,
            location=location,
            resume_data=resume_data or {}
        )

        try:
            # Step 1: Find career page
            self._log("Step 1: Finding career page...")
            result = self._execute_agent(
                self.career_finder,
                context,
                AgentMessage("orchestrator", "CareerFinderAgent", "find_career_page")
            )

            if result.status == AgentStatus.FAILED:
                return self._create_error_result(
                    company_name,
                    f"Could not find career page: {result.error}",
                    start_time
                )

            career_url = result.data.get("career_url", "")
            self._log(f"Found career page: {career_url}")

            # Step 2: Initial page load
            self._log("Step 2: Loading career page...")
            context.navigation_plan = {"steps": [{"action": "wait_for_js", "timeout": 15000}]}
            nav_result = self._execute_agent(
                self.navigator,
                context,
                AgentMessage("orchestrator", "NavigatorAgent", "load_page")
            )

            if nav_result.status == AgentStatus.FAILED:
                return self._create_error_result(
                    company_name,
                    f"Failed to load page: {nav_result.error}",
                    start_time
                )

            # Get initial HTML
            context.page_html = self.navigator.get_page_html()

            # Step 3: Analyze page structure
            self._log("Step 3: Analyzing page structure...")
            analysis_result = self._execute_agent(
                self.page_analyzer,
                context,
                AgentMessage("orchestrator", "PageAnalyzerAgent", "analyze")
            )

            if analysis_result.status == AgentStatus.FAILED:
                self._log(f"Analysis warning: {analysis_result.error}")
                # Continue with basic scraping

            page_structure = analysis_result.data.get("page_structure", {})
            self._log(f"Pagination: {page_structure.get('pagination_type', 'unknown')}")
            self._log(f"Estimated jobs: {page_structure.get('estimated_total_jobs', 'unknown')}")

            # Step 4: Navigate based on analysis
            self._log("Step 4: Navigating career page...")
            nav_result = self._execute_agent(
                self.navigator,
                context,
                AgentMessage("orchestrator", "NavigatorAgent", "navigate")
            )

            if nav_result.status == AgentStatus.FAILED:
                self._log(f"Navigation warning: {nav_result.error}")

            pages_collected = nav_result.data.get("pages_collected", 1)
            self._log(f"Collected {pages_collected} page(s)")

            # Load known jobs for this company (for dedup / early exit)
            try:
                context.known_job_urls = jobs_db.get_known_job_urls(company_name)
                context.known_job_keys = jobs_db.get_known_job_keys(company_name)
                known_count = len(context.known_job_urls) + len(context.known_job_keys)
                if known_count:
                    self._log(f"Loaded {known_count} known jobs for dedup")
            except Exception as e:
                self._log(f"Could not load known jobs: {e}")

            # Step 5: Scrape ALL job titles
            self._log("Step 5: Scraping all job titles...")
            scrape_result = self._execute_agent(
                self.scraper,
                context,
                AgentMessage("orchestrator", "ScraperAgent", "scrape", nav_result.data)
            )

            if scrape_result.status == AgentStatus.FAILED:
                return self._create_error_result(
                    company_name,
                    f"Scraping failed: {scrape_result.error}",
                    start_time
                )

            total_jobs = scrape_result.data.get("jobs_count", 0)
            self._log(f"Scraped {total_jobs} total job titles")

            # Log new vs already-known jobs
            if context.known_job_urls or context.known_job_keys:
                new_count = 0
                known_count = 0
                for j in context.raw_jobs:
                    j_url = j.get("url", "")
                    j_key = f"{j.get('title', '')}|||{j.get('location', '')}"
                    if j_url and j_url in context.known_job_urls:
                        known_count += 1
                    elif not j_url and j_key in context.known_job_keys:
                        known_count += 1
                    else:
                        new_count += 1
                self._log(f"  New: {new_count}, Already known: {known_count}")

            # Step 5.5: Use LLM to filter jobs by title relevance
            if keywords and context.raw_jobs:
                self._log("Step 5.5: LLM filtering by title relevance...")
                filtered_jobs = self._filter_jobs_by_title(context.raw_jobs, keywords)
                discarded = len(context.raw_jobs) - len(filtered_jobs)
                self._log(f"Kept {len(filtered_jobs)} relevant, discarded {discarded}")
                context.raw_jobs = filtered_jobs

            # Step 6: Verify results (with retry loop)
            MAX_RETRY_ATTEMPTS = 3
            for attempt in range(MAX_RETRY_ATTEMPTS + 1):
                self._log(f"Step 6: Verifying results (attempt {attempt + 1})...")
                verify_result = self._execute_agent(
                    self.verifier,
                    context,
                    AgentMessage("orchestrator", "VerifierAgent", "verify")
                )

                if verify_result.status == AgentStatus.SUCCESS:
                    verified_count = verify_result.data.get("jobs_verified", 0)
                    self._log(f"Verified {verified_count} jobs")
                    break

                if verify_result.status != AgentStatus.NEEDS_RETRY:
                    issues = verify_result.data.get("issues", [])
                    self._log(f"Verification issues: {issues}")
                    break

                if attempt >= MAX_RETRY_ATTEMPTS:
                    self._log("Max retries reached, continuing with available jobs")
                    break

                # --- Run ReviewAgent to diagnose the failure ---
                self._log("Step 6a: Diagnosing failure with ReviewAgent...")
                review_result = self._execute_agent(
                    self.review,
                    context,
                    AgentMessage("orchestrator", "ReviewAgent", "diagnose")
                )
                strategy = review_result.data.get("retry_strategy", "")
                self._log(f"Diagnosis: {context.page_diagnosis}, strategy: {strategy}")

                if strategy == "give_up":
                    self._log("ReviewAgent recommends giving up (auth wall / captcha / exhausted)")
                    break

                # --- Execute the recommended retry strategy ---

                if strategy == "use_api_data" and context.intercepted_api_data:
                    self._log("Step 6b: Extracting jobs from intercepted API data...")
                    api_jobs = self.scraper.extract_from_api_data(
                        context.intercepted_api_data, context.company_name
                    )
                    if api_jobs:
                        context.raw_jobs = [j.to_dict() for j in api_jobs]
                        self._log(f"Extracted {len(api_jobs)} jobs from API data")
                    continue  # re-verify

                if strategy == "wait_longer":
                    self._log("Step 6b: Re-navigating with longer wait...")
                    context.navigation_plan = {"steps": [{"action": "wait_for_js", "timeout": 20000}]}
                    nav_result = self._execute_agent(
                        self.navigator, context,
                        AgentMessage("orchestrator", "NavigatorAgent", "navigate")
                    )
                    context.page_html = self.navigator.get_page_html()
                    # Re-scrape with new HTML
                    scrape_result = self._execute_agent(
                        self.scraper, context,
                        AgentMessage("orchestrator", "ScraperAgent", "scrape", nav_result.data)
                    )
                    self._log(f"Re-scrape found {scrape_result.data.get('jobs_count', 0)} jobs")
                    continue  # re-verify

                if strategy == "try_ats_pattern":
                    self._log(f"Step 6b: Re-scraping with ATS pattern ({context.ats_platform})...")
                    scrape_result = self._execute_agent(
                        self.scraper, context,
                        AgentMessage("orchestrator", "ScraperAgent", "scrape",
                                     {"all_html": [context.page_html]})
                    )
                    self._log(f"ATS re-scrape found {scrape_result.data.get('jobs_count', 0)} jobs")
                    continue  # re-verify

                if strategy == "use_llm_on_raw_text":
                    self._log("Step 6b: Forcing LLM extraction on raw text...")
                    # Clear selectors so Strategies 1 & 2 yield nothing, forcing Strategy 3 (LLM)
                    context.navigation_plan["selectors"] = {}
                    scrape_result = self._execute_agent(
                        self.scraper, context,
                        AgentMessage("orchestrator", "ScraperAgent", "scrape",
                                     {"all_html": [context.page_html]})
                    )
                    self._log(f"LLM re-scrape found {scrape_result.data.get('jobs_count', 0)} jobs")
                    continue  # re-verify

                if strategy == "try_iframe":
                    self._log("Step 6b: Attempting iframe content extraction...")
                    iframe_src = review_result.data.get("diagnosis", {}).get("iframe_src", "")
                    if iframe_src:
                        # Navigate to the iframe URL directly
                        context.career_url = iframe_src
                        context.navigation_plan = {"steps": [{"action": "wait_for_js", "timeout": 15000}]}
                        nav_result = self._execute_agent(
                            self.navigator, context,
                            AgentMessage("orchestrator", "NavigatorAgent", "load_page")
                        )
                        context.page_html = self.navigator.get_page_html()
                        scrape_result = self._execute_agent(
                            self.scraper, context,
                            AgentMessage("orchestrator", "ScraperAgent", "scrape", nav_result.data)
                        )
                        self._log(f"Iframe scrape found {scrape_result.data.get('jobs_count', 0)} jobs")
                    continue  # re-verify

                # Unknown strategy — break to avoid infinite loop
                self._log(f"Unknown retry strategy '{strategy}', continuing with available jobs")
                break

            # Step 7: Match to resume (if resume provided)
            if resume_data and context.verified_jobs:
                self._log("Step 7: Matching jobs to resume...")
                match_result = self._execute_agent(
                    self.matcher,
                    context,
                    AgentMessage("orchestrator", "MatcherAgent", "match")
                )

                if match_result.status == AgentStatus.SUCCESS:
                    strong = match_result.data.get("strong_matches", 0)
                    moderate = match_result.data.get("moderate_matches", 0)
                    self._log(f"Found {strong} strong matches, {moderate} moderate matches")

            # Build final result
            execution_time = time.time() - start_time
            final_jobs = context.matched_jobs if context.matched_jobs else context.verified_jobs

            self._log(f"Completed in {execution_time:.1f}s")

            return OrchestratorResult(
                success=len(final_jobs) > 0,
                company=company_name,
                jobs_found=len(final_jobs),
                matched_jobs=final_jobs,
                errors=context.errors,
                execution_time=execution_time,
                agent_log=self.log_entries
            )

        except Exception as e:
            return self._create_error_result(
                company_name,
                str(e),
                start_time
            )

        finally:
            # Clean up browser
            self.navigator.close()

    def search_multiple_companies(
        self,
        companies: Optional[List[str]] = None,
        keywords: str = "",
        location: str = "",
        resume_data: Dict = None,
        employment_area: str = "",
        discovery_filters: Optional[Dict] = None,
        max_companies: int = 20,
        use_llm_for_discovery: bool = False
    ) -> List[OrchestratorResult]:
        """Search multiple companies or discover them by employment area."""
        resolved_companies = companies[:] if companies else []

        if not resolved_companies and employment_area:
            self._log(f"Discovering companies for employment area: {employment_area}")
            try:
                resolved_companies = self.discover_companies(
                    employment_area=employment_area,
                    filters=discovery_filters,
                    max_companies=max_companies,
                    use_llm=use_llm_for_discovery,
                    keywords=keywords,
                    location=location,
                    resume_data=resume_data,
                )
            except ValueError as exc:
                self._log(str(exc))
                return []

        if not resolved_companies:
            raise ValueError("At least one company or employment_area must be provided")

        results = []
        for company in resolved_companies:
            self._log(f"\n{'='*50}")
            self._log(f"Searching: {company}")
            self._log(f"{'='*50}")

            result = self.search_jobs(company, keywords, location, resume_data)
            results.append(result)

        return results

    def discover_companies(
        self,
        employment_area: str,
        filters: Optional[Dict] = None,
        max_companies: int = 20,
        use_llm: bool = False,
        keywords: str = "",
        location: str = "",
        resume_data: Optional[Dict] = None
    ) -> List[str]:
        """Run the discovery agent to build a company list for a sector."""
        if not employment_area:
            raise ValueError("employment_area is required for discovery")

        context = AgentContext(
            employment_area=employment_area,
            keywords=keywords,
            location=location,
            resume_data=resume_data or {},
            company_filters=filters or {},
        )

        message = AgentMessage(
            "orchestrator",
            "CompanyDiscoveryAgent",
            "discover_companies",
            {
                "employment_area": employment_area,
                "filters": filters or {},
                "max_companies": max_companies,
                "use_llm": use_llm,
            }
        )

        result = self._execute_agent(self.company_discovery, context, message)

        if result.status == AgentStatus.FAILED:
            error = result.error or f"Company discovery failed for {employment_area}"
            raise ValueError(error)

        companies = result.data.get("companies", [])
        self._log(f"Discovered {len(companies)} companies for {employment_area}")
        return companies

    def _filter_jobs_by_title(self, jobs: List[Dict], keywords: str) -> List[Dict]:
        """
        Use LLM to filter jobs by title relevance BEFORE detailed processing.
        Scrapes ALL jobs first, then uses LLM to decide which titles are relevant.
        """
        if not jobs or not keywords:
            return jobs

        if not self.llm:
            # Fallback: simple keyword matching
            keywords_lower = keywords.lower()
            return [j for j in jobs if any(
                term in j.get("title", "").lower()
                for term in keywords_lower.split()
            )]

        relevant_jobs = []
        batch_size = 30

        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            titles = [f"{idx+1}. {job.get('title', 'Unknown')}"
                     for idx, job in enumerate(batch)]

            prompt = f"""Filter job titles for relevance to: "{keywords}"

Job Titles:
{chr(10).join(titles)}

Return ONLY the numbers of RELEVANT jobs as comma-separated values.
Include direct matches and related roles (e.g., ML Engineer for Data Scientist).
Exclude completely unrelated roles.

Numbers only:"""

            try:
                response = self.llm.analyze(prompt, max_tokens=200)
                if response:
                    import re
                    numbers = re.findall(r'\d+', response)
                    indices = [int(n) - 1 for n in numbers]
                    for idx in indices:
                        if 0 <= idx < len(batch):
                            relevant_jobs.append(batch[idx])
                    self._log(f"  Batch {i//batch_size + 1}: kept {len(indices)} of {len(batch)}")
                else:
                    self._log(f"  Batch {i//batch_size + 1}: LLM returned nothing, keeping all")
                    relevant_jobs.extend(batch)
            except Exception as e:
                self._log(f"  Batch {i//batch_size + 1} error: {e}, keeping all")
                relevant_jobs.extend(batch)

        return relevant_jobs

    def _execute_agent(
        self,
        agent,
        context: AgentContext,
        message: AgentMessage
    ) -> AgentMessage:
        """Execute an agent and handle errors."""
        try:
            return agent.execute(context, message)
        except Exception as e:
            self._log(f"Agent {agent.name} error: {e}")
            return AgentMessage(
                sender=agent.name,
                recipient="orchestrator",
                action="error",
                status=AgentStatus.FAILED,
                error=str(e)
            )

    def _create_error_result(
        self,
        company: str,
        error: str,
        start_time: float
    ) -> OrchestratorResult:
        """Create an error result."""
        return OrchestratorResult(
            success=False,
            company=company,
            jobs_found=0,
            errors=[error],
            execution_time=time.time() - start_time,
            agent_log=self.log_entries
        )

    def _log(self, message: str):
        """Log a message."""
        print(f"[Orchestrator] {message}")
        self.log_entries.append(message)


def create_job_scraper(use_local_llm: bool = True, headless: bool = True):
    """
    Factory function to create a job scraper with configured LLM.

    Args:
        use_local_llm: Use local HuggingFace model (True) or API (False)
        headless: Run browser in headless mode

    Returns:
        Configured JobScraperOrchestrator
    """
    # Import LLM from existing module
    try:
        from llm_analyzer import LLMAnalyzer
        llm = LLMAnalyzer()
    except ImportError:
        print("Warning: LLMAnalyzer not found, running without LLM")
        llm = None

    return JobScraperOrchestrator(llm=llm, headless=headless)
