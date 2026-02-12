"""
Agent 6: Resume Matcher Agent
Responsible for matching jobs to a resume based on skills and experience level.
"""
import re
import json
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field, asdict

from .base_agent import BaseAgent, AgentContext, AgentMessage, AgentStatus


@dataclass
class MatchResult:
    """Result of matching a job to a resume."""
    job_title: str
    company: str
    match_score: float  # 0-100
    skill_match: float  # 0-100
    level_match: float  # 0-100
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    level_assessment: str = ""  # "under-qualified", "good-fit", "over-qualified"
    recommendation: str = ""  # "strong", "moderate", "weak"
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ResumeProfile:
    """Extracted profile from resume."""
    skills: Set[str] = field(default_factory=set)
    years_experience: int = 0
    job_level: str = ""  # entry, mid, senior, staff, principal, manager, director
    titles: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)


class MatcherAgent(BaseAgent):
    """
    Matches jobs to resume based on skills and experience level.

    Analyzes:
    - Skill overlap between job requirements and resume
    - Experience level alignment
    - Title/role alignment
    - Overall fit score

    Can use LLM for deeper semantic matching.
    """

    # Job level hierarchy
    LEVEL_HIERARCHY = {
        'intern': 0,
        'entry': 1,
        'junior': 1,
        'associate': 2,
        'mid': 3,
        'senior': 4,
        'staff': 5,
        'principal': 6,
        'lead': 5,
        'manager': 5,
        'director': 7,
        'vp': 8,
        'head': 7,
        'chief': 9,
        'executive': 9
    }

    # Common tech skills for matching
    TECH_SKILLS = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
        'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'terraform',
        'react', 'angular', 'vue', 'node', 'django', 'flask', 'fastapi',
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'spark', 'hadoop', 'kafka', 'airflow',
        'git', 'ci/cd', 'agile', 'scrum'
    }

    def __init__(self, llm=None):
        super().__init__("MatcherAgent", llm)

    def execute(self, context: AgentContext, message: AgentMessage) -> AgentMessage:
        """Filter jobs by relevance and match against resume."""
        self.status = AgentStatus.RUNNING

        jobs = context.verified_jobs
        resume_data = context.resume_data

        if not jobs:
            return self._create_response(
                "orchestrator",
                "matching_failed",
                {},
                AgentStatus.FAILED,
                "No jobs to match"
            )

        self.log(f"Processing {len(jobs)} total jobs")

        if not self.llm:
            error_msg = "LLM is not available — matching requires an LLM for accurate scoring. Check your LLM config."
            self.log(error_msg)
            return self._create_response(
                "orchestrator",
                "matching_failed",
                {},
                AgentStatus.FAILED,
                error_msg
            )

        # Step 2: Extract resume profile
        profile = self._extract_resume_profile(resume_data)
        self.log(f"Resume profile: {len(profile.skills)} skills, level: {profile.job_level}")

        # Step 3: Match each job against resume
        matched_jobs = []
        for job in jobs:
            match_result = self._match_job(job, profile)
            matched_jobs.append({
                **job,
                "match_result": match_result.to_dict()
            })

        # Sort by match score (best matches first)
        matched_jobs.sort(key=lambda x: x["match_result"]["match_score"], reverse=True)

        # Discard weak matches (keep only strong and moderate)
        good_matches = [j for j in matched_jobs if j["match_result"]["recommendation"] in ("strong", "moderate")]
        discarded_weak = len(matched_jobs) - len(good_matches)

        # Store in context (only good matches)
        context.matched_jobs = good_matches

        # Summary stats
        strong_matches = sum(1 for j in good_matches if j["match_result"]["recommendation"] == "strong")
        moderate_matches = sum(1 for j in good_matches if j["match_result"]["recommendation"] == "moderate")

        self.log(f"Matching complete: {strong_matches} strong, {moderate_matches} moderate, "
                 f"{discarded_weak} weak discarded")

        return self._create_response(
            "orchestrator",
            "matching_complete",
            {
                "total_jobs": len(matched_jobs),
                "strong_matches": strong_matches,
                "moderate_matches": moderate_matches,
                "jobs": matched_jobs
            },
            AgentStatus.SUCCESS
        )

    def _extract_resume_profile(self, resume_data: Dict) -> ResumeProfile:
        """Extract structured profile from resume data."""
        profile = ResumeProfile()

        if not resume_data:
            return profile

        # Extract skills
        skills_raw = resume_data.get("skills", [])
        if isinstance(skills_raw, str):
            skills_raw = [s.strip() for s in skills_raw.split(',')]
        profile.skills = set(s.lower() for s in skills_raw)

        # Extract years of experience
        profile.years_experience = resume_data.get("years_experience", 0)

        # Extract job level from current/recent title
        titles = resume_data.get("titles", [])
        if titles:
            profile.titles = titles
            profile.job_level = self._infer_level_from_title(titles[0])

        # Extract education
        profile.education = resume_data.get("education", [])

        # If using LLM, enhance profile extraction
        if self.llm and resume_data.get("raw_text"):
            profile = self._llm_enhance_profile(profile, resume_data["raw_text"])

        return profile

    def _infer_level_from_title(self, title: str) -> str:
        """Infer job level from title."""
        title_lower = title.lower()

        for level, _ in sorted(self.LEVEL_HIERARCHY.items(), key=lambda x: -x[1]):
            if level in title_lower:
                return level

        # Default based on common patterns
        if 'intern' in title_lower:
            return 'intern'
        elif any(x in title_lower for x in ['junior', 'jr', 'entry']):
            return 'junior'
        elif any(x in title_lower for x in ['senior', 'sr']):
            return 'senior'
        elif 'staff' in title_lower:
            return 'staff'
        elif any(x in title_lower for x in ['lead', 'principal']):
            return 'principal'
        elif 'manager' in title_lower:
            return 'manager'
        elif 'director' in title_lower:
            return 'director'

        return 'mid'  # Default

    def _match_job(self, job: Dict, profile: ResumeProfile) -> MatchResult:
        """Match a single job against resume profile using LLM."""
        return self._llm_match_job(job, profile)

    def _llm_match_job(self, job: Dict, profile: ResumeProfile) -> MatchResult:
        """Use LLM for semantic job matching that considers role type, domain, and fit."""
        title = job.get("title", "")
        company = job.get("company", "")
        description = job.get("description", "")

        resume_titles = ", ".join(profile.titles[:3]) if profile.titles else "Unknown"
        resume_skills = ", ".join(list(profile.skills)[:20]) if profile.skills else "None listed"
        resume_level = profile.job_level or "unknown"

        prompt = f"""Score how well this job matches this candidate. Be STRICT and realistic.

CANDIDATE:
- Current/recent titles: {resume_titles}
- Level: {resume_level}
- Skills: {resume_skills}
- Years experience: {profile.years_experience}

JOB:
- Title: {title}
- Company: {company}
- Description: {description[:500] if description else 'Not available'}

Scoring rules:
- Role type mismatch (e.g., "Data Scientist" vs "Software Engineer" vs "ML Engineer") should significantly reduce the score. These are DIFFERENT roles.
- Domain/industry keywords in the job title (e.g., "Financial Crimes", "Healthcare", "Compliance") that don't appear in the candidate's background should reduce the score.
- Level mismatch (e.g., mid applying to director) should reduce the score.
- A perfect match means the candidate's role type, skills, domain experience, and level all align.

Return ONLY valid JSON, no other text:
{{{{
  "match_score": <0-100 integer>,
  "skill_match": <0-100 integer>,
  "level_match": <0-100 integer>,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "level_assessment": "<good-fit|stretch-role|over-qualified|under-qualified>",
  "recommendation": "<strong|moderate|weak>",
  "notes": "Brief explanation of the score"
}}}}"""

        try:
            response = self._call_llm(prompt, max_tokens=400)
            if response:
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return MatchResult(
                        job_title=title,
                        company=company,
                        match_score=min(100, max(0, float(data.get("match_score", 0)))),
                        skill_match=min(100, max(0, float(data.get("skill_match", 0)))),
                        level_match=min(100, max(0, float(data.get("level_match", 0)))),
                        matched_skills=data.get("matched_skills", []),
                        missing_skills=data.get("missing_skills", [])[:5],
                        level_assessment=data.get("level_assessment", ""),
                        recommendation=data.get("recommendation", "weak"),
                        notes=data.get("notes", "")
                    )
        except Exception as e:
            raise RuntimeError(f"LLM match failed for '{title}': {e}") from e

    def _heuristic_match_job(self, job: Dict, profile: ResumeProfile) -> MatchResult:
        """Fallback heuristic matching when LLM is unavailable."""
        title = job.get("title", "")
        company = job.get("company", "")
        description = job.get("description", "")

        # Extract job requirements
        job_skills = self._extract_job_skills(title, description)
        job_level = self._extract_job_level(title)

        # Calculate skill match
        matched_skills = profile.skills.intersection(job_skills)
        missing_skills = job_skills - profile.skills

        if job_skills:
            skill_match = (len(matched_skills) / len(job_skills)) * 100
        else:
            skill_match = self._fuzzy_skill_match(profile.skills, title, description)

        # Calculate level match
        level_match, level_assessment = self._calculate_level_match(profile.job_level, job_level)

        # Penalize role type mismatch (basic heuristic)
        role_penalty = self._role_type_penalty(profile.titles, title)
        skill_match = max(0, skill_match - role_penalty)

        # Calculate overall match score
        match_score = (skill_match * 0.6) + (level_match * 0.4)

        # Determine recommendation
        if match_score >= 70:
            recommendation = "strong"
        elif match_score >= 50:
            recommendation = "moderate"
        else:
            recommendation = "weak"

        notes = self._generate_notes(matched_skills, missing_skills, level_assessment)

        return MatchResult(
            job_title=title,
            company=company,
            match_score=round(match_score, 1),
            skill_match=round(skill_match, 1),
            level_match=round(level_match, 1),
            matched_skills=list(matched_skills),
            missing_skills=list(missing_skills)[:5],
            level_assessment=level_assessment,
            recommendation=recommendation,
            notes=notes
        )

    def _role_type_penalty(self, resume_titles: List[str], job_title: str) -> float:
        """Penalize when the role type fundamentally differs from resume."""
        if not resume_titles:
            return 0

        job_lower = job_title.lower()
        resume_lower = " ".join(t.lower() for t in resume_titles)

        # Define role families
        role_families = {
            "data_scientist": ["data scientist", "data science", "research scientist"],
            "ml_engineer": ["machine learning engineer", "ml engineer", "mlops"],
            "data_engineer": ["data engineer", "data platform", "etl"],
            "software_engineer": ["software engineer", "software developer", "backend engineer", "frontend engineer"],
            "analyst": ["data analyst", "business analyst", "analytics"],
            "manager": ["engineering manager", "data science manager", "ml manager"],
        }

        resume_family = None
        job_family = None
        for family, keywords in role_families.items():
            if any(kw in resume_lower for kw in keywords):
                resume_family = family
            if any(kw in job_lower for kw in keywords):
                job_family = family

        # Different role families = penalty
        if resume_family and job_family and resume_family != job_family:
            # Adjacent families get smaller penalty
            adjacent = {
                ("data_scientist", "ml_engineer"): 15,
                ("data_scientist", "analyst"): 15,
                ("data_scientist", "data_engineer"): 20,
                ("ml_engineer", "software_engineer"): 15,
                ("data_engineer", "software_engineer"): 15,
            }
            pair = tuple(sorted([resume_family, job_family]))
            return adjacent.get(pair, 30)  # Default: big penalty for unrelated roles

        return 0

    def _extract_job_skills(self, title: str, description: str) -> Set[str]:
        """Extract required skills from job title and description."""
        text = f"{title} {description}".lower()
        found_skills = set()

        for skill in self.TECH_SKILLS:
            if skill in text:
                found_skills.add(skill)

        # Also extract from title patterns
        title_lower = title.lower()
        if 'python' in title_lower:
            found_skills.add('python')
        if 'machine learning' in title_lower or 'ml' in title_lower:
            found_skills.add('machine learning')
        if 'data' in title_lower:
            found_skills.update(['sql', 'python'])
        if 'frontend' in title_lower or 'front-end' in title_lower:
            found_skills.update(['javascript', 'react'])
        if 'backend' in title_lower or 'back-end' in title_lower:
            found_skills.update(['python', 'sql'])

        return found_skills

    def _extract_job_level(self, title: str) -> str:
        """Extract job level from title."""
        return self._infer_level_from_title(title)

    def _calculate_level_match(self, resume_level: str, job_level: str) -> tuple:
        """Calculate level match score and assessment."""
        resume_rank = self.LEVEL_HIERARCHY.get(resume_level, 3)
        job_rank = self.LEVEL_HIERARCHY.get(job_level, 3)

        diff = resume_rank - job_rank

        if diff == 0:
            return 100, "good-fit"
        elif diff == 1:
            return 80, "slightly-over-qualified"
        elif diff == -1:
            return 80, "stretch-role"
        elif diff >= 2:
            return 50, "over-qualified"
        else:  # diff <= -2
            return 40, "under-qualified"

    def _fuzzy_skill_match(self, resume_skills: Set[str], title: str, description: str) -> float:
        """Fuzzy match when explicit skills not found."""
        text = f"{title} {description}".lower()
        matches = 0

        for skill in resume_skills:
            if skill in text:
                matches += 1

        if not resume_skills:
            return 50  # Default middle score

        return min(100, (matches / len(resume_skills)) * 150)  # Boost since partial match

    def _generate_notes(
        self,
        matched_skills: Set[str],
        missing_skills: Set[str],
        level_assessment: str
    ) -> str:
        """Generate human-readable notes about the match."""
        notes = []

        if matched_skills:
            notes.append(f"Matching skills: {', '.join(list(matched_skills)[:3])}")

        if missing_skills:
            notes.append(f"Consider learning: {', '.join(list(missing_skills)[:2])}")

        level_notes = {
            "good-fit": "Experience level aligns well",
            "slightly-over-qualified": "You may be slightly over-qualified",
            "stretch-role": "This would be a growth opportunity",
            "over-qualified": "Consider if this level is right for you",
            "under-qualified": "May need more experience for this role"
        }
        if level_assessment in level_notes:
            notes.append(level_notes[level_assessment])

        return ". ".join(notes)

    def _llm_enhance_profile(self, profile: ResumeProfile, raw_text: str) -> ResumeProfile:
        """Use LLM to enhance profile extraction."""
        prompt = f"""Extract skills and experience level from this resume text.

Resume:
{raw_text[:3000]}

Return JSON only:
{{
    "skills": ["skill1", "skill2", ...],
    "years_experience": number,
    "job_level": "junior|mid|senior|staff|principal|manager|director"
}}"""

        response = self._call_llm(prompt, max_tokens=500)
        if response:
            try:
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    if data.get("skills"):
                        profile.skills.update(s.lower() for s in data["skills"])
                    if data.get("years_experience"):
                        profile.years_experience = data["years_experience"]
                    if data.get("job_level"):
                        profile.job_level = data["job_level"]
            except:
                pass

        return profile
