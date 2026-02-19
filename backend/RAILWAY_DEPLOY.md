# Railway Deployment Guide

## Overview

This deploys 3 services on Railway:
- **API** - FastAPI backend (from `backend/Dockerfile`)
- **Worker** - Celery worker (from `backend/Dockerfile.worker`)
- **Redis** - Message broker (Railway plugin)

PostgreSQL is also added as a Railway plugin.

## Step 1: Create Railway Project

1. Go to [railway.com](https://railway.com) and sign in with GitHub
2. Click **New Project** > **Deploy from GitHub repo**
3. Select `Whdgurtler/job_search_app`

## Step 2: Add Databases

In your Railway project dashboard:

1. Click **+ New** > **Database** > **Add PostgreSQL**
2. Click **+ New** > **Database** > **Add Redis**

Railway auto-provisions these and provides connection URLs.

## Step 3: Deploy the API Service

The initial deploy from GitHub creates one service. Configure it:

1. Click the service > **Settings**:
   - **Root Directory**: leave empty (Dockerfile uses project root as build context)
   - **Custom Dockerfile Path**: `backend/Dockerfile`
   - **Watch Paths**: `/backend/**`

2. Click **Variables** and add:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ENVIRONMENT=production
   HUGGINGFACE_API_KEY=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
   FIREBASE_PROJECT_ID=your-firebase-project-id
   ```

   Note: `${{Postgres.DATABASE_URL}}` and `${{Redis.REDIS_URL}}` are Railway
   reference variables that auto-fill from your database plugins.

   **Important:** The default DATABASE_URL from Railway uses `postgresql://`.
   SQLAlchemy async requires `postgresql+asyncpg://`. Add this variable:
   ```
   DATABASE_URL_SYNC=${{Postgres.DATABASE_URL}}
   ```
   Then set DATABASE_URL manually by copying the Postgres URL and changing
   `postgresql://` to `postgresql+asyncpg://`.

3. Click **Settings** > **Networking** > **Generate Domain** to get a public URL

## Step 4: Deploy the Worker Service

1. In your project, click **+ New** > **GitHub Repo** > select the same repo
2. This creates a second service. Configure it:
   - **Settings** > **Custom Dockerfile Path**: `backend/Dockerfile.worker`
   - **Settings** > **Watch Paths**: `/backend/**`, `/agents/**`

3. Add the same environment variables as the API service

4. In **Settings** > **Networking**, do NOT generate a domain (worker doesn't serve HTTP)

## Step 5: Run Migrations

Option A - Railway CLI:
```bash
npm install -g @railway/cli
railway login
railway link  # select your project
railway run -s api -- alembic -c backend/alembic.ini upgrade head
```

Option B - Add a one-off service:
1. In Railway, click **+ New** > **GitHub Repo** (same repo)
2. Set Dockerfile to `backend/Dockerfile`
3. Override start command: `alembic -c alembic.ini upgrade head`
4. Add DATABASE_URL variable
5. After it runs successfully, delete the service

## Step 6: Verify

Your API URL will be something like:
```
https://job-search-app-production-xxxx.up.railway.app
```

Test it:
```bash
curl https://your-api-url.up.railway.app/health
# Should return: {"status":"ok","version":"1.0.0"}
```

## Step 7: Update Flutter App

Update your Flutter `.env.prod` (or equivalent):
```
API_BASE_URL=https://your-api-url.up.railway.app/api/v1
```

Then rebuild: `flutter build appbundle --release`

## Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| API (hobby plan) | ~$5 |
| Worker | ~$5-10 |
| PostgreSQL | included |
| Redis | included |
| **Total** | **~$5-15/mo** |

Railway's Hobby plan is $5/month with $5 of usage included. Much cheaper than
Cloud Run for low-traffic apps.
