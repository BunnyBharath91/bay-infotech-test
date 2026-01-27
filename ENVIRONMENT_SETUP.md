# Environment Variables Setup Guide

This guide explains how to configure environment variables for local development and production deployment.

---

## 📁 Environment Files Structure

```
bay-infotech-test/
├── server/
│   ├── .env.example        ← Template (commit to Git)
│   └── .env                ← Your local config (DO NOT commit)
│
└── client/
    ├── .env.example        ← Template (commit to Git)
    └── .env                ← Your local config (DO NOT commit)
```

**Important:** 
- ✅ `.env.example` files are committed to Git (templates for others)
- ❌ `.env` files are in `.gitignore` (contain your actual secrets)

---

## 🖥️ Local Development Setup

### Step 1: Backend Environment

```bash
cd server
cp .env.example .env
```

Edit `server/.env`:

```env
# Use SQLite for local development (easiest)
DATABASE_URL=sqlite+aiosqlite:///./helpdesk.db

# Get your FREE Gemini API key from:
# https://aistudio.google.com/app/apikey
LLM_API_KEY=your-actual-gemini-api-key-here

# Keep everything else as default
USE_LLM=true
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
```

### Step 2: Frontend Environment

```bash
cd client
cp .env.example .env
```

Edit `client/.env`:

```env
# Point to your local backend
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Initialize Database

```bash
cd server
python full_reset.py       # Create tables
python simple_ingest.py    # Load KB
```

### Step 4: Start Services

```bash
# Terminal 1 - Backend
cd server
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd client
npm run dev
```

Access: http://localhost:5173

---

## 🚀 Production Deployment

### Backend (Render)

When deploying to Render, **DO NOT** create a `.env` file. Instead, set environment variables in the Render dashboard:

**Dashboard → Your Service → Environment**

```env
# Database (from Render PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host.render.com/dbname

# LLM Configuration
USE_LLM=true
LLM_PROVIDER=gemini
LLM_API_KEY=your-actual-gemini-api-key
LLM_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.0

# Embeddings (no changes needed)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.5

# CORS (update with your actual Vercel URL)
CORS_ORIGINS=["https://your-frontend.vercel.app"]

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Frontend (Vercel)

When deploying to Vercel, set environment variable in Vercel dashboard:

**Dashboard → Your Project → Settings → Environment Variables**

```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## 🔑 Getting API Keys

### Gemini (Recommended - Free)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Paste into `LLM_API_KEY` in your `.env`

**Free Tier Limits:**
- 15 requests per minute
- 1,500 requests per day
- Plenty for development and demo

### OpenAI (Alternative - Paid)

1. Go to https://platform.openai.com/api-keys
2. Sign in and create new API key
3. Copy key (starts with `sk-...`)
4. Update `.env`:
   ```env
   LLM_PROVIDER=openai
   LLM_API_KEY=sk-your-key-here
   LLM_MODEL=gpt-4
   ```

---

## 🗄️ Database Options

### Option 1: SQLite (Local Dev - Easiest)

```env
DATABASE_URL=sqlite+aiosqlite:///./helpdesk.db
```

**Pros:**
- No setup required
- Works immediately
- Perfect for development

**Cons:**
- Slower vector search (in-memory cosine similarity)
- Single file database
- Not suitable for production

### Option 2: PostgreSQL (Production)

**Render (Recommended):**
1. Create PostgreSQL database in Render
2. Copy connection string from dashboard
3. Add to environment variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@host.render.com/dbname
```

**Neon (Alternative):**
1. Create project at https://neon.tech
2. Copy connection string
3. Change `postgresql://` to `postgresql+asyncpg://`

```env
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/dbname?sslmode=require
```

---

## ⚙️ Configuration Options

### LLM Providers

```env
# Gemini (Free tier available)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp

# OpenAI (Paid)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# Anthropic (Paid)
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229

# Mock (Testing, no API key needed)
LLM_PROVIDER=mock

# KB-Only Mode (No LLM, instant responses)
USE_LLM=false
```

### CORS Configuration

**Development:**
```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**Production:**
```env
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

**Both:**
```env
CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:5173"]
```

---

## 🔒 Security Best Practices

### DO ✅

- Keep `.env` files out of Git (they're in `.gitignore`)
- Use `.env.example` as templates (commit these)
- Rotate API keys regularly
- Use environment variables on hosting platforms (Render, Vercel)
- Use different API keys for dev/staging/prod

### DON'T ❌

- Never commit `.env` files to Git
- Never hardcode API keys in source code
- Never share `.env` files via email/chat
- Never use production keys in development
- Never log API keys in application logs

---

## 🐛 Troubleshooting

### "Module not found" or import errors

```bash
cd server
pip install -r requirements.txt
```

### "Database not found"

```bash
cd server
python full_reset.py
python simple_ingest.py
```

### "Invalid API key"

- Check your `.env` has correct `LLM_API_KEY`
- Verify key is active at https://aistudio.google.com/app/apikey
- Try regenerating the key

### "CORS policy error" in browser

- Check backend `CORS_ORIGINS` includes your frontend URL
- Restart backend after changing `.env`
- Clear browser cache

### Frontend can't connect to backend

- Verify `VITE_API_BASE_URL` in `client/.env`
- Check backend is running on http://localhost:8000
- Test backend directly: `curl http://localhost:8000/health`

---

## 📚 Additional Resources

- **Gemini API Docs:** https://ai.google.dev/docs
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Vite Docs:** https://vitejs.dev

---

**Need help?** Check [DEPLOYMENT.md](./DEPLOYMENT.md) for full deployment instructions.
