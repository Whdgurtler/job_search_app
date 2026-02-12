"""
Agent 4: Scraper Agent
Responsible for extracting job postings from HTML content.
"""
import re
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin
from datetime import datetime
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus


@dataclass
class JobPosting:
    """Represents a scraped job posting."""
    title: str
    company: str
    location: str = "Not specified"
    is_remote: bool = False
    url: str = ""
    description: str = ""
    department: str = ""
    employment_type: str = ""
    posting_date: str = ""
    source: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class ScraperAgent(BaseAgent):
    """
    Extracts job postings from HTML content.

    Uses multiple strategies:
    1. CSS selector-based extraction (from PageAnalyzer)
    2. Link pattern matching
    3. LLM-powered extraction for complex pages
    """

    def __init__(self, llm=None):
        super().__init__("ScraperAgent", llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Extract jobs from the collected HTML."""
        self.status = AgentStatus.RUNNING

        # Get HTML from navigation results
        nav_data = message.data
        all_html = nav_data.get("all_html", [])
        if not all_html and context.page_html:
            all_html = [context.page_html]

        if not all_html:
            return self._create_response(
                "orchestrator",
                "scraping_failed",
                {},
                AgentStatus.FAILED,
                "No HTML content to scrape"
            )

        company_name = context.company_name
        career_url = context.career_url
        keywords = context.keywords
        selectors = context.navigation_plan.get("selectors", {})

        self.log(f"Scraping {len(all_html)} page(s) for {company_name}")

        all_jobs = []

        # Strategy 0: Extract from intercepted API data (highest fidelity)
        if context.intercepted_api_data:
            api_jobs = self.extract_from_api_data(context.intercepted_api_data, company_name)
            if api_jobs:
                self.log(f"API interception extracted {len(api_jobs)} jobs")
                all_jobs.extend(api_jobs)

        # Strategy 0b: ATS-specific extraction (known platform selectors)
        if context.ats_platform and not all_jobs:
            for html in all_html:
                ats_jobs = self._extract_from_ats(html, context.ats_platform, company_name, career_url)
                for job in ats_jobs:
                    if not self._is_duplicate(job, all_jobs):
                        all_jobs.append(job)
            if all_jobs:
                self.log(f"ATS extraction ({context.ats_platform}): {len(all_jobs)} jobs")

        # Process each page of HTML (standard strategies 1-3)
        if not all_jobs:
            for i, html in enumerate(all_html):
                self.log(f"Processing page {i + 1}/{len(all_html)}")
                soup = BeautifulSoup(html, 'html.parser')

                # Strategy 1: Use selectors from page analysis
                jobs = self._extract_with_selectors(soup, selectors, company_name, career_url)

                # Strategy 2: If no results, try link pattern matching
                if not jobs:
                    jobs = self._extract_from_links(soup, company_name, career_url)

                # Strategy 3: If still no results, use LLM extraction
                if not jobs and self.llm:
                    jobs = self._extract_with_llm(html, company_name, keywords)

                # Add unique jobs
                for job in jobs:
                    if not self._is_duplicate(job, all_jobs):
                        all_jobs.append(job)

        # Only filter out obvious category headers (not keyword filtering)
        # Keyword/relevance filtering is done by MatcherAgent
        all_jobs = self._filter_categories(all_jobs)

        # Convert to dicts
        jobs_data = [j.to_dict() if isinstance(j, JobPosting) else j for j in all_jobs]

        # Store in context
        context.raw_jobs = jobs_data

        self.log(f"Extracted {len(jobs_data)} jobs")

        return self._create_response(
            "orchestrator",
            "scraping_complete",
            {
                "jobs_count": len(jobs_data),
                "jobs": jobs_data
            },
            AgentStatus.SUCCESS
        )

    def _extract_with_selectors(
        self,
        soup: BeautifulSoup,
        selectors: Dict,
        company_name: str,
        base_url: str
    ) -> List[JobPosting]:
        """Extract jobs using CSS selectors from page analysis."""
        jobs = []
        job_card_selector = selectors.get("job_card", "")

        if not job_card_selector:
            return jobs

        try:
            cards = soup.select(job_card_selector)
            self.log(f"Found {len(cards)} job cards with selector: {job_card_selector}")

            for card in cards:
                try:
                    # Get raw text from card (preserving newlines)
                    link_elem = card.select_one(selectors.get("job_link", "a"))

                    # Get text with newlines preserved
                    if link_elem:
                        raw_text = link_elem.get_text(separator='\n', strip=True)
                    else:
                        title_elem = card.select_one(selectors.get("job_title", "a"))
                        raw_text = title_elem.get_text(separator='\n', strip=True) if title_elem else ""

                    if not raw_text or len(raw_text) < 3:
                        continue

                    # Parse title/location/remote from raw text
                    parsed = self._parse_job_text(raw_text)

                    # Extract URL
                    url = ""
                    if link_elem:
                        url = link_elem.get("href", "")
                        if url and not url.startswith("http"):
                            url = urljoin(base_url, url)

                    posting_date = self._extract_posting_date(card)

                    jobs.append(JobPosting(
                        title=parsed["title"],
                        company=company_name,
                        location=parsed["location"],
                        is_remote=parsed["is_remote"],
                        url=url,
                        posting_date=posting_date,
                        source="selector_extraction"
                    ))

                except Exception as e:
                    continue

        except Exception as e:
            self.log(f"Selector extraction error: {e}")

        return jobs

    def _extract_from_links(
        self,
        soup: BeautifulSoup,
        company_name: str,
        base_url: str
    ) -> List[JobPosting]:
        """Extract jobs by finding job-related links."""
        jobs = []

        # Find links that look like job postings
        job_link_patterns = [
            'a[href*="/job/"]',
            'a[href*="/jobs/"]',
            'a[href*="/position/"]',
            'a[href*="/positions/"]',
            'a[href*="/career/"]',
            'a[href*="/opening/"]',
        ]

        seen_urls = set()

        for pattern in job_link_patterns:
            links = soup.select(pattern)
            for link in links:
                href = link.get("href", "")
                if not href or href in seen_urls:
                    continue

                # Skip list/category pages
                if href.endswith("/jobs/") or href.endswith("/positions/") or href.endswith("/careers/"):
                    continue

                seen_urls.add(href)

                raw_text = link.get_text(separator='\n', strip=True)
                if not raw_text or len(raw_text) < 3:
                    continue

                # Parse title/location/remote
                parsed = self._parse_job_text(raw_text)

                # If parser didn't find location, try nearby elements
                if parsed["location"] == "Not specified":
                    parsed["location"] = self._find_nearby_location(link)

                # Build absolute URL
                if not href.startswith("http"):
                    href = urljoin(base_url, href)

                posting_date = self._extract_posting_date(link)

                jobs.append(JobPosting(
                    title=parsed["title"],
                    company=company_name,
                    location=parsed["location"],
                    is_remote=parsed["is_remote"],
                    url=href,
                    posting_date=posting_date,
                    source="link_extraction"
                ))

        return jobs

    def _extract_with_llm(
        self,
        html: str,
        company_name: str,
        keywords: str = ""
    ) -> List[JobPosting]:
        """Use LLM to extract jobs from complex pages."""
        jobs = []

        # Get text content
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Chunk if needed
        max_chars = 12000
        chunks = []
        if len(text) > max_chars:
            for i in range(0, len(text), max_chars - 1000):
                chunks.append(text[i:i + max_chars])
                if len(chunks) >= 3:
                    break
        else:
            chunks = [text]

        keyword_filter = f"\nFocus on jobs related to: {keywords}" if keywords else ""

        for chunk_idx, chunk in enumerate(chunks):
            prompt = f"""Extract job listings from this {company_name} career page text.{keyword_filter}

Text content:
{chunk}

Return ONLY a JSON array (no markdown):
[{{"title": "Job Title", "location": "City, State", "is_remote": true, "url": ""}}]

Rules:
- Skip department/category headers
- Only include actual job titles
- Separate title from location (do NOT put location in the title)
- Set is_remote to true if the job mentions Remote
- Return empty array [] if no jobs found"""

            response = self._call_llm(prompt, max_tokens=2000)
            if not response:
                continue

            try:
                # Extract JSON array
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    jobs_data = json.loads(json_match.group())
                    for job_data in jobs_data:
                        if isinstance(job_data, dict) and job_data.get("title"):
                            location = job_data.get("location", "Not specified")
                            is_remote = job_data.get("is_remote", False)

                            # Also check location string for "Remote"
                            if not is_remote and 'remote' in str(location).lower():
                                is_remote = True
                                location = re.sub(r'\bremote\b\s*[-,]?\s*', '', location, flags=re.I).strip()
                                if not location:
                                    location = "Not specified"

                            jobs.append(JobPosting(
                                title=job_data["title"],
                                company=company_name,
                                location=location,
                                is_remote=is_remote,
                                url=job_data.get("url", ""),
                                source="llm_extraction"
                            ))
            except:
                continue

        self.log(f"LLM extracted {len(jobs)} jobs")
        return jobs

    def _find_nearby_location(self, link_elem) -> str:
        """Try to find location text near a job link."""
        location = "Not specified"

        # Check parent elements
        parent = link_elem.parent
        for _ in range(3):  # Go up 3 levels
            if not parent:
                break

            # Look for location indicators
            loc_elem = parent.select_one("[class*='location'], [class*='place'], [class*='city']")
            if loc_elem:
                location = loc_elem.get_text(strip=True)
                break

            # Look for "Remote" text
            parent_text = parent.get_text()
            if "remote" in parent_text.lower():
                location = "Remote"
                break

            parent = parent.parent

        return location

    def _parse_job_text(self, raw_text: str) -> Dict:
        """
        Parse raw job text into title, location, and remote status.

        Many career sites embed title + location in a single text block like:
            "Senior Data Scientist\nRemote\nBay Area, CA, US"
            "Product Manager\nNew York, NY"
            "Software Engineer\nRemote"

        Returns:
            Dict with 'title', 'location', 'is_remote'
        """
        lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]

        title = ""
        location = "Not specified"
        is_remote = False

        if not lines:
            return {"title": raw_text.strip(), "location": location, "is_remote": is_remote}

        # First line is always the title
        title = lines[0]

        # Process remaining lines for location/remote
        location_parts = []
        for line in lines[1:]:
            line_lower = line.lower().strip()

            if line_lower in ('remote', 'remote work', 'fully remote', 'work from home'):
                is_remote = True
            elif 'remote' in line_lower and len(line_lower) < 30:
                # e.g. "Remote - US" or "Hybrid Remote"
                is_remote = True
                # Still might contain location info
                cleaned = re.sub(r'remote\s*[-–—]?\s*', '', line, flags=re.I).strip()
                if cleaned:
                    location_parts.append(cleaned)
            elif self._looks_like_location(line):
                location_parts.append(line)

        if location_parts:
            location = ', '.join(location_parts)

        # Also check if "Remote" is jammed into the title without newlines
        # e.g. "Data ScientistRemoteBay Area, CA, US"
        if not is_remote and 'Remote' in title:
            remote_idx = title.find('Remote')
            if remote_idx > 3:  # Not at the very start
                is_remote = True
                # Split: everything before "Remote" is title, after is location
                after_remote = title[remote_idx + len('Remote'):].strip()
                title = title[:remote_idx].strip()
                if after_remote and self._looks_like_location(after_remote):
                    location = after_remote

        # Clean up title
        title = re.sub(r'\s*[-–—]\s*$', '', title)
        title = re.sub(r'\s*,\s*$', '', title)
        title = ' '.join(title.split())

        return {"title": title, "location": location, "is_remote": is_remote}

    def _looks_like_location(self, text: str) -> bool:
        """Check if a string looks like a location."""
        # Common location patterns
        location_patterns = [
            r'[A-Z][a-z]+,\s*[A-Z]{2}',           # City, ST
            r'[A-Z][a-z]+,\s*[A-Z][a-z]+',         # City, Country
            r'\b(US|USA|UK|Canada|Australia|Germany|Japan|France|India|Singapore|Mexico)\b',
            r'\b(CA|NY|TX|WA|MA|IL|CO|GA|FL|OR|PA)\b',
            r'\b(San Francisco|New York|Seattle|Austin|London|Tokyo|Berlin)\b',
            r'\b(Bay Area|Remote)\b',
        ]
        for pattern in location_patterns:
            if re.search(pattern, text, re.I):
                return True
        return False

    def _extract_posting_date(self, element) -> str:
        """Extract posting date from a job card element or its ancestors.

        Looks for <time> tags, datetime attributes, and common date text patterns
        near the job card.
        """
        search_scope = element
        # Walk up to 2 parents to broaden the search
        for _ in range(2):
            parent = search_scope.parent if hasattr(search_scope, 'parent') else None
            if parent and parent.name not in (None, '[document]', 'html', 'body'):
                search_scope = parent
            else:
                break

        # 1. <time datetime="..."> is the most reliable
        time_el = search_scope.select_one('time[datetime]')
        if time_el:
            raw = time_el.get('datetime', '')
            parsed = self._parse_date_string(raw)
            if parsed:
                return parsed

        # 2. Elements with date-related classes/attributes
        date_selectors = [
            '[class*="date" i]', '[class*="posted" i]', '[class*="publish" i]',
            '[data-date]', '[data-posted]',
        ]
        for sel in date_selectors:
            date_el = search_scope.select_one(sel)
            if date_el:
                # Check data attributes first
                for attr in ('data-date', 'data-posted', 'datetime', 'content'):
                    val = date_el.get(attr, '')
                    if val:
                        parsed = self._parse_date_string(val)
                        if parsed:
                            return parsed
                # Fall back to text content
                text = date_el.get_text(strip=True)
                parsed = self._parse_date_string(text)
                if parsed:
                    return parsed

        return ""

    @staticmethod
    def _parse_date_string(text: str) -> str:
        """Try to parse a date string into YYYY-MM-DD format."""
        if not text:
            return ""
        text = text.strip()

        # ISO-like formats: 2025-01-15, 2025-01-15T10:00:00Z
        m = re.match(r'(\d{4}-\d{2}-\d{2})', text)
        if m:
            return m.group(1)

        # US formats: Jan 15, 2025 / January 15, 2025
        for fmt in ('%b %d, %Y', '%B %d, %Y', '%m/%d/%Y', '%d %b %Y', '%d %B %Y'):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # "3 days ago" style — skip, not reliable enough for dedup
        return ""

    def _clean_title(self, title: str, location: str) -> str:
        """Clean job title by removing appended location."""
        parsed = self._parse_job_text(title)
        return parsed["title"]

    def _is_duplicate(self, job: JobPosting, existing_jobs: List) -> bool:
        """Check if job is a duplicate."""
        for existing in existing_jobs:
            existing_title = existing.title if isinstance(existing, JobPosting) else existing.get("title", "")
            existing_url = existing.url if isinstance(existing, JobPosting) else existing.get("url", "")

            # Check by URL (most reliable)
            if job.url and existing_url and job.url == existing_url:
                return True

            # Check by title (fuzzy)
            if job.title.lower() == existing_title.lower():
                return True

        return False

    def _filter_by_keywords(self, jobs: List[JobPosting], keywords: str) -> List[JobPosting]:
        """Filter jobs by keyword relevance."""
        if not keywords:
            return jobs

        keywords_lower = keywords.lower()
        keyword_terms = keywords_lower.replace(',', ' ').split()

        # Related terms mapping
        related_terms = {
            'data scientist': ['data science', 'machine learning', 'ml', 'analytics', 'ai'],
            'machine learning': ['ml', 'ai', 'data scientist', 'deep learning'],
            'software engineer': ['developer', 'swe', 'programmer', 'software'],
            'product manager': ['pm', 'product'],
            'data engineer': ['data', 'etl', 'pipeline'],
        }

        filtered = []
        for job in jobs:
            title_lower = job.title.lower() if isinstance(job, JobPosting) else job.get("title", "").lower()

            # Check direct keyword match
            if any(term in title_lower for term in keyword_terms):
                filtered.append(job)
                continue

            # Check related terms
            for key, terms in related_terms.items():
                if key in keywords_lower:
                    if any(term in title_lower for term in terms):
                        filtered.append(job)
                        break

        self.log(f"Keyword filter: {len(jobs)} -> {len(filtered)} jobs")
        return filtered

    # ------------------------------------------------------------------
    # ATS-specific extraction
    # ------------------------------------------------------------------

    # Known CSS selectors for popular ATS platforms
    _ATS_SELECTORS: Dict[str, Dict[str, str]] = {
        "workday": {
            "job_card": (
                "li.css-1q2dra3, [data-automation-id='jobItem'], "
                "a[data-automation-id='jobTitle'], "
                "li[class*='css-'] a[href*='job']"
            ),
            "title": "a[data-automation-id='jobTitle'], h3 a, a",
            "location": "[data-automation-id='locations'], dd.css-129m7dg, span[class*='location']",
            "link": "a[data-automation-id='jobTitle'], a[href*='job']",
        },
        "greenhouse": {
            "job_card": ".opening, .job-post, [class*='JobPost'], tr.job-post",
            "title": "a, .opening-title, td.cell-title a",
            "location": ".location, .job-post-location, td.cell-location",
            "link": "a",
        },
        "lever": {
            "job_card": ".posting, [class*='posting']",
            "title": ".posting-title a, h5 a, a",
            "location": ".posting-categories .sort-by-location, .location, .workplaceTypes",
            "link": ".posting-title a, h5 a, a",
        },
        "icims": {
            "job_card": ".iCIMS_JobsTable .row, .listingContainer, .iCIMS_MainWrapper li",
            "title": "a.iCIMS_Anchor, .title a, a",
            "location": ".iCIMS_JobsTable .col-xs-6:nth-child(2), .location",
            "link": "a.iCIMS_Anchor, a",
        },
        "taleo": {
            "job_card": "tr.job, .requisition, .contentlinepanel, table.job-results tr",
            "title": "a.jobTitle, .titlelink a, a",
            "location": ".location, .locationColumn",
            "link": "a.jobTitle, .titlelink a, a",
        },
    }

    def _extract_from_ats(
        self, html: str, ats_platform: str, company_name: str, base_url: str
    ) -> List[JobPosting]:
        """Extract jobs using known ATS platform selectors."""
        sels = self._ATS_SELECTORS.get(ats_platform)
        if not sels:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        jobs: List[JobPosting] = []

        for selector in sels["job_card"].split(", "):
            selector = selector.strip()
            if not selector:
                continue
            cards = soup.select(selector)
            if not cards:
                continue

            self.log(f"ATS ({ats_platform}) selector '{selector}' matched {len(cards)} cards")

            for card in cards:
                try:
                    # Title
                    title_el = None
                    for ts in sels["title"].split(", "):
                        title_el = card.select_one(ts.strip())
                        if title_el:
                            break
                    if not title_el:
                        title_el = card
                    raw_text = title_el.get_text(separator='\n', strip=True)
                    if not raw_text or len(raw_text) < 3:
                        continue

                    parsed = self._parse_job_text(raw_text)

                    # Location (override if found in ATS element)
                    for ls in sels["location"].split(", "):
                        loc_el = card.select_one(ls.strip())
                        if loc_el:
                            loc_text = loc_el.get_text(strip=True)
                            if loc_text:
                                parsed["location"] = loc_text
                            break

                    # Link
                    url = ""
                    for lks in sels["link"].split(", "):
                        lk_el = card.select_one(lks.strip())
                        if lk_el and lk_el.get("href"):
                            url = lk_el["href"]
                            break
                    if url and not url.startswith("http"):
                        url = urljoin(base_url, url)

                    posting_date = self._extract_posting_date(card)

                    jobs.append(JobPosting(
                        title=parsed["title"],
                        company=company_name,
                        location=parsed["location"],
                        is_remote=parsed["is_remote"],
                        url=url,
                        posting_date=posting_date,
                        source=f"ats_{ats_platform}",
                    ))
                except Exception:
                    continue

            if jobs:
                break  # first matching selector is enough

        return jobs

    # ------------------------------------------------------------------
    # API data extraction
    # ------------------------------------------------------------------

    def extract_from_api_data(
        self, api_data: list, company_name: str
    ) -> List[JobPosting]:
        """Extract jobs from intercepted API/XHR JSON responses."""
        jobs: List[JobPosting] = []

        for entry in api_data:
            body = entry.get("body", "")
            if not body:
                continue
            try:
                data = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                continue

            arrays = self._find_job_arrays(data)
            for arr in arrays:
                for item in arr:
                    if not isinstance(item, dict):
                        continue
                    title = (
                        item.get("title") or item.get("name")
                        or item.get("jobTitle") or item.get("job_title")
                        or item.get("positionTitle") or item.get("position_title")
                        or ""
                    )
                    if not title or len(title) < 3:
                        continue

                    # Location — many shapes in API responses
                    loc = "Not specified"
                    loc_raw = item.get("location") or item.get("locationsText") or ""
                    if isinstance(loc_raw, dict):
                        loc = loc_raw.get("name") or loc_raw.get("city") or "Not specified"
                    elif isinstance(loc_raw, list):
                        parts = [
                            (l.get("name") if isinstance(l, dict) else str(l))
                            for l in loc_raw[:3]
                        ]
                        loc = ", ".join(p for p in parts if p) or "Not specified"
                    elif isinstance(loc_raw, str) and loc_raw:
                        loc = loc_raw

                    url = (
                        item.get("url") or item.get("absolute_url")
                        or item.get("hostedUrl") or item.get("applyUrl") or ""
                    )

                    is_remote = False
                    if "remote" in loc.lower() or item.get("isRemote") or item.get("remote"):
                        is_remote = True

                    # Extract posting date from API data
                    posting_date = ""
                    for date_key in ("postedDate", "posted_date", "publishedDate",
                                     "published_date", "createdAt", "created_at",
                                     "datePosted", "date_posted", "postingDate",
                                     "posting_date", "updatedAt", "updated_at"):
                        raw_date = item.get(date_key, "")
                        if raw_date:
                            posting_date = self._parse_date_string(str(raw_date))
                            if posting_date:
                                break

                    jobs.append(JobPosting(
                        title=title,
                        company=company_name,
                        location=loc,
                        is_remote=is_remote,
                        url=url,
                        posting_date=posting_date,
                        department=item.get("department", item.get("departmentName", "")),
                        source="api_interception",
                    ))

        return jobs

    def _find_job_arrays(self, data, depth: int = 0) -> List[list]:
        """Recursively find arrays of job-like dicts in JSON data."""
        if depth > 5:
            return []

        results: List[list] = []
        job_keys = {"title", "name", "jobtitle", "job_title", "positiontitle", "position_title"}

        if isinstance(data, list) and len(data) >= 3:
            hits = sum(
                1 for item in data[:10]
                if isinstance(item, dict) and any(
                    k.lower() in job_keys for k in item
                )
            )
            if hits >= 2:
                results.append(data)

        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, (list, dict)):
                    results.extend(self._find_job_arrays(v, depth + 1))

        return results

    # ------------------------------------------------------------------
    # Category filtering
    # ------------------------------------------------------------------

    def _filter_categories(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove category headers from job list."""
        category_keywords = [
            'engineering', 'marketing', 'sales', 'finance', 'operations',
            'design', 'product', 'legal', 'hr', 'human resources', 'support',
            'customer success', 'business', 'corporate'
        ]

        filtered = []
        for job in jobs:
            title = job.title if isinstance(job, JobPosting) else job.get("title", "")
            title_lower = title.lower()
            word_count = len(title.split())

            # Skip if short title matching category
            is_category = False
            if word_count <= 3:
                if any(cat in title_lower for cat in category_keywords):
                    # Keep if it has job indicators
                    job_indicators = ['engineer', 'scientist', 'analyst', 'manager', 'developer',
                                     'designer', 'lead', 'director', 'specialist', 'coordinator']
                    if not any(ind in title_lower for ind in job_indicators):
                        is_category = True

            if not is_category:
                filtered.append(job)

        if len(filtered) < len(jobs):
            self.log(f"Removed {len(jobs) - len(filtered)} category headers")

        return filtered
