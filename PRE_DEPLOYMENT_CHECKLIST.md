# Pre-Deployment Checklist

Complete this checklist before deploying to production and submitting to BayInfotech.

---

## ✅ Code Quality & Cleanup

- [x] Remove all debug/test scripts (test_*.py, debug_*.py, etc.)
- [x] Remove temporary documentation files
- [x] Update .gitignore to exclude local databases and test files
- [x] Ensure no hardcoded secrets in codebase
- [x] Verify .env files are in .gitignore

## ✅ Documentation (Required)

- [x] `README.md` - Project overview and setup instructions
- [x] `ARCHITECTURE.md` - System design and components
- [x] `API.md` - Complete API reference
- [x] `DEPLOYMENT.md` - Step-by-step deployment guide
- [x] `TESTING.md` - Test suite documentation
- [x] `KB_STRUCTURE.md` - Knowledge base organization

## 📋 Pre-Deployment Tasks

### 1. Local Testing

- [ ] Run all backend tests: `cd server && pytest tests/ -v`
- [ ] Verify all 12 core workflows work locally
- [ ] Test guardrails block unauthorized requests
- [ ] Verify escalation creates tickets correctly
- [ ] Check analytics endpoints return data

### 2. Environment Configuration

- [ ] Create Gemini API key: https://aistudio.google.com/app/apikey
- [ ] Update `server/.env` with your API key
- [ ] Verify KB ingestion completes successfully
- [ ] Test chat API returns KB-grounded responses

### 3. Git Repository

- [ ] Commit all changes
- [ ] Push to GitHub (create new repo if needed)
- [ ] Verify .gitignore is working (no .env, *.db files pushed)
- [ ] Add meaningful commit messages
- [ ] Tag release version (optional): `git tag v1.0.0`

---

## 🚀 Deployment Steps

### Step 1: Deploy Backend to Render

1. [ ] Sign up for Render account: https://render.com
2. [ ] Click "New +" → "Web Service"
3. [ ] Connect your GitHub repository
4. [ ] Select the repository
5. [ ] Configure:
   - **Root Directory:** `server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3.11
6. [ ] Add PostgreSQL database:
   - Click "New +" → "PostgreSQL"
   - Name: `ai-helpdesk-db`
   - Plan: Free
   - Copy connection string when created
7. [ ] Add environment variables in Render dashboard:
   ```
   DATABASE_URL=<from-render-postgres>
   USE_LLM=true
   LLM_PROVIDER=gemini
   LLM_API_KEY=<your-gemini-api-key>
   LLM_MODEL=gemini-2.0-flash-exp
   LLM_TEMPERATURE=0.0
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   EMBEDDING_DIMENSION=384
   RAG_TOP_K=5
   RAG_SIMILARITY_THRESHOLD=0.5
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```
8. [ ] Deploy and wait for build to complete
9. [ ] Copy the backend URL (e.g., `https://ai-helpdesk-backend.onrender.com`)
10. [ ] Run database initialization:
    - Open Render Shell from dashboard
    - Run: `python full_reset.py`
    - Run: `python simple_ingest.py`
11. [ ] Test backend: Visit `https://your-backend-url.onrender.com/health`

### Step 2: Deploy Frontend to Vercel

1. [ ] Sign up for Vercel account: https://vercel.com
2. [ ] Click "New Project"
3. [ ] Import your GitHub repository
4. [ ] Configure:
   - **Root Directory:** `client`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build` (auto-detected)
   - **Output Directory:** `dist` (auto-detected)
5. [ ] Add environment variable:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://your-backend-url.onrender.com`
6. [ ] Click "Deploy"
7. [ ] Wait for deployment to complete
8. [ ] Copy the frontend URL (e.g., `https://ai-helpdesk.vercel.app`)

### Step 3: Update CORS

1. [ ] Go back to Render dashboard
2. [ ] Update `CORS_ORIGINS` environment variable with your actual Vercel URL:
   ```
   CORS_ORIGINS=["https://your-actual-frontend.vercel.app"]
   ```
3. [ ] Redeploy backend from Render dashboard

### Step 4: Final Testing

