FROM python:3.14-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app/backend/

# Copy existing project modules (agents, llm_analyzer, etc.)
COPY ../agents /app/agents
COPY ../llm_analyzer.py ../resume_parser.py ../resume_file_parser.py \
     ../config.py ../company_discovery.py ../db.py /app/

WORKDIR /app/backend

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
