# Frontend Deployment - Vercel

## Quick Setup

1. **Connect Repository to Vercel**
   - Go to https://vercel.com
   - Add New → Project
   - Import your GitHub repository

2. **Configure Project**
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Add Environment Variable**
   - Go to Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-railway-backend.railway.app`

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically

## Environment Variables

- `VITE_API_URL`: Your Railway backend URL

## Custom Domain

After deployment, you can add a custom domain in Vercel settings.

