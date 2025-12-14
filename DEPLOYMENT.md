# Deployment Guide

This guide will help you deploy Email Clean Agent to Railway (backend) and Vercel (frontend).

## Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Vercel account (sign up at https://vercel.com)
- Google Cloud Console access (for OAuth)
- OpenAI API key

## Step 1: Prepare Your Repository

1. Push your code to GitHub:
```bash
git push origin main
```

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will detect the `backend/` directory

### 2.2 Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

```
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=https://your-railway-url.railway.app/auth/google/callback
OPENAI_API_KEY=sk-your-openai-key
SECRET_KEY=generate-a-random-secret-key-here
ENCRYPTION_KEY=your-44-character-base64-key
DATABASE_URL=postgresql://user:pass@host:port/dbname (Railway provides this automatically)
BACKEND_URL=https://your-railway-url.railway.app
FRONTEND_URL=https://your-vercel-url.vercel.app
ENVIRONMENT=production
```

**Important Notes:**
- Railway will provide `DATABASE_URL` automatically if you add a PostgreSQL service
- `GOOGLE_REDIRECT_URI` must match your Railway backend URL
- Generate `SECRET_KEY` using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Use the same `ENCRYPTION_KEY` from your local `.env` file

### 2.3 Configure Build Settings

Railway should auto-detect:
- **Root Directory:** `backend`
- **Build Command:** (auto-detected from Dockerfile)
- **Start Command:** (auto-detected from Procfile)

### 2.4 Add PostgreSQL (Optional but Recommended)

1. In Railway dashboard, click "+ New" → "Database" → "PostgreSQL"
2. Railway will automatically set `DATABASE_URL` environment variable
3. The app will use PostgreSQL instead of SQLite

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Project

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

### 3.2 Configure Environment Variables

In Vercel dashboard → Settings → Environment Variables, add:

```
VITE_API_URL=https://your-railway-backend-url.railway.app
```

### 3.3 Deploy

Click "Deploy" - Vercel will build and deploy your frontend.

## Step 4: Update Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" → "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add to "Authorized redirect URIs":
   - `https://your-railway-url.railway.app/auth/google/callback`
5. Save changes

## Step 5: Test Deployment

1. Visit your Vercel frontend URL
2. Try logging in with Google
3. Test processing a few emails
4. Check Railway logs for any errors

## Troubleshooting

### Backend Issues

- **CORS errors:** Make sure `FRONTEND_URL` in Railway matches your Vercel URL
- **Database errors:** Check that `DATABASE_URL` is set correctly
- **OAuth errors:** Verify redirect URI matches exactly in Google Console

### Frontend Issues

- **API connection errors:** Check `VITE_API_URL` is set to your Railway backend URL
- **Build errors:** Check Vercel build logs for specific errors

## Environment Variables Reference

### Backend (Railway)

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | `GOCSPX-...` |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL | `https://your-app.railway.app/auth/google/callback` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `SECRET_KEY` | App secret key | Random string (32+ chars) |
| `ENCRYPTION_KEY` | Token encryption key | 44-char base64 string |
| `DATABASE_URL` | Database connection | Auto-provided by Railway |
| `BACKEND_URL` | Backend URL | `https://your-app.railway.app` |
| `FRONTEND_URL` | Frontend URL | `https://your-app.vercel.app` |
| `ENVIRONMENT` | Environment | `production` |

### Frontend (Vercel)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://your-app.railway.app` |

## Post-Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] All environment variables set
- [ ] Google OAuth redirect URI updated
- [ ] Database connected (if using PostgreSQL)
- [ ] Test login flow
- [ ] Test email processing
- [ ] Check logs for errors
- [ ] Verify CORS is working
- [ ] Test on mobile device

## Support

If you encounter issues:
1. Check Railway logs: Railway dashboard → Deployments → View logs
2. Check Vercel logs: Vercel dashboard → Deployments → View logs
3. Verify all environment variables are set correctly
4. Ensure Google OAuth redirect URI matches exactly

