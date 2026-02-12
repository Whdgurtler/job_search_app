"""
Agent 1: Career Page Finder
Responsible for finding the career page URL for a given company.
"""
import requests
from typing import Optional, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus


class CareerFinderAgent(BaseAgent):
    """
    Finds the career/jobs page URL for a given company.

    Strategies:
    1. Try common career page URL patterns
    2. Search company website for career links
    3. Use web search to find career page
    4. Use LLM to analyze search results
    """

    # Common career page URL patterns
    CAREER_PATTERNS = [
        "/careers",
        "/jobs",
        "/career",
        "/join-us",
        "/work-with-us",
        "/opportunities",
        "/positions",
        "/openings",
        "/hiring",
        "/careers/",
        "/jobs/",
    ]

    # Known company career URLs (cache)
    KNOWN_CAREER_URLS = {
        "block": "https://boards.greenhouse.io/block",
        "square": "https://boards.greenhouse.io/block",
        "airbnb": "https://careers.airbnb.com/positions/",
        "google": "https://careers.google.com/jobs/",
        "meta": "https://www.metacareers.com/jobs",
        "facebook": "https://www.metacareers.com/jobs",
        "amazon": "https://www.amazon.jobs/",
        "apple": "https://jobs.apple.com/",
        "microsoft": "https://careers.microsoft.com/",
        "netflix": "https://jobs.netflix.com/",
        "stripe": "https://stripe.com/jobs",
        "openai": "https://openai.com/careers",
        "anthropic": "https://www.anthropic.com/careers",
        # Banking
        "jpmorgan chase": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions",
        "jpmorgan": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions",
        "bank of america": "https://careers.bankofamerica.com/en-us/search-results",
        "wells fargo": "https://www.wellsfargojobs.com/en/jobs/",
        "citigroup": "https://jobs.citi.com/search-jobs",
        "citi": "https://jobs.citi.com/search-jobs",
        "goldman sachs": "https://higher.gs.com/roles",
        "morgan stanley": "https://morganstanley.tal.net/vx/lang-en-GB/mobile-0/brand-2/xf-53616c7465645f5f/candidate/jobboard/vacancy/1/adv/",
        "capital one": "https://www.capitalonecareers.com/search-jobs",
        "us bank": "https://careers.usbank.com/global/en/search-results",
        "pnc": "https://careers.pnc.com/global/en",
        "td bank": "https://jobs.td.com/en-CA/job-search-results/",
        "american express": "https://aexp.eightfold.ai/careers",
        "amex": "https://aexp.eightfold.ai/careers",
        "discover": "https://jobs.discover.com/jobs",
        # National banks
        "truist": "https://truist.wd1.myworkdayjobs.com/Careers",
        "charles schwab": "https://www.schwabjobs.com/search-jobs",
        "schwab": "https://www.schwabjobs.com/search-jobs",
        "bny mellon": "https://eofe.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions",
        "bny": "https://eofe.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions",
        "state street": "https://careers.statestreet.com/global/en/search-results",
        "citizens financial": "https://jobs.citizensbank.com/",
        "citizens bank": "https://jobs.citizensbank.com/",
        "hsbc": "https://mycareer.hsbc.com/",
        "bmo harris": "https://jobs.bmo.com/us/en/search-results",
        "bmo": "https://jobs.bmo.com/us/en/search-results",
        "fifth third bank": "https://fifththird.wd5.myworkdayjobs.com/53702",
        "fifth third": "https://fifththird.wd5.myworkdayjobs.com/53702",
        "keybank": "https://keybank.wd5.myworkdayjobs.com/External_Career_Site",
        "key bank": "https://keybank.wd5.myworkdayjobs.com/External_Career_Site",
        "ally financial": "https://ally.avature.net/careers",
        "ally bank": "https://ally.avature.net/careers",
        # Super regional banks
        "huntington": "https://huntington.wd5.myworkdayjobs.com/HNBCareers",
        "huntington bancshares": "https://huntington.wd5.myworkdayjobs.com/HNBCareers",
        "regions": "https://careers.regions.com/us/en/",
        "regions bank": "https://careers.regions.com/us/en/",
        "m&t bank": "https://mtb.wd5.myworkdayjobs.com/MTB",
        "northern trust": "https://ntrs.wd1.myworkdayjobs.com/northerntrust",
        "synchrony": "https://synchronyfinancial.wd5.myworkdayjobs.com/careers",
        "synchrony financial": "https://synchronyfinancial.wd5.myworkdayjobs.com/careers",
        "first citizens": "https://jobs.firstcitizens.com/",
        "first citizens bank": "https://jobs.firstcitizens.com/",
        "comerica": "https://careers.comerica.com/us/en",
        "zions bancorporation": "https://careers.zionsbancorp.com/",
        "zions bank": "https://careers.zionsbancorp.com/",
        "western alliance": "https://westernalliancebank.wd5.myworkdayjobs.com/WAB",
        "western alliance bank": "https://westernalliancebank.wd5.myworkdayjobs.com/WAB",
        "east west bank": "https://careers-eastwestbank.icims.com/jobs/intro",
        "webster bank": "https://careers.websteronline.com/jobs",
        "frost bank": "https://careers.frostbank.com/us/en",
        "flagstar bank": "https://careers.flagstar.com/us/en",
        "flagstar": "https://careers.flagstar.com/us/en",
        "synovus": "https://careers.synovus.com/us/en/",
        "bok financial": "https://jobs.bokf.com/",
        "first horizon": "https://firsthorizon.wd5.myworkdayjobs.com/TNBCareers",
        "associated bank": "https://associatedbank.wd1.myworkdayjobs.com/external_careers",
        # Tech
        "spotify": "https://www.lifeatspotify.com/jobs",
        "coinbase": "https://www.coinbase.com/careers/positions",
        "databricks": "https://www.databricks.com/company/careers/open-positions",
        "reddit": "https://boards.greenhouse.io/reddit",
    }

    def __init__(self, llm=None):
        super().__init__("CareerFinderAgent", llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Find the career page for the company."""
        self.status = AgentStatus.RUNNING
        company_name = context.company_name.lower().strip()

        self.log(f"Finding career page for: {company_name}")

        # Strategy 1: Check known URLs cache
        career_url = self._check_known_urls(company_name)
        if career_url:
            self.log(f"Found in cache: {career_url}")
            context.career_url = career_url
            return self._create_response(
                "orchestrator",
                "career_url_found",
                {"career_url": career_url, "method": "cache"},
                AgentStatus.SUCCESS
            )

        # Strategy 2: Try common URL patterns on company domain
        career_url = self._try_url_patterns(company_name)
        if career_url:
            self.log(f"Found via URL pattern: {career_url}")
            context.career_url = career_url
            return self._create_response(
                "orchestrator",
                "career_url_found",
                {"career_url": career_url, "method": "url_pattern"},
                AgentStatus.SUCCESS
            )

        # Strategy 3: Search company homepage for career links
        career_url = self._search_homepage(company_name)
        if career_url:
            self.log(f"Found on homepage: {career_url}")
            context.career_url = career_url
            return self._create_response(
                "orchestrator",
                "career_url_found",
                {"career_url": career_url, "method": "homepage_search"},
                AgentStatus.SUCCESS
            )

        # Strategy 4: Web search for career page
        career_url = self._web_search(company_name)
        if career_url:
            self.log(f"Found via web search: {career_url}")
            context.career_url = career_url
            return self._create_response(
                "orchestrator",
                "career_url_found",
                {"career_url": career_url, "method": "web_search"},
                AgentStatus.SUCCESS
            )

        # Failed to find career page
        self.status = AgentStatus.FAILED
        error_msg = f"Could not find career page for {company_name}"
        self.log(error_msg)
        return self._create_response(
            "orchestrator",
            "career_url_not_found",
            {"company": company_name},
            AgentStatus.FAILED,
            error_msg
        )

    def _check_known_urls(self, company_name: str) -> Optional[str]:
        """Check if company is in known URLs cache."""
        # Try exact match
        if company_name in self.KNOWN_CAREER_URLS:
            return self.KNOWN_CAREER_URLS[company_name]

        # Try partial match
        for key, url in self.KNOWN_CAREER_URLS.items():
            if key in company_name or company_name in key:
                return url

        return None

    def _try_url_patterns(self, company_name: str) -> Optional[str]:
        """Try common career page URL patterns."""
        # Build potential base URLs
        domains = [
            f"https://www.{company_name}.com",
            f"https://{company_name}.com",
            f"https://careers.{company_name}.com",
            f"https://jobs.{company_name}.com",
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        for domain in domains:
            for pattern in self.CAREER_PATTERNS:
                url = domain + pattern
                try:
                    response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        return response.url  # Return final URL after redirects
                except:
                    continue

        return None

    def _search_homepage(self, company_name: str) -> Optional[str]:
        """Search company homepage for career/jobs links."""
        domains = [
            f"https://www.{company_name}.com",
            f"https://{company_name}.com",
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        career_keywords = ['career', 'job', 'hiring', 'join', 'work', 'position', 'opening']

        for domain in domains:
            try:
                response = requests.get(domain, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find links containing career-related keywords
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text().lower()

                    for keyword in career_keywords:
                        if keyword in href.lower() or keyword in text:
                            # Build absolute URL
                            if href.startswith('http'):
                                return href
                            else:
                                return urljoin(domain, href)

            except:
                continue

        return None

    def _web_search(self, company_name: str) -> Optional[str]:
        """Use web search to find career page (placeholder for future implementation)."""
        # This could integrate with a search API or use the LLM
        # For now, return None and rely on other strategies
        return None
