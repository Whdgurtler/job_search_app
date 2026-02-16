# Start FastAPI development server

# Set environment variables
$env:DATABASE_URL = "postgresql+asyncpg://jobsearch:localdev@localhost:5432/jobsearch"
$env:DATABASE_URL_SYNC = "postgresql://jobsearch:localdev@localhost:5432/jobsearch"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:ENVIRONMENT = "development"

# Change to backend directory and add parent to Python path
Set-Location C:\job-search-agent\backend
$env:PYTHONPATH = "C:\job-search-agent\backend;C:\job-search-agent"

Write-Host "Starting FastAPI server at http://localhost:8000"
Write-Host "Docs available at http://localhost:8000/docs"
Write-Host ""

# Run uvicorn
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
