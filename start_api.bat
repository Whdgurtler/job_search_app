@echo off
cd /d C:\job-search-agent\backend

set DATABASE_URL=postgresql+asyncpg://jobsearch:localdev@localhost:5432/jobsearch
set DATABASE_URL_SYNC=postgresql://jobsearch:localdev@localhost:5432/jobsearch
set REDIS_URL=redis://localhost:6379/0
set ENVIRONMENT=development
set PYTHONPATH=C:\job-search-agent\backend;C:\job-search-agent

echo Starting FastAPI Server...
echo Database: %DATABASE_URL%
echo.

..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
