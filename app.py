"""
Job Search Agent - Web Interface
Multi-agent architecture for intelligent job searching with resume matching.
Results stored in SQLite and loaded on startup with most recent first.
"""
import gradio as gr
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

# Set environment variables before imports
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'
os.environ['KMP_INIT_AT_FORK'] = 'FALSE'
os.environ['MKL_THREADING_LAYER'] = 'GNU'

from agents.orchestrator import JobScraperOrchestrator, create_job_scraper
from resume_parser import ResumeParser
from resume_file_parser import ResumeFileParser
from llm_analyzer import LLMAnalyzer
import db

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _jobs_to_dataframe(jobs: List[Dict]) -> pd.DataFrame:
    """Convert jobs list to a display DataFrame."""
    if not jobs:
        return pd.DataFrame()
    rows = []
    for job in jobs:
        match = job.get("match_result", {})
        # Support both nested match_result (from orchestrator) and flat (from DB)
        score = match.get("match_score", 0) if match else job.get("match_score", 0)
        rec = match.get("recommendation", "") if match else job.get("recommendation", "")
        level = match.get("level_assessment", "") if match else job.get("level_assessment", "")

        rows.append({
            'Date': job.get('scraped_date', ''),
            'Title': job.get('title', 'N/A'),
            'Company': job.get('company', 'N/A'),
            'Location': job.get('location', 'N/A'),
            'Remote': 'Yes' if job.get('is_remote', False) else '',
            'Match': f"{score}%" if score else '',
            'Fit': rec,
            'Level': level,
            'URL': job.get('url', ''),
        })
    return pd.DataFrame(rows)


def load_from_database(company_filter: str = "", remote_only: bool = False) -> tuple[pd.DataFrame, str, pd.DataFrame]:
    """Load jobs from SQLite, most recent first."""
    try:
        company = company_filter.strip() if company_filter else None
        jobs = db.get_recent_jobs(limit=500, company=company, remote_only=remote_only)

        # Build history table
        history = db.get_job_count_by_date()
        hist_df = pd.DataFrame(history) if history else pd.DataFrame()
        if not hist_df.empty:
            hist_df.columns = ['Date', 'Total Jobs', 'Strong', 'Moderate']

        if not jobs:
            return pd.DataFrame(), "No jobs in database yet. Run a search or wait for the daily scrape.", hist_df

        df = _jobs_to_dataframe(jobs)

        dates = df['Date'].nunique()
        companies = df['Company'].nunique()
        strong = sum(1 for j in jobs if j.get('recommendation') == 'strong')
        moderate = sum(1 for j in jobs if j.get('recommendation') == 'moderate')
        remote = sum(1 for j in jobs if j.get('is_remote'))

        msg = (f"**{len(jobs)} jobs** from {companies} companies across {dates} scrape date(s) "
               f"| {strong} strong, {moderate} moderate | {remote} remote")
        return df, msg, hist_df

    except Exception as e:
        return pd.DataFrame(), f"Error loading from database: {e}", pd.DataFrame()


def parse_resume_info(resume_file) -> tuple[str, str, dict]:
    """Extract key information from uploaded resume."""
    if resume_file is None:
        return "", "", {}

    try:
        file_parser = ResumeFileParser()
        llm = LLMAnalyzer()
        resume_parser = ResumeParser(llm)

        resume_text = file_parser.parse(resume_file.name)
        if not resume_text:
            return "Could not extract text from resume", "", {}

        resume_data = resume_parser.parse(resume_text)

        info = f"""### Resume Analysis

**Current Role:** {resume_data.current_title}
**Experience:** {resume_data.experience_years} years
**Level:** {resume_data.current_level}
**Leadership:** {'Yes' if resume_data.has_leadership_experience else 'No'}

**Skills:** {', '.join(resume_data.skills[:10])}

**Education:** {', '.join(resume_data.education)}
"""
        resume_dict = {
            "skills": resume_data.skills,
            "years_experience": resume_data.experience_years,
            "titles": [resume_data.current_title] + resume_data.past_titles,
            "education": resume_data.education,
            "raw_text": resume_text[:3000],
        }
        return info, resume_data.current_title, resume_dict

    except Exception as e:
        return f"Error parsing resume: {str(e)}", "", {}


