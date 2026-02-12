"""Celery task that runs the job scraper orchestrator.

This will be fully implemented in Phase 2. Stub provided for scaffolding.
"""
from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, name="run_scrape")
def run_scrape(self, run_id: str, user_id: str, config: dict):
    """Execute a scrape run for a user.

    Phase 2 implementation will:
    1. Load user's active resume from PostgreSQL
    2. Create a PostgresDBAdapter for user-scoped dedup queries
    3. Create JobScraperOrchestrator with the adapter
    4. Run orchestrator.search_multiple_companies()
    5. Write results to PostgreSQL jobs table
    6. Update scrape_runs status
    """
    # TODO: Phase 2 implementation
    raise NotImplementedError("Scrape task will be implemented in Phase 2")
