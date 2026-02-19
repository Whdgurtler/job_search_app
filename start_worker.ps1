# Start Celery Worker

# Set environment variables  
$env:DATABASE_URL = "postgresql+asyncpg://jobsearch:localdev@localhost:5432/jobsearch"
$env:DATABASE_URL_SYNC = "postgresql://jobsearch:localdev@localhost:5432/jobsearch"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:ENVIRONMENT = "development"

# Change to backend directory and add to Python path
Set-Location C:\job-search-agent\backend
$env:PYTHONPATH = "C:\job-search-agent\backend;C:\job-search-agent"

Write-Host "Starting Celery Worker..."
Write-Host "Broker: redis://localhost:6379/0"
Write-Host ""

# Run celery worker
..\.venv\Scripts\python.exe -m celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
