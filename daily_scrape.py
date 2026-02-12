"""
Daily job scrape script.
Runs the multi-agent orchestrator for configured targets and stores results in SQLite.

Usage:
    python daily_scrape.py                  # Run with defaults
    python daily_scrape.py --keywords "ML Engineer"  # Override keywords
"""
import sys
import os
import time
import argparse
from datetime import date
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'
os.environ['KMP_INIT_AT_FORK'] = 'FALSE'
os.environ['MKL_THREADING_LAYER'] = 'GNU'

from agents.orchestrator import create_job_scraper
from resume_file_parser import ResumeFileParser
from resume_parser import ResumeParser
from llm_analyzer import LLMAnalyzer
import db

# ============================================================================
# CONFIGURATION - edit these to change daily targets
# ============================================================================

RESUME_PATH = r"C:\Users\whdgu\OneDrive\Desktop\W_Gurtler.docx"

# Specific companies to scrape every day
COMPANIES = ["Airbnb", "Block"]

# Employment areas to discover companies from
EMPLOYMENT_AREAS = ["banking"]

# Default keywords (overridden by resume if available)
DEFAULT_KEYWORDS = "Data Scientist"


def parse_resume(resume_path: str) -> dict:
    """Parse resume file into a dict for the orchestrator."""
    if not os.path.exists(resume_path):
        print(f"Resume not found: {resume_path}")
        return {}

    try:
        file_parser = ResumeFileParser()
        llm = LLMAnalyzer()
        parser = ResumeParser(llm)

        text = file_parser.parse(resume_path)
        if not text:
            print("Could not extract text from resume")
            return {}

        data = parser.parse(text)
        print(f"Resume parsed: {data.current_title}, {data.experience_years}y, "
              f"{len(data.skills)} skills")

        return {
            "skills": data.skills,
            "years_experience": data.experience_years,
            "titles": [data.current_title] + data.past_titles,
            "education": data.education,
            "raw_text": text[:3000],
            "current_title": data.current_title,
        }
    except Exception as e:
        print(f"Resume parse error: {e}")
        return {}


def run_daily_scrape(keywords: str = None):
    """Execute the daily scrape for all configured targets."""
    start = time.time()
    today = date.today().isoformat()

    print(f"{'='*60}")
    print(f"Daily Job Scrape - {today}")
    print(f"{'='*60}")

    # Parse resume
    resume_data = parse_resume(RESUME_PATH)
    kw = keywords or resume_data.get("current_title") or DEFAULT_KEYWORDS
    print(f"Keywords: {kw}")

    all_jobs = []
    all_errors = []
    all_companies = []

    orchestrator = create_job_scraper(headless=True)

    # 1) Scrape specific companies
    if COMPANIES:
        print(f"\n--- Scraping companies: {', '.join(COMPANIES)} ---")
        results = orchestrator.search_multiple_companies(
            companies=COMPANIES,
            keywords=kw,
            resume_data=resume_data,
        )
        for r in results:
            all_companies.append(r.company)
            if r.success:
                all_jobs.extend(r.matched_jobs)
                print(f"  {r.company}: {r.jobs_found} jobs ({r.execution_time:.0f}s)")
            else:
                all_errors.extend(r.errors)
                print(f"  {r.company}: FAILED - {r.errors}")

    # 2) Scrape employment areas
    for area in EMPLOYMENT_AREAS:
        print(f"\n--- Discovering companies for: {area} ---")
        try:
            results = orchestrator.search_multiple_companies(
                employment_area=area,
                keywords=kw,
                resume_data=resume_data,
                max_companies=40,
            )
            for r in results:
                all_companies.append(r.company)
                if r.success:
                    all_jobs.extend(r.matched_jobs)
                    print(f"  {r.company}: {r.jobs_found} jobs ({r.execution_time:.0f}s)")
                else:
                    all_errors.extend(r.errors)
                    print(f"  {r.company}: FAILED - {r.errors}")
        except Exception as e:
            msg = f"Area '{area}' failed: {e}"
            all_errors.append(msg)
            print(f"  {msg}")

    # 3) Store results in database
    duration = time.time() - start
    save_result = db.save_jobs(all_jobs, scraped_date=today)
    db.save_run(today, all_companies, kw, len(all_jobs), all_errors, duration)

    print(f"\n{'='*60}")
    print(f"COMPLETE: {len(all_jobs)} jobs found, "
          f"{save_result['inserted']} new, {save_result['updated']} updated")
    print(f"Companies: {', '.join(all_companies)}")
    print(f"Errors: {len(all_errors)}")
    print(f"Duration: {duration:.0f}s")
    print(f"{'='*60}")

    return len(all_jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily job scrape")
    parser.add_argument("--keywords", type=str, default=None,
                        help="Override keywords (default: from resume)")
    args = parser.parse_args()
    run_daily_scrape(keywords=args.keywords)
