"""
Agent 7: Review Agent
Diagnoses scraping failures and proposes retry strategies.
"""
import re
from typing import Dict, List

from bs4 import BeautifulSoup

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus


class ReviewAgent(BaseAgent):
    """
    Diagnoses why scraping failed and proposes a retry strategy.

    Examines:
    - HTML content: empty SPA shell? iframe? auth wall?
    - Intercepted API data: did we capture job data via XHR?
    - URL patterns: known ATS platform?
    - Page text content: is there text but scraper couldn't parse it?
    """

    # ATS platform detection patterns (compiled on first use)
    ATS_PATTERNS: Dict[str, List[str]] = {
        "workday": [
            r'myworkdayjobs\.com',
            r'wd\d+\.myworkdayjobs\.com',
            r'workday\.com.*recruiting',
        ],
        "greenhouse": [
            r'boards\.greenhouse\.io',
            r'greenhouse\.io',
            r'grnh\.se',
        ],
        "lever": [
            r'jobs\.lever\.co',
            r'lever\.co',
        ],
        "icims": [
            r'icims\.com',
            r'careers-.*\.icims\.com',
        ],
        "taleo": [
            r'taleo\.net',
            r'oracle.*taleo',
        ],
        "successfactors": [
            r'successfactors\.com',
            r'jobs\.sap\.com',
        ],
        "eightfold": [
            r'eightfold\.ai',
        ],
        "avature": [
            r'avature\.net',
        ],
    }

    def __init__(self, llm=None):
        super().__init__("ReviewAgent", llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Diagnose scraping failure and propose retry strategy."""
        self.status = AgentStatus.RUNNING

        html = context.page_html
        career_url = context.career_url
        api_data = context.intercepted_api_data

        diagnosis = self._diagnose_page(html, career_url)
        context.page_diagnosis = diagnosis["type"]
        context.ats_platform = diagnosis.get("ats_platform", "")

        strategy = self._propose_strategy(diagnosis, api_data, context.retry_count)
        context.retry_strategy = strategy

        self.log(f"Diagnosis: {diagnosis['type']}, ATS: {diagnosis.get('ats_platform', 'none')}, Strategy: {strategy}")

        return self._create_response(
            "orchestrator",
            "review_complete",
            {
                "diagnosis": diagnosis,
                "retry_strategy": strategy,
                "ats_platform": diagnosis.get("ats_platform", ""),
            },
            AgentStatus.SUCCESS
        )

    # ------------------------------------------------------------------
    # Page diagnosis
    # ------------------------------------------------------------------

    def _diagnose_page(self, html: str, url: str) -> dict:
        """Examine HTML + URL to determine why scraping failed."""
        if not html:
            return {"type": "empty", "detail": "No HTML content"}

        soup = BeautifulSoup(html, 'html.parser')

        # Strip non-visible tags and measure visible text
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            tag.decompose()
        visible_text = soup.get_text(separator=" ", strip=True)
        text_len = len(visible_text)

        # Detect ATS platform from URL
        ats = self._detect_ats(url)

        # --- Check for auth wall ---
        if self._is_auth_wall(soup, visible_text):
            return {"type": "auth_wall", "ats_platform": ats, "text_len": text_len}

        # --- Check for CAPTCHA ---
        if self._is_captcha(soup, visible_text):
            return {"type": "captcha", "ats_platform": ats, "text_len": text_len}

        # --- Check for SPA shell (empty body with JS framework markers) ---
        js_indicators = soup.find_all(
            id=re.compile(r'^(root|app|__next|__nuxt|main-app)$', re.I)
        )
        data_react = soup.find_all(attrs={"data-reactroot": True})
        ng_app = soup.find_all(attrs={"ng-app": True}) + soup.find_all(attrs={"ng-version": True})
        is_spa = bool(js_indicators or data_react or ng_app)

        if text_len < 200 and is_spa:
            return {"type": "spa_shell", "ats_platform": ats, "text_len": text_len,
                    "detail": "Page is a JS framework shell with no rendered content"}

        # --- Check for iframe-embedded content ---
        job_iframes = soup.find_all("iframe", src=re.compile(
            r'job|career|workday|icims|greenhouse|lever|taleo', re.I
        ))
        if job_iframes:
            iframe_src = job_iframes[0].get("src", "")
            return {"type": "iframe_content", "ats_platform": ats,
                    "iframe_src": iframe_src, "text_len": text_len}

        # --- Content exists but scraper couldn't parse it ---
        if text_len > 500:
            return {"type": "parse_failure", "ats_platform": ats, "text_len": text_len,
                    "detail": "Page has content but extraction strategies failed"}

        # --- SPA with some content but not enough ---
        if is_spa:
            return {"type": "spa_shell", "ats_platform": ats, "text_len": text_len,
                    "detail": "JS framework page with insufficient rendered content"}

        return {"type": "unknown", "ats_platform": ats, "text_len": text_len}

    def _detect_ats(self, url: str) -> str:
        """Detect ATS platform from URL."""
        if not url:
            return ""
        for platform, patterns in self.ATS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.I):
                    return platform
        return ""

    def _is_auth_wall(self, soup: BeautifulSoup, text: str) -> bool:
        """Check if page shows a login / auth wall."""
        # Password input is a strong signal
        if soup.find("input", {"type": "password"}):
            return True
        text_lower = text.lower()
        auth_phrases = ["sign in", "log in", "login", "single sign-on", "sso"]
        # Need at least one phrase AND a form or button nearby
        if any(p in text_lower for p in auth_phrases):
            if soup.find("form") or soup.find("button"):
                # Make sure it's not just a nav "Sign In" link on an otherwise valid page
                if len(text) < 1000:
                    return True
        return False

    def _is_captcha(self, soup: BeautifulSoup, text: str) -> bool:
        """Check for CAPTCHA challenges."""
        text_lower = text.lower()
        if any(p in text_lower for p in [
            "captcha", "verify you are human", "i'm not a robot",
            "please verify", "access denied", "checking your browser",
        ]):
            return True
        if soup.find("iframe", src=re.compile(r'recaptcha|hcaptcha|captcha', re.I)):
            return True
        return False

    # ------------------------------------------------------------------
    # Strategy proposal
    # ------------------------------------------------------------------

    def _propose_strategy(self, diagnosis: dict, api_data: list, retry_count: int) -> str:
        """Based on diagnosis + available data, propose a retry strategy."""
        dtype = diagnosis["type"]

        # If we already captured API data with job content, use it directly
        if api_data and self._api_data_has_jobs(api_data):
            return "use_api_data"

        if dtype == "auth_wall":
            return "give_up"

        if dtype == "captcha":
            return "give_up"

        if dtype == "iframe_content":
            return "try_iframe"

        if dtype == "spa_shell":
            ats = diagnosis.get("ats_platform", "")
            if ats:
                return "try_ats_pattern"
            if retry_count < 2:
                return "wait_longer"
            return "give_up"

        if dtype == "parse_failure":
            ats = diagnosis.get("ats_platform", "")
            if ats:
                return "try_ats_pattern"
            return "use_llm_on_raw_text"

        if dtype == "empty":
            if retry_count < 2:
                return "wait_longer"
            return "give_up"

        # unknown — try ATS if detected, else LLM
        ats = diagnosis.get("ats_platform", "")
        if ats:
            return "try_ats_pattern"
        return "use_llm_on_raw_text"

    def _api_data_has_jobs(self, api_data: list) -> bool:
        """Quick check: does any intercepted API response contain job-like JSON?"""
        import json as _json
        job_keys = {"title", "name", "jobtitle", "job_title", "positiontitle"}

        for entry in api_data:
            body = entry.get("body", "")
            if not body:
                continue
            try:
                data = _json.loads(body)
                items = self._find_items(data)
                if items:
                    return True
            except (_json.JSONDecodeError, TypeError):
                continue
        return False

    def _find_items(self, data, depth: int = 0) -> bool:
        """Recursively check if data contains an array of job-like dicts."""
        if depth > 4:
            return False
        job_keys = {"title", "name", "jobtitle", "job_title", "positiontitle"}
        if isinstance(data, list) and len(data) >= 3:
            hits = sum(
                1 for item in data[:10]
                if isinstance(item, dict) and any(
                    k.lower() in job_keys for k in item
                )
            )
            if hits >= 2:
                return True
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, (list, dict)) and self._find_items(v, depth + 1):
                    return True
        return False
