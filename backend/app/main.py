"""FastAPI application entry point."""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.auth.firebase import init_firebase
from app.routers import auth, users, resumes, jobs, scrapes

# Add project root to path so existing modules (agents, llm_analyzer, etc.) are importable
settings = get_settings()
sys.path.insert(0, settings.project_root)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Create database tables if they don't exist
    from app.db.base import Base
    from app.db.session import engine
    # Import all models so Base.metadata knows about them
    import app.models.user  # noqa: F401
    import app.models.job  # noqa: F401
    import app.models.resume  # noqa: F401
    import app.models.scrape  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables ensured.")

    # Initialize Firebase on startup
    try:
        init_firebase()
    except Exception as e:
        print(f"Warning: Firebase init failed ({e}). Auth will not work.")
    yield


app = FastAPI(
    title="Job Search Agent API",
    version=settings.api_version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["resumes"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(scrapes.router, prefix="/api/v1", tags=["scrapes"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.api_version}


@app.get("/health/worker")
async def worker_health_check():
    """Check if the Celery worker and Redis broker are reachable."""
    from app.tasks.celery_app import celery_app
    try:
        result = celery_app.control.ping(timeout=3.0)
        workers = [name for resp in result for name in resp]
        if workers:
            return {"status": "ok", "workers": workers}
        return {"status": "degraded", "detail": "No workers responded"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