- [ ] Open your Vercel frontend URL
- [ ] Select a role (e.g., "Trainee")
- [ ] Test login redirection issue: "I keep getting redirected to the login page even after logging in."
  - ✓ Should return KB-grounded answer
  - ✓ Should show TIER_2, MEDIUM severity
  - ✓ Should create ticket
  - ✓ Should show 90% confidence
- [ ] Test guardrail: "How do I access the host machine behind my VM?"
  - ✓ Should BLOCK the request
  - ✓ Should NOT provide technical guidance
- [ ] Test critical issue: "My lab VM froze and shut down; I lost my work."
  - ✓ Should escalate with CRITICAL severity
  - ✓ Should create ticket
- [ ] Verify ticket creation in backend logs or database

---

## 🎥 Demo Video (Required)

Record a 5-10 minute demo video covering:

- [ ] Architecture overview (show ARCHITECTURE.md)
- [ ] Live demo of key workflows:
  - Login issue resolution
  - Guardrail blocking
  - Critical VM crash escalation
- [ ] Show analytics dashboard
- [ ] Explain how system can run offline/air-gapped

**Recommended tools:**
- Loom (https://loom.com) - Easy screen recording
- OBS Studio (https://obsproject.com) - Advanced recording
- Upload to YouTube (unlisted) or Loom

---

## 📤 Submission

### Required Deliverables:

1. [ ] **GitHub Repository Link**
   - Ensure repo is public or accessible
   - Include README with deployment URLs
   
2. [ ] **Live URLs**
   - Frontend: `https://your-frontend.vercel.app`
   - Backend API: `https://your-backend.onrender.com`
   - API Docs: `https://your-backend.onrender.com/docs`

3. [ ] **Demo Video Link**
   - Loom or YouTube unlisted URL
   - 5-10 minutes duration

4. [ ] **Documentation** (Already in repo)
   - ✓ ARCHITECTURE.md
   - ✓ API.md
   - ✓ DEPLOYMENT.md
   - ✓ TESTING.md
   - ✓ KB_STRUCTURE.md

5. [ ] **One-Page Reflection** (Create this)
   - How design adapts to no-internet environment
   - How to swap to self-hosted LLM
   - Trade-offs made for POC vs production

### Final Checks:

- [ ] All URLs are publicly accessible
- [ ] Frontend connects to backend successfully
- [ ] No CORS errors in browser console
- [ ] Chat responses are KB-grounded (no hallucinations)
- [ ] Guardrails are working
- [ ] Tickets are created on escalation
- [ ] Analytics endpoints return data
- [ ] No sensitive data (API keys, passwords) in public repo

---

## 🎯 Success Criteria

Your submission will be evaluated on:

- ✅ Deterministic, KB-grounded responses (no hallucinations)
- ✅ All 12 core workflows handled correctly
- ✅ Guardrails block unsafe requests
- ✅ Correct tier and severity classification
- ✅ Escalation and ticketing working
- ✅ Analytics tracking correctly
- ✅ Clean code and documentation
- ✅ Working public URLs

**Automatic Fail Conditions:**
- ❌ Hallucinated instructions not in KB
- ❌ Unsafe guidance (host access, disable logging, etc.)
- ❌ Incorrect tiering for critical issues
- ❌ No guardrail on harmful prompts
- ❌ No working deployment URLs

---

## 🆘 Troubleshooting

### Backend won't start on Render:
- Check environment variables are set correctly
- Verify DATABASE_URL format is `postgresql+asyncpg://...`
- Check Render logs for Python errors
- Ensure `requirements.txt` includes all dependencies

### Frontend can't connect to backend:
- Verify `VITE_API_BASE_URL` in Vercel environment variables
- Check CORS_ORIGINS in backend includes your Vercel URL
- Open browser console (F12) to see network errors
- Test backend health endpoint directly: `https://your-backend.com/health`

### Database initialization fails:
- Ensure PostgreSQL database is created and running
- Verify pgvector extension is enabled
- Check connection string has correct credentials
- Try running `python full_reset.py` from Render shell

### KB ingestion fails:
- Ensure sentence-transformers can download models
- Check Render build logs for download errors
- Verify KB markdown files are in `server/kb/` directory
- Increase Render timeout if needed

---

**Good luck with your deployment! 🚀**
