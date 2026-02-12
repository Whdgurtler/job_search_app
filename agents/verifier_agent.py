"""
Agent 5: Verifier Agent
Responsible for verifying scraped jobs and requesting re-analysis if needed.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus


@dataclass
class VerificationResult:
    """Result of job verification."""
    is_valid: bool
    jobs_verified: int
    jobs_removed: int
    issues: List[str]
    needs_reanalysis: bool
    reanalysis_reason: str = ""


class VerifierAgent(BaseAgent):
    """
    Verifies scraped job data and ensures quality.

    Checks:
    - Job count is reasonable (not 0, not suspiciously low)
    - Jobs have valid titles (not categories)
    - Jobs have URLs when expected
    - Jobs match search keywords
    - No obvious duplicates

    Can trigger re-analysis if results are suspicious.
    """

    # Minimum jobs expected (can be adjusted based on company size)
    MIN_JOBS_THRESHOLD = 1
    # Maximum retries before giving up
    MAX_RETRIES = 3

    def __init__(self, llm=None):
        super().__init__("VerifierAgent", llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Verify scraped jobs and determine if re-analysis is needed."""
        self.status = AgentStatus.RUNNING

        jobs = context.raw_jobs
        keywords = context.keywords
        company = context.company_name
        retry_count = context.retry_count

        self.log(f"Verifying {len(jobs)} jobs for {company}")

        issues = []
        needs_reanalysis = False
        reanalysis_reason = ""

        # Check 1: Job count
        if len(jobs) == 0:
            issues.append("No jobs found")
            if retry_count < self.MAX_RETRIES:
                needs_reanalysis = True
                reanalysis_reason = "zero_jobs"
        elif len(jobs) < self.MIN_JOBS_THRESHOLD:
            issues.append(f"Very few jobs found ({len(jobs)})")

        # Check 2: Validate individual jobs
        valid_jobs = []
        invalid_count = 0

        for job in jobs:
            validation = self._validate_job(job, keywords)
            if validation["is_valid"]:
                valid_jobs.append(job)
            else:
                invalid_count += 1
                if validation.get("issue"):
                    issues.append(validation["issue"])

        # Check 3: Keyword relevance (if keywords provided)
        if keywords and valid_jobs:
            relevant_count = self._count_relevant_jobs(valid_jobs, keywords)
            relevance_ratio = relevant_count / len(valid_jobs)

            if relevance_ratio < 0.3:  # Less than 30% relevant
                issues.append(f"Low keyword relevance: {relevant_count}/{len(valid_jobs)} jobs match '{keywords}'")
                if retry_count < self.MAX_RETRIES:
                    needs_reanalysis = True
                    reanalysis_reason = "low_relevance"

        # Check 4: Duplicate detection
        unique_jobs, dup_count = self._remove_duplicates(valid_jobs)
        if dup_count > 0:
            issues.append(f"Removed {dup_count} duplicate jobs")
            valid_jobs = unique_jobs

        # Check 5: URL validation
        jobs_with_urls = sum(1 for j in valid_jobs if j.get("url"))
        if len(valid_jobs) > 0 and jobs_with_urls / len(valid_jobs) < 0.5:
            issues.append(f"Many jobs missing URLs: {jobs_with_urls}/{len(valid_jobs)}")

        # Store verified jobs in context
        context.verified_jobs = valid_jobs

        # Build result
        result = VerificationResult(
            is_valid=len(valid_jobs) > 0 and not needs_reanalysis,
            jobs_verified=len(valid_jobs),
            jobs_removed=len(jobs) - len(valid_jobs),
            issues=issues,
            needs_reanalysis=needs_reanalysis,
            reanalysis_reason=reanalysis_reason
        )

        self.log(f"Verification complete: {len(valid_jobs)} valid jobs, {len(issues)} issues")

        if needs_reanalysis:
            context.retry_count += 1
            self.log(f"Requesting re-analysis (attempt {context.retry_count}/{self.MAX_RETRIES})")
            return self._create_response(
                "orchestrator",
                "needs_reanalysis",
                {
                    "reason": reanalysis_reason,
                    "retry_count": context.retry_count,
                    "issues": issues
                },
                AgentStatus.NEEDS_RETRY
            )

        return self._create_response(
            "orchestrator",
            "verification_complete",
            {
                "jobs_verified": len(valid_jobs),
                "jobs_removed": len(jobs) - len(valid_jobs),
                "issues": issues,
                "jobs": valid_jobs
            },
            AgentStatus.SUCCESS
        )

    def _validate_job(self, job: Dict, keywords: str = "") -> Dict:
        """Validate a single job posting."""
        title = job.get("title", "")

        # Check for empty title
        if not title or len(title) < 3:
            return {"is_valid": False, "issue": "Empty or too short title"}

        # Check for category headers
        if self._is_category_header(title):
            return {"is_valid": False, "issue": f"Category header: {title}"}

        # Check for garbage data
        if self._is_garbage(title):
            return {"is_valid": False, "issue": f"Invalid title: {title}"}

        return {"is_valid": True}

    def _is_category_header(self, title: str) -> bool:
        """Check if title is a category header rather than a job."""
        title_lower = title.lower().strip()
        word_count = len(title.split())

        # Single word or very short titles that are categories
        category_names = [
            'engineering', 'marketing', 'sales', 'finance', 'operations',
            'design', 'product', 'legal', 'hr', 'human resources', 'support',
            'customer success', 'business development', 'corporate', 'hardware',
            'software', 'research', 'data', 'analytics', 'counsel'
        ]

        if word_count <= 2:
            if title_lower in category_names or any(cat == title_lower for cat in category_names):
                return True

        # Check for category-like patterns
        if word_count <= 3:
            for cat in category_names:
                if title_lower == cat or title_lower == f"{cat} team":
                    return True

        return False

    def _is_garbage(self, title: str) -> bool:
        """Check if title is garbage/invalid data."""
        # Too many special characters
        special_chars = sum(1 for c in title if not c.isalnum() and c not in ' -,&/')
        if special_chars > len(title) * 0.3:
            return True

        # All caps or all lower with no spaces (likely code/ID)
        if title.isupper() and len(title) > 20:
            return True

        # Looks like a URL or ID
        if title.startswith('http') or title.startswith('/'):
            return True

        return False

    def _count_relevant_jobs(self, jobs: List[Dict], keywords: str) -> int:
        """Count jobs relevant to keywords."""
        keywords_lower = keywords.lower()
        keyword_terms = keywords_lower.replace(',', ' ').split()

        # Related terms
        related = {
            'data scientist': ['data science', 'machine learning', 'ml', 'analytics', 'ai'],
            'machine learning': ['ml', 'ai', 'data scientist', 'deep learning'],
            'software engineer': ['developer', 'swe', 'programmer'],
        }

        count = 0
        for job in jobs:
            title_lower = job.get("title", "").lower()

            # Direct match
            if any(term in title_lower for term in keyword_terms):
                count += 1
                continue

            # Related terms match
            for key, terms in related.items():
                if key in keywords_lower:
                    if any(term in title_lower for term in terms):
                        count += 1
                        break

        return count

    def _remove_duplicates(self, jobs: List[Dict]) -> tuple:
        """Remove duplicate jobs."""
        seen_titles = set()
        seen_urls = set()
        unique = []
        dup_count = 0

        for job in jobs:
            title = job.get("title", "").lower().strip()
            url = job.get("url", "")

            # Check URL duplicate
            if url and url in seen_urls:
                dup_count += 1
                continue

            # Check title duplicate
            if title in seen_titles:
                dup_count += 1
                continue

            seen_titles.add(title)
            if url:
                seen_urls.add(url)
            unique.append(job)

        return unique, dup_count
