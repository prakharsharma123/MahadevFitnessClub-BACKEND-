# Mahadev Fitness Club — Render Deployment Guide

## What was fixed
1. **Procfile** — Added proper gunicorn workers/timeout so Render doesn't kill the app in 50s
2. **app.py** — Removed debug=True, added PORT env var support, added /health endpoint
3. **Removed large images** from static/uploads (they don't belong in git)
4. **Removed database.db** from git (Render filesystem is ephemeral anyway)
5. **Credentials** now readable from environment variables (more secure)

---

## Step-by-Step Deployment on Render

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial deploy - gym management app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Create Web Service on Render
- Go to https://render.com → New → Web Service
- Connect your GitHub repo
- Fill in:
  - **Name**: mahadev-gym (or anything)
  - **Runtime**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: (leave blank — uses Procfile automatically)
  - **Instance Type**: Free

### 3. Set Environment Variables on Render
Go to your service → Environment → Add these:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | any long random string e.g. `mahadev_gym_2025_xK9p` |
| `ADMIN_USERNAME` | `Ashish Singh` |
| `ADMIN_PASSWORD` | `Ashish@123` |

> **Optional**: If you want persistent data (won't reset on redeploy), add a free PostgreSQL DB on Render and set `DATABASE_URL` to the connection string it gives you.

### 4. Deploy
Click "Deploy" — it will build and start. Visit your Render URL.

---

## ⚠️ Important: Data Loss Warning
Render's **free tier resets the filesystem on every redeploy**. This means:
- Your SQLite database (`database.db`) is wiped each time you redeploy
- Member photos in `static/uploads/` are also wiped

**Solution**: Add a free Render PostgreSQL database:
1. Render Dashboard → New → PostgreSQL (free tier)
2. Copy the "Internal Database URL"
3. Add it as `DATABASE_URL` environment variable in your web service
4. Your app already supports this — it reads `DATABASE_URL` automatically!

---

## Why app was terminating in 50 seconds
The original Procfile was:
```
web: gunicorn app:app
```
This used default gunicorn settings with a **30-second worker timeout**.
Render's free tier is slow to start, and the worker was getting killed before it could respond.

Fixed Procfile:
```
web: gunicorn app:app --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT
```

---

## Keeping App Alive (Free Tier Sleep)
Render free tier sleeps after 15 minutes of inactivity. To keep it awake, use a free service like:
- https://uptimerobot.com — set a monitor to ping `https://YOUR-APP.onrender.com/health` every 5 minutes
- This is free and prevents the sleep entirely
