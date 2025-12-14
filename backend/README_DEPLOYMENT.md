# Backend Deployment - Railway

## Quick Setup

1. **Connect Repository to Railway**
   - Go to https://railway.app
   - New Project → Deploy from GitHub
   - Select your repository

2. **Set Root Directory**
   - In Railway dashboard → Settings → Service
   - Set "Root Directory" to `backend`

3. **Add Environment Variables**
   - Go to Variables tab
   - Add all variables from `.env.example`
   - Update URLs to your production URLs

4. **Add PostgreSQL (Optional)**
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway auto-sets `DATABASE_URL`

5. **Deploy**
   - Railway will auto-deploy on push
   - Or click "Deploy" manually

## Environment Variables Required

See `DEPLOYMENT.md` in root directory for full list.

## Health Check

After deployment, test: `https://your-app.railway.app/health`

