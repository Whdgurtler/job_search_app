FROM python:3.11-slim AS builder

WORKDIR /app

# Install build deps in builder stage only
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (slim API-only requirements)
COPY backend/requirements-api.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-api.txt

# --- Final stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy backend code
COPY backend/ /app/backend/

# Copy existing project modules (agents, llm_analyzer, etc.)
COPY agents/ /app/agents/
COPY llm_analyzer.py resume_parser.py resume_file_parser.py \
     config.py company_discovery.py db.py /app/

WORKDIR /app/backend

EXPOSE 8080

# Railway sets PORT env var; default to 8080 for local/Cloud Run
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 4
