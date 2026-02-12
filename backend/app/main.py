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
