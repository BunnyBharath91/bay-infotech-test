# Deployment Guide

This guide covers deploying the AI Help Desk platform to production using **Vercel (frontend)** and **Render (backend + PostgreSQL)**.

## Prerequisites

- ✅ GitHub account (with this repo pushed)
- ✅ Vercel account (free tier works)
- ✅ Render account (free tier works)
- ✅ Google Gemini API key ([Get it free here](https://aistudio.google.com/app/apikey))

## Architecture Overview

```
┌─────────────────────┐
│  Vercel (Frontend)  │ ← React app
└──────────┬──────────┘
           │ HTTPS
┌──────────▼──────────┐
│ Render (Backend)    │ ← FastAPI
│  + PostgreSQL       │
│  + pgvector         │
└─────────────────────┘
```

---

## Part 1: Database Setup (Neon)

### 1. Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign in
2. Click "New Project"
3. Name: `ai-helpdesk-db`
4. Region: Choose closest to your users
5. Click "Create Project"

### 2. Enable pgvector

Neon automatically includes pgvector. Verify with:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Get Connection String

1. In Neon dashboard, go to "Connection Details"
2. Copy the connection string (starts with `postgresql://`)
3. Save for later use

**Format:**
```
postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

For async use, change `postgresql://` to `postgresql+asyncpg://`:
```
postgresql+asyncpg://user:password@host.neon.tech/dbname?sslmode=require
```

---

## Part 2: Backend Deployment (Render)

### 1. Prepare Repository

Ensure your backend code is pushed to GitHub:

```bash
git add server/
git commit -m "Add backend implementation"
git push origin main
```

### 2. Create Render Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ai-helpdesk-backend`
   - **Region**: Same as Neon (or closest)
   - **Branch**: `main`
   - **Root Directory**: `server`
   - **Runtime**: `Docker`
   - **Instance Type**: `Starter` (or higher for production)

### 3. Environment Variables

Add these environment variables in Render:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/dbname?sslmode=require
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.0
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.5
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 4. Deploy

1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Wait for deployment to complete (~5-10 minutes)
4. Note your backend URL: `https://ai-helpdesk-backend.onrender.com`

### 5. Initialize Database

After first deployment, run initialization scripts:

```bash
# SSH into Render shell (or use Render dashboard shell)
python scripts/init_db.py
python scripts/ingest_kb.py
```

**Alternative**: Create a one-time job in Render:
1. New → Background Worker
2. Command: `python scripts/init_db.py && python scripts/ingest_kb.py`
3. Run once

---

## Part 3: Frontend Deployment (Vercel)

### 1. Prepare Frontend

Update API base URL in frontend:

Create `client/.env.production`:

```env
VITE_API_BASE_URL=https://ai-helpdesk-backend.onrender.com
```

Commit changes:

```bash
git add client/.env.production
git commit -m "Add production API URL"
git push origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `client`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 3. Environment Variables

Add in Vercel:

```env
VITE_API_BASE_URL=https://ai-helpdesk-backend.onrender.com
```

### 4. Deploy

1. Click "Deploy"
2. Wait for deployment (~2-3 minutes)
3. Note your frontend URL: `https://your-project.vercel.app`

### 5. Update CORS

Go back to Render and update `CORS_ORIGINS`:

```env
CORS_ORIGINS=https://your-project.vercel.app,http://localhost:5173
```

Redeploy backend.

---

## Part 4: Verification

### 1. Test Backend

```bash
curl https://ai-helpdesk-backend.onrender.com/health
# Should return: {"status":"healthy"}
```

### 2. Test Frontend

1. Open `https://your-project.vercel.app`
2. Send a test message: "How do I reset my password?"
3. Verify response is KB-grounded

### 3. Test Analytics

```bash
curl https://ai-helpdesk-backend.onrender.com/api/metrics/summary
# Should return metrics JSON
```

---

## Part 5: Monitoring

### Backend Monitoring (Render)

1. Go to Render dashboard → Your service
2. Click "Metrics" tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Response times
   - Error rates

### Database Monitoring (Neon)

1. Go to Neon dashboard → Your project
2. Click "Monitoring" tab
3. Monitor:
   - Connection count
   - Query performance
   - Storage usage

### Frontend Monitoring (Vercel)

1. Go to Vercel dashboard → Your project
2. Click "Analytics" tab
3. Monitor:
   - Page views
   - Response times
   - Error rates

---

## Troubleshooting

### Backend Won't Start

**Check logs in Render:**
1. Dashboard → Service → Logs
2. Look for errors in startup

**Common issues:**
- Missing environment variables
- Database connection failed
- Port already in use (should be 8000)

### Database Connection Failed

**Verify connection string:**
```bash
# Test connection
psql "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

**Check:**
- SSL mode is `require`
- Password is correct
- Database name exists

### KB Ingestion Failed

**Run manually:**
```bash
# In Render shell
cd /app
python scripts/init_db.py
python scripts/ingest_kb.py
```

**Check:**
- KB files exist in `server/kb/`
- Sentence Transformers model downloads successfully
- Database has pgvector extension enabled

### Frontend Can't Reach Backend

**Check CORS:**
- Backend `CORS_ORIGINS` includes frontend URL
- No trailing slashes in URLs

**Check API URL:**
- `VITE_API_BASE_URL` is correct
- HTTPS (not HTTP) for production

---

## Scaling

### Horizontal Scaling (Render)

1. Dashboard → Service → Settings
2. Increase instance count
3. Render handles load balancing automatically

### Database Scaling (Neon)

1. Dashboard → Project → Settings
2. Upgrade compute size
3. Enable autoscaling

### CDN (Vercel)

Vercel automatically uses CDN for static assets.

---

## Backup & Recovery

### Database Backups (Neon)

Neon automatically backs up daily. To restore:
1. Dashboard → Project → Backups
2. Select backup point
3. Click "Restore"

### Manual Backup

```bash
pg_dump "postgresql://user:password@host.neon.tech/dbname" > backup.sql
```

### Restore

```bash
psql "postgresql://user:password@host.neon.tech/dbname" < backup.sql
```

---

## Security Checklist

- [ ] Environment variables are not committed to Git
- [ ] Database uses SSL connections
- [ ] API keys are rotated regularly
- [ ] CORS is configured for production domains only
- [ ] Rate limiting is enabled (recommended)
- [ ] Logs don't contain sensitive data
- [ ] Database backups are enabled
- [ ] Monitoring alerts are configured

---

## Cost Estimates

### Neon (Database)
- Free tier: 0.5 GB storage, 100 hours compute/month
- Pro: ~$20/month for 10 GB + autoscaling

### Render (Backend)
- Free tier: 750 hours/month (sleeps after inactivity)
- Starter: $7/month (always on)
- Standard: $25/month (more resources)

### Vercel (Frontend)
- Free tier: Unlimited bandwidth for personal projects
- Pro: $20/month for production features

### LLM API
- OpenAI GPT-4: ~$0.03 per 1K tokens
- Anthropic Claude: ~$0.015 per 1K tokens
- Estimated: $50-200/month depending on usage

**Total estimated cost: $100-300/month for production**

---

## Next Steps

1. Set up monitoring alerts
2. Configure rate limiting
3. Add authentication (JWT)
4. Set up CI/CD pipeline
5. Create staging environment
6. Document runbooks for common issues
