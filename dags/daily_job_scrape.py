"""
Airflow DAG: Daily Job Scrape

Runs every day at 7:00 AM, scrapes Airbnb, Block, and banking companies,
matches against the configured resume, and stores results in SQLite.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = r"C:\job-search-agent"
VENV_PYTHON = rf"{PROJECT_DIR}\.venv\Scripts\python.exe"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="daily_job_scrape",
    default_args=default_args,
    description="Scrape Airbnb, Block, and banking for job postings daily",
    schedule="0 7 * * *",  # Every day at 7:00 AM
    start_date=datetime(2026, 2, 9),
    catchup=False,
    tags=["jobs", "scraping"],
) as dag:

    scrape = BashOperator(
        task_id="run_daily_scrape",
        bash_command=f'cd /d "{PROJECT_DIR}" && "{VENV_PYTHON}" daily_scrape.py',
        execution_timeout=timedelta(minutes=30),
    )

    scrape
