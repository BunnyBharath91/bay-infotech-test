# Deploy Client to Vercel via CLI

This project is configured for Vercel deployment. Use the Vercel CLI to deploy from your machine.

## Prerequisites

- Node.js 18+
- A [Vercel account](https://vercel.com/signup)
- Backend API URL: `https://bay-infotech-test-production.up.railway.app`

## Quick Start

After linking your project (step 3 below), set the backend URL:

```bash
npx vercel env add VITE_API_BASE_URL
# When prompted, enter: https://bay-infotech-test-production.up.railway.app
# Select: Production, Preview, and Development (or all three)
```

Then deploy: `npm run deploy:prod`

## One-time setup

### 1. Install dependencies

From the **project root**:

```bash
cd client
npm install
```

### 2. Log in to Vercel

```bash
npx vercel login
```

Follow the prompts to authenticate (email or GitHub/GitLab/Bitbucket).

### 3. Link the project (first deploy only)

From the `client` directory:

```bash
npx vercel
```

- **Set up and deploy?** → `Y`
- **Which scope?** → Your account or team
- **Link to existing project?** → `N` (first time) or `Y` (if you already created it in the dashboard)
- **Project name?** → Accept default or choose one (e.g. `pcte-ai-help-desk-demo`)
- **Directory?** → `./` (current directory)

### 4. Add environment variable

Set the backend API base URL so the frontend can call your API:

```bash
npx vercel env add VITE_API_BASE_URL
```

- **What’s the value?** → `https://bay-infotech-test-production.up.railway.app` (no trailing slash)
- **Add to which environment?** → Choose **Production**, **Preview**, and **Development** as needed (or all three)

Redeploy after adding or changing env vars (see below).

## Deploy

All commands are run from the `client` directory.

### Preview (staging)

```bash
npm run deploy
```

or:

```bash
npx vercel
```

Creates a preview URL (e.g. `https://client-xxx.vercel.app`).

### Production

```bash
npm run deploy:prod
```

or:

```bash
npx vercel --prod
```

Deploys to your production domain (e.g. `https://your-project.vercel.app`).

## After changing env vars

If you add or update `VITE_API_BASE_URL` (or other env vars):

```bash
npx vercel env add VITE_API_BASE_URL   # add/update
npm run deploy:prod                    # redeploy production
```

## Useful CLI commands

| Command | Description |
|--------|-------------|
| `npx vercel` | Deploy preview |
| `npx vercel --prod` | Deploy production |
| `npx vercel env ls` | List env vars |
| `npx vercel env pull` | Pull env vars to `.env.local` |
| `npx vercel logs <url>` | View deployment logs |

## Project config

- **Framework:** Vite (auto-detected)
- **Build:** `npm run build`
- **Output:** `dist/`
- **SPA:** All routes rewrite to `index.html` (see `vercel.json`)

Env vars prefixed with `VITE_` are embedded at build time and used by `src/api/chatApi.js`.