def search_jobs_interface(
    keywords: str,
    companies_text: str,
    employment_area: str,
    location: str,
    resume_info_state: dict,
    progress=gr.Progress()
) -> tuple[pd.DataFrame, str]:
    """Search for jobs using the multi-agent orchestrator and store in DB."""

    if not keywords:
        return pd.DataFrame(), "Please enter search keywords"

    if not companies_text.strip() and not employment_area.strip():
        return pd.DataFrame(), "Please enter company names or an employment area"

    try:
        progress(0.05, desc="Initializing multi-agent system...")
        orchestrator = create_job_scraper(use_local_llm=False, headless=True)

        companies = None
        if companies_text.strip():
            companies = [c.strip() for c in companies_text.split(',') if c.strip()]

        resume_data = resume_info_state if resume_info_state else None

        progress(0.1, desc="Starting job search...")

        if companies:
            results = orchestrator.search_multiple_companies(
                companies=companies, keywords=keywords,
                location=location, resume_data=resume_data,
            )
        elif employment_area.strip():
            results = orchestrator.search_multiple_companies(
                employment_area=employment_area.strip(), keywords=keywords,
                location=location, resume_data=resume_data,
            )
        else:
            return pd.DataFrame(), "Please enter company names or an employment area"

        progress(0.9, desc="Saving to database...")

        all_jobs = []
        company_summaries = []
        errors = []

        for r in results:
            if r.success:
                all_jobs.extend(r.matched_jobs)
                company_summaries.append(f"  {r.company}: {r.jobs_found} jobs")
            else:
                errors.append(f"  {r.company}: {', '.join(r.errors)}")

        # Save to database
        today = datetime.now().strftime("%Y-%m-%d")
        inserted = db.save_jobs(all_jobs, scraped_date=today)
        searched_companies = [c for c in (companies or []) if c]
        db.save_run(today, searched_companies, keywords, len(all_jobs), errors,
                    sum(r.execution_time for r in results))

        progress(1.0, desc="Complete!")

        if not all_jobs:
            error_detail = "\n".join(errors) if errors else "No matching jobs found."
            return pd.DataFrame(), f"No jobs found.\n{error_detail}"

        df = _jobs_to_dataframe(all_jobs)

        company_list = "\n".join(company_summaries) if company_summaries else "None"
        strong = sum(1 for j in all_jobs if j.get('match_result', {}).get('recommendation') == 'strong')
        moderate = sum(1 for j in all_jobs if j.get('match_result', {}).get('recommendation') == 'moderate')
        remote_count = sum(1 for j in all_jobs if j.get('is_remote', False))

        message = f"""**Found {len(all_jobs)} matching jobs!** ({inserted} new in DB)

**Matches:** {strong} strong, {moderate} moderate
**Remote:** {remote_count} remote positions

**By Company:**
{company_list}"""

        if errors:
            message += f"\n\n**Errors:**\n" + "\n".join(errors)

        return df, message

    except Exception as e:
        return pd.DataFrame(), f"Error during search: {str(e)}"


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface():
    """Create the main Gradio interface."""

    with gr.Blocks(title="Job Search Agent") as demo:

        resume_data_state = gr.State({})

        gr.Markdown("""
        # Job Search Agent

        Multi-agent system that scrapes company career pages daily.
        Results are stored in a database - most recent scrape shown first.
        """)

        # ====================================================================
        # TAB 1: DASHBOARD (auto-loads from DB)
        # ====================================================================

        with gr.Tab("Dashboard"):
            gr.Markdown("### Latest Job Matches")

            with gr.Row():
                company_filter = gr.Dropdown(
                    label="Filter by Company",
                    choices=[""] + db.get_companies(),
                    value="",
                    allow_custom_value=True,
                )
                remote_filter = gr.Checkbox(label="Remote only", value=False)
                refresh_btn = gr.Button("Refresh", variant="secondary")

            dashboard_status = gr.Markdown()
            dashboard_table = gr.Dataframe(
                label="Jobs (most recent first)",
                interactive=False,
                wrap=True,
            )

            gr.Markdown("### Scrape History")
            history_table = gr.Dataframe(
                label="Daily Scrape Runs",
                interactive=False,
            )

            refresh_btn.click(
                fn=load_from_database,
                inputs=[company_filter, remote_filter],
                outputs=[dashboard_table, dashboard_status, history_table],
            )

            # Auto-load on startup
            demo.load(
                fn=load_from_database,
                inputs=[company_filter, remote_filter],
                outputs=[dashboard_table, dashboard_status, history_table],
            )

        # ====================================================================
        # TAB 2: MANUAL SEARCH
        # ====================================================================

        with gr.Tab("Search Jobs"):
            gr.Markdown("### Run a Manual Search")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Resume (Optional)")
                    resume_upload = gr.File(
                        label="Upload Resume",
                        file_types=[".pdf", ".docx", ".txt"],
                        type="filepath"
                    )
                    resume_parse_btn = gr.Button("Analyze Resume", variant="secondary")
                    resume_info = gr.Markdown()

                with gr.Column(scale=2):
                    gr.Markdown("#### Search Parameters")
                    keywords_input = gr.Textbox(
                        label="Keywords / Job Title",
                        placeholder="e.g., Data Scientist, Machine Learning Engineer",
                        lines=1,
                    )
                    companies_input = gr.Textbox(
                        label="Target Companies (comma-separated)",
                        placeholder="e.g., Block, Airbnb, Stripe",
                        lines=2,
                    )
                    employment_area_input = gr.Textbox(
                        label="Employment Area (alternative to companies)",
                        placeholder="e.g., Fintech, Big Tech, Banking",
                        lines=1,
                    )
                    location_input = gr.Textbox(
                        label="Location",
                        value="",
                        placeholder="e.g., Remote, San Francisco",
                    )

            search_btn = gr.Button("Search Jobs", variant="primary")
            search_status = gr.Markdown()
            search_table = gr.Dataframe(
                label="Search Results",
                interactive=False,
                wrap=True,
            )

            def on_parse_resume(resume_file):
                info, kw, data = parse_resume_info(resume_file)
                return info, kw, data

            resume_parse_btn.click(
                fn=on_parse_resume,
                inputs=[resume_upload],
                outputs=[resume_info, keywords_input, resume_data_state],
            )

            search_btn.click(
                fn=search_jobs_interface,
                inputs=[
                    keywords_input, companies_input,
                    employment_area_input, location_input,
                    resume_data_state,
                ],
                outputs=[search_table, search_status],
            )

        # ====================================================================
        # TAB 3: HELP
        # ====================================================================

        with gr.Tab("Help"):
            gr.Markdown("""
            ## How It Works

            **Daily automated scraping** runs at 7:00 AM via Airflow:
            - **Airbnb** and **Block** career pages
            - **Banking** sector companies (JPMorgan, Goldman Sachs, Capital One, etc.)
            - Matches all jobs against your resume

            Results are stored in a **SQLite database** and shown here, most recent first.

            ### Manual Search

            You can also run ad-hoc searches from the "Search Jobs" tab for any company.

            ### Results Columns

            - **Date**: When the job was scraped
            - **Match**: Overall match score (0-100%)
            - **Fit**: strong or moderate recommendation
            - **Level**: How your experience fits (good-fit, stretch-role, etc.)
            - **Remote**: Whether the position is remote

            ### Airflow Schedule

            The DAG `daily_job_scrape` runs at `0 7 * * *` (7 AM daily).
            To change targets, edit `daily_scrape.py`.
            """)

        gr.Markdown("---\nPowered by multi-agent AI job matching | Daily scrapes via Airflow")

    return demo


# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7862,
        show_error=True,
    )
