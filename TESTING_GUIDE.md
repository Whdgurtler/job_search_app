# Quick Start: Testing Phase 1 Backend

## Prerequisites

1. **Install Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and restart
   - Verify: `docker --version` and `docker-compose --version`

2. **Firebase Admin SDK Setup** (Optional for initial test)
   - Go to Firebase Console → Project Settings → Service Accounts
   - Generate new private key (JSON)
   - Save as `backend/firebase-credentials.json`
   - Add to `.gitignore` (already done)

3. **Environment Variables**
   - Copy `backend/.env.example` to `backend/.env`
   - Update values (DATABASE_URL, REDIS_URL, etc.)

## Quick Test (No Firebase)

### 1. Start Services

```bash
cd C:\job-search-agent\backend
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- API server on port 8000
- Celery worker

### 2. Run Database Migration

```bash
docker-compose exec api alembic upgrade head
```

### 3. Test API Health

```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health -Method GET

# Or use browser:
http://localhost:8000/docs  # Swagger UI
```

### 4. Create Test User (Direct SQL)

```sql
-- Connect to PostgreSQL
docker-compose exec postgres psql -U jobsearch

INSERT INTO users (firebase_uid, email, is_active, quota_scrapes_per_day, plan)
VALUES ('test-user-123', 'test@example.com', true, 5, 'free');

-- Get user ID
SELECT id, email FROM users;
```

### 5. Test Resume Upload (Mock)

Create test file: `test_resume.txt`
```
John Doe
Senior Machine Learning Engineer

EXPERIENCE
- 5 years ML experience
- Python, TensorFlow, PyTorch
- Built recommendation systems

EDUCATION
- MS Computer Science, Stanford
```

```bash
# Upload (will need auth token - see below)
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer <test-token>" \
  -F "file=@test_resume.txt" \
  -F "filename=john_doe_resume.txt"
```

### 6. Trigger Scrape

```bash
curl -X POST http://localhost:8000/api/v1/scrapes/trigger \
  -H "Authorization: Bearer <test-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "companies": ["Airbnb", "Block"],
    "keywords": "machine learning engineer"
  }'
```

### 7. Check Scrape Status

```bash
curl http://localhost:8000/api/v1/scrapes/{run_id}/status \
  -H "Authorization: Bearer <test-token>"
```

### 8. List Jobs

```bash
curl "http://localhost:8000/api/v1/jobs?page=1&per_page=20" \
  -H "Authorization: Bearer <test-token>"
```

## Mock Auth (For Testing Without Firebase)

Create a bypass in `backend/app/dependencies.py`:

```python
# Temporary testing bypass
async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    # Mock user for testing
    result = await db.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Test user not found")
    return user
```

Then restart API:
```bash
docker-compose restart api
```

## Check Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f postgres
```

## Verify Celery Task

```bash
# Check worker logs for task execution
docker-compose logs worker | grep "run_scrape"

# Check database for jobs
docker-compose exec postgres psql -U jobsearch -c "SELECT COUNT(*) FROM jobs;"
```

## Troubleshooting

### API won't start
```bash
docker-compose logs api
# Common: Missing dependencies, wrong Python path
```

### Worker can't connect to Redis
```bash
docker-compose logs worker
# Check redis container: docker-compose ps redis
```

### Database connection error
```bash
docker-compose logs postgres
# Check if PostgreSQL started: docker-compose ps postgres
```

### Alembic migration fails
```bash
# Check migration script
cat backend/alembic/versions/1a9d32737874_*.py

# Try manual migration
docker-compose exec api alembic current
docker-compose exec api alembic upgrade head --sql > migration.sql
```

## Full Test Script

Save as `backend/test_api.ps1`:

```powershell
# Start stack
docker-compose up -d
Start-Sleep -Seconds 10

# Run migration
docker-compose exec -T api alembic upgrade head

# Create test user
docker-compose exec -T postgres psql -U jobsearch -c "
INSERT INTO users (firebase_uid, email, is_active, quota_scrapes_per_day, plan)
VALUES ('test-123', 'test@test.com', true, 5, 'free')
ON CONFLICT (email) DO NOTHING;
"

# Health check
$response = Invoke-WebRequest -Uri http://localhost:8000/health
Write-Host "API Health:" $response.StatusCode

# Open Swagger
Start-Process "http://localhost:8000/docs"

Write-Host "✅ Backend ready at http://localhost:8000"
Write-Host "📚 Docs at http://localhost:8000/docs"
Write-Host "🔍 Logs: docker-compose logs -f"
```

Run: `.\test_api.ps1`

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes (DELETES DATA)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Next Steps After Testing

1. ✅ Verify all endpoints work
2. ✅ Confirm Celery executes scrape_task
3. ✅ Check jobs inserted into PostgreSQL
4. 🎯 Move to Phase 2: Celery polish + error handling
5. 🎯 Start Phase 3: Flutter mobile development

## Useful Commands

```bash
# Shell into API container
docker-compose exec api bash

# Shell into PostgreSQL
docker-compose exec postgres psql -U jobsearch

# Check Celery worker status
docker-compose exec worker celery -A app.tasks.celery_app inspect active

# Monitor Redis
docker-compose exec redis redis-cli MONITOR

# Restart single service
docker-compose restart api

# View service resource usage
docker stats
```
