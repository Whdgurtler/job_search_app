# Google Cloud Run Deployment Guide

## Prerequisites

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. A GCP project with billing enabled

## Step 1: Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com
```

## Step 2: Create Infrastructure

### Artifact Registry (Docker images)
```bash
gcloud artifacts repositories create jobsearch \
  --repository-format=docker \
  --location=us-central1
```

### Cloud SQL (PostgreSQL)
```bash
gcloud sql instances create jobsearch-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_SECURE_PASSWORD

gcloud sql databases create jobsearch --instance=jobsearch-db

gcloud sql users create jobsearch \
  --instance=jobsearch-db \
  --password=YOUR_SECURE_PASSWORD
```

### Memorystore (Redis)
```bash
gcloud redis instances create jobsearch-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0 \
  --tier=basic
```

## Step 3: Store Secrets

```bash
# Database URL
echo -n "postgresql+asyncpg://jobsearch:PASSWORD@/jobsearch?host=/cloudsql/PROJECT_ID:us-central1:jobsearch-db" | \
  gcloud secrets create DATABASE_URL --data-file=-

# Redis URL (get IP from: gcloud redis instances describe jobsearch-redis --region=us-central1)
echo -n "redis://REDIS_IP:6379/0" | \
  gcloud secrets create REDIS_URL --data-file=-

# Firebase credentials
gcloud secrets create FIREBASE_CREDENTIALS --data-file=firebase-credentials.json
```

## Step 4: Deploy

```bash
# From the project root directory:
gcloud builds submit --config backend/cloudbuild.yaml .
```

## Step 5: Run Migrations

```bash
# Connect to Cloud SQL proxy and run migrations
gcloud run jobs create migrate \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/jobsearch/jobsearch-api:latest \
  --region=us-central1 \
  --command="alembic" \
  --args="upgrade,head" \
  --set-cloudsql-instances=PROJECT_ID:us-central1:jobsearch-db

gcloud run jobs execute migrate --region=us-central1
```

## Step 6: Get API URL

```bash
gcloud run services describe jobsearch-api --region=us-central1 --format='value(status.url)'
```

Use this URL to update your Flutter `.env.prod`:
```
API_BASE_URL=https://jobsearch-api-XXXXX-uc.a.run.app/api/v1
```

## Cost Estimate (Low Traffic)

| Service | Monthly Cost |
|---------|-------------|
| Cloud Run API (min 0) | ~$0-5 |
| Cloud Run Worker (min 1) | ~$15-25 |
| Cloud SQL (f1-micro) | ~$8 |
| Memorystore (1GB basic) | ~$35 |
| **Total** | **~$58-73/mo** |

For a cheaper start, consider using [Railway](https://railway.app) or [Render](https://render.com) which offer simpler setup at lower costs for low-traffic apps.
