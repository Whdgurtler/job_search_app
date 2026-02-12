"""
Agent 2: Page Analyzer
Responsible for analyzing career page structure and creating a navigation plan.
"""
import re
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass, field, asdict

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus


@dataclass
class PageStructure:
    """Describes the structure of a career page."""
    pagination_type: str = "none"  # none, load_more, numbered, infinite_scroll
    total_jobs_indicator: Optional[str] = None  # Text showing total jobs
    estimated_total_jobs: int = 0
    jobs_per_page: int = 0
    total_pages: int = 0

    # Selectors
    job_card_selector: str = ""
    job_title_selector: str = ""
    job_location_selector: str = ""
    job_link_selector: str = ""
    load_more_selector: str = ""
    next_page_selector: str = ""
    search_input_selector: str = ""

    # Pagination details
    pagination_button_text: List[str] = field(default_factory=list)
    page_number_pattern: str = ""

    # Additional info
    has_filters: bool = False
    has_search: bool = False
    is_javascript_heavy: bool = False
    needs_scroll: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


class PageAnalyzerAgent(BaseAgent):
    """
    Analyzes a career page to understand its structure.

    Determines:
    - Pagination type (load more, numbered pages, infinite scroll)
    - CSS selectors for job elements
    - How to navigate the page
    - Total number of jobs available
    """

    def __init__(self, llm=None):
        super().__init__("PageAnalyzerAgent", llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Analyze the career page structure."""
        self.status = AgentStatus.RUNNING

        html = context.page_html
        if not html:
            return self._create_response(
                "orchestrator",
                "analysis_failed",
                {},
                AgentStatus.FAILED,
                "No HTML content to analyze"
            )

        self.log(f"Analyzing page structure for {context.company_name}")

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Build page structure
        structure = PageStructure()

        # Detect pagination type
        structure = self._detect_pagination(soup, structure)

        # Find job card selectors
        structure = self._find_job_selectors(soup, structure)

        # Check for search/filters
        structure = self._check_interactive_elements(soup, structure)

        # Estimate total jobs
        structure = self._estimate_total_jobs(soup, structure)

        # Use LLM to refine analysis if available
        if self.llm and not structure.job_card_selector:
            structure = self._llm_analyze_structure(html, structure)

        # Store in context
        context.page_structure = structure.to_dict()

        # Create navigation plan
        nav_plan = self._create_navigation_plan(structure)
        context.navigation_plan = nav_plan

        self.log(f"Analysis complete: {structure.pagination_type} pagination, "
                f"~{structure.estimated_total_jobs} jobs")

        return self._create_response(
            "orchestrator",
            "analysis_complete",
            {
                "page_structure": structure.to_dict(),
                "navigation_plan": nav_plan
            },
            AgentStatus.SUCCESS
        )

    def _detect_pagination(self, soup: BeautifulSoup, structure: PageStructure) -> PageStructure:
        """Detect the type of pagination used."""

        # Check for "Load More" button
        load_more_patterns = [
            'load more', 'show more', 'view more', 'more jobs',
            'load-more', 'loadmore', 'show-more'
        ]

        buttons = soup.find_all(['button', 'a'])
        for btn in buttons:
            btn_text = btn.get_text().lower().strip()
            btn_class = ' '.join(btn.get('class', [])).lower()

            for pattern in load_more_patterns:
                if pattern in btn_text or pattern in btn_class:
                    structure.pagination_type = "load_more"
                    structure.load_more_selector = self._build_selector(btn)
                    structure.pagination_button_text.append(btn_text)
                    self.log(f"Found load more button: {btn_text}")
                    return structure

        # Check for numbered pagination
        page_indicators = soup.find_all(['a', 'button'], string=re.compile(r'^\d+$'))
        if len(page_indicators) >= 2:
            # Found page numbers
            structure.pagination_type = "numbered"
            # Find the container
            for indicator in page_indicators:
                parent = indicator.parent
                if parent and len(parent.find_all(['a', 'button'], string=re.compile(r'^\d+$'))) >= 2:
                    structure.next_page_selector = "a[text()='2'], button[text()='2']"
                    break
            self.log("Found numbered pagination")
            return structure

        # Check for next/prev buttons
        next_patterns = ['next', 'siguiente', '>', '→', '»']
        for btn in buttons:
            btn_text = btn.get_text().lower().strip()
            for pattern in next_patterns:
                if pattern in btn_text:
                    structure.pagination_type = "numbered"
                    structure.next_page_selector = self._build_selector(btn)
                    self.log(f"Found next button: {btn_text}")
                    return structure

        # Check for infinite scroll indicators
        scroll_indicators = soup.find_all(attrs={'data-infinite-scroll': True})
        if scroll_indicators:
            structure.pagination_type = "infinite_scroll"
            structure.needs_scroll = True
            self.log("Detected infinite scroll")
            return structure

        # No pagination detected
        structure.pagination_type = "none"
        self.log("No pagination detected")
        return structure

    def _find_job_selectors(self, soup: BeautifulSoup, structure: PageStructure) -> PageStructure:
        """Find CSS selectors for job card elements."""

        # Common job card patterns
        job_card_patterns = [
            ('a[href*="/job"]', 'job link pattern'),
            ('a[href*="/position"]', 'position link pattern'),
            ('a[href*="/careers/"]', 'careers link pattern'),
            ('[class*="job-card"]', 'job-card class'),
            ('[class*="job-listing"]', 'job-listing class'),
            ('[class*="position-card"]', 'position-card class'),
            ('[class*="opening"]', 'opening class'),
            ('article[class*="job"]', 'article.job'),
            ('li[class*="job"]', 'li.job'),
            ('div[data-job-id]', 'data-job-id'),
        ]

        for selector, description in job_card_patterns:
            elements = soup.select(selector)
            if elements and len(elements) >= 3:  # At least 3 job-like elements
                structure.job_card_selector = selector
                structure.jobs_per_page = len(elements)
                self.log(f"Found job cards using {description}: {len(elements)} elements")

                # Try to find title and location within cards
                sample_card = elements[0]
                structure.job_title_selector = self._find_title_selector(sample_card)
                structure.job_location_selector = self._find_location_selector(sample_card)
                structure.job_link_selector = self._find_link_selector(sample_card)
                break

        return structure

    def _find_title_selector(self, card) -> str:
        """Find the selector for job title within a card."""
        # Try common title patterns
        patterns = ['h1', 'h2', 'h3', 'h4', '[class*="title"]', '[class*="name"]', 'a']
        for pattern in patterns:
            elem = card.select_one(pattern)
            if elem and elem.get_text().strip():
                return pattern
        return 'a'  # Default to link text

    def _find_location_selector(self, card) -> str:
        """Find the selector for job location within a card."""
        patterns = [
            '[class*="location"]',
            '[class*="place"]',
            '[class*="city"]',
            'span:contains("Remote")',
            '[data-location]'
        ]
        for pattern in patterns:
            try:
                elem = card.select_one(pattern)
                if elem:
                    return pattern
            except:
                continue
        return '[class*="location"]'

    def _find_link_selector(self, card) -> str:
        """Find the selector for job link within a card."""
        link = card.select_one('a[href*="job"], a[href*="position"], a[href]')
        if link:
            href = link.get('href', '')
            if '/job' in href:
                return 'a[href*="job"]'
            elif '/position' in href:
                return 'a[href*="position"]'
        return 'a'

    def _check_interactive_elements(self, soup: BeautifulSoup, structure: PageStructure) -> PageStructure:
        """Check for search boxes and filters."""

        # Check for search input
        search_inputs = soup.find_all('input', {'type': 'text'})
        for inp in search_inputs:
            placeholder = (inp.get('placeholder') or '').lower()
            name = (inp.get('name') or '').lower()
            if 'search' in placeholder or 'search' in name or 'job' in placeholder:
                structure.has_search = True
                structure.search_input_selector = self._build_selector(inp)
                break

        # Check for filters
        filter_indicators = soup.find_all(
            ['select', 'div'],
            class_=re.compile(r'filter|dropdown|select', re.I)
        )
        if filter_indicators:
            structure.has_filters = True

        # Check if page is JavaScript-heavy
        scripts = soup.find_all('script')
        react_indicators = soup.find_all(id=re.compile(r'root|app|__next'))
        if len(scripts) > 10 or react_indicators:
            structure.is_javascript_heavy = True

        return structure

    def _estimate_total_jobs(self, soup: BeautifulSoup, structure: PageStructure) -> PageStructure:
        """Try to find and parse total job count."""

        # Look for text like "X jobs" or "X open positions"
        text = soup.get_text()
        patterns = [
            r'(\d+)\s*(?:open\s+)?(?:job|position|role|opening)s?',
            r'showing\s+\d+\s*-\s*\d+\s+of\s+(\d+)',
            r'(\d+)\s+results?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    structure.estimated_total_jobs = int(match.group(1))
                    structure.total_jobs_indicator = match.group(0)
                    self.log(f"Found total jobs indicator: {match.group(0)}")
                    break
                except:
                    continue

        # Estimate pages if we have jobs per page
        if structure.jobs_per_page > 0 and structure.estimated_total_jobs > 0:
            structure.total_pages = (structure.estimated_total_jobs + structure.jobs_per_page - 1) // structure.jobs_per_page

        return structure

    def _build_selector(self, element) -> str:
        """Build a CSS selector for an element."""
        if element.get('id'):
            return f"#{element['id']}"

        classes = element.get('class', [])
        if classes:
            return f"{element.name}.{'.'.join(classes)}"

        return element.name

    def _llm_analyze_structure(self, html: str, structure: PageStructure) -> PageStructure:
        """Use LLM to analyze page structure when heuristics fail."""
        # Take a sample of the HTML
        sample = html[:15000] if len(html) > 15000 else html

        prompt = f"""Analyze this career page HTML and identify the CSS selectors for job listings.

HTML Sample:
{sample}

Return JSON only:
{{
    "job_card_selector": "CSS selector for job cards/listings",
    "job_title_selector": "CSS selector for job title within card",
    "job_link_selector": "CSS selector for job link within card",
    "pagination_type": "none|load_more|numbered|infinite_scroll"
}}"""

        response = self._call_llm(prompt, max_tokens=500)
        if response:
            try:
                # Extract JSON from response
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    if data.get('job_card_selector'):
                        structure.job_card_selector = data['job_card_selector']
                    if data.get('job_title_selector'):
                        structure.job_title_selector = data['job_title_selector']
                    if data.get('job_link_selector'):
                        structure.job_link_selector = data['job_link_selector']
                    if data.get('pagination_type'):
                        structure.pagination_type = data['pagination_type']
            except:
                pass

        return structure

    def _create_navigation_plan(self, structure: PageStructure) -> Dict:
        """Create a navigation plan based on page structure analysis."""
        plan = {
            "steps": [],
            "pagination_strategy": structure.pagination_type,
            "max_pages": min(structure.total_pages, 30) if structure.total_pages > 0 else 30,
            "requires_javascript": structure.is_javascript_heavy,
            "selectors": {
                "job_card": structure.job_card_selector,
                "job_title": structure.job_title_selector,
                "job_location": structure.job_location_selector,
                "job_link": structure.job_link_selector,
            }
        }

        # Build navigation steps
        if structure.is_javascript_heavy:
            plan["steps"].append({
                "action": "wait_for_js",
                "timeout": 5000
            })

        if structure.needs_scroll:
            plan["steps"].append({
                "action": "scroll_to_bottom",
                "wait_after": 2000
            })

        if structure.pagination_type == "load_more":
            plan["steps"].append({
                "action": "click_load_more",
                "selector": structure.load_more_selector,
                "button_text": structure.pagination_button_text,
                "max_clicks": plan["max_pages"]
            })
        elif structure.pagination_type == "numbered":
            plan["steps"].append({
                "action": "navigate_pages",
                "method": "numbered",
                "max_pages": plan["max_pages"]
            })
        elif structure.pagination_type == "infinite_scroll":
            plan["steps"].append({
                "action": "infinite_scroll",
                "max_scrolls": 20,
                "wait_between": 2000
            })

        plan["steps"].append({
            "action": "extract_jobs",
            "selector": structure.job_card_selector
        })

        return plan
