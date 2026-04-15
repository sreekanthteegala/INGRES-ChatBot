# 🚀 Deployment Guide - INGRES Groundwater Chatbot

This guide will help you deploy the full-stack groundwater chatbot to production.

## 📋 Prerequisites

- GitHub account (repository already connected)
- Render account (for backend) - https://render.com
- Vercel account (for frontend) - https://vercel.com
- OpenAI API key

---

## 🔧 Part 1: Deploy Backend (Render)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `sreekanthteegala/INGRES-ChatBot`
3. Configure the service:

**Basic Settings:**
- **Name**: `ingres-groundwater-api`
- **Region**: Oregon (US West) or closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: Python 3

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`

### Step 3: Add Environment Variables
Click **"Environment"** tab and add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `DATABASE_PATH` | `groundwater.db` |
| `OPENAI_API_KEY` | `your-openai-api-key-here` |
| `ALLOWED_ORIGINS` | `*` |

⚠️ **Important**: Replace `your-openai-api-key-here` with your actual OpenAI API key

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Once deployed, you'll get a URL like: `https://ingres-groundwater-api.onrender.com`

### Step 5: Test Backend
Open your backend URL in browser:
```
https://ingres-groundwater-api.onrender.com
```

You should see:
```json
{
  "message": "INGRES Groundwater Chatbot API Running",
  "version": "2.0.0",
  "status": "healthy"
}
```

Test health endpoint:
```
https://ingres-groundwater-api.onrender.com/health
```

---

## 🎨 Part 2: Deploy Frontend (Vercel)

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### Step 2: Import Project
1. Click **"Add New..."** → **"Project"**
2. Import `sreekanthteegala/INGRES-ChatBot`
3. Configure the project:

**Framework Preset:** Vite
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `dist`

### Step 3: Add Environment Variable
In **"Environment Variables"** section, add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://ingres-groundwater-api.onrender.com` |

⚠️ **Important**: Replace with your actual Render backend URL from Part 1

### Step 4: Deploy
1. Click **"Deploy"**
2. Wait for deployment (2-3 minutes)
3. Once deployed, you'll get a URL like: `https://ingres-chatbot.vercel.app`

### Step 5: Test Frontend
1. Open your Vercel URL
2. Try asking: "Which state has the highest groundwater availability?"
3. Try using filters to query data

---

## 🔗 Part 3: Update CORS (if needed)

If you get CORS errors, update the backend environment variable:

1. Go to Render dashboard
2. Select your web service
3. Go to **"Environment"** tab
4. Update `ALLOWED_ORIGINS` to your Vercel URL:
   ```
   https://ingres-chatbot.vercel.app
   ```
5. Save and redeploy

---

## ✅ Part 4: Verify Deployment

### Backend Checks:
- [ ] `/` endpoint returns API info
- [ ] `/health` endpoint shows database connection
- [ ] `/docs` shows API documentation
- [ ] `/chat` endpoint accepts POST requests
- [ ] `/filter_query` endpoint works

### Frontend Checks:
- [ ] Page loads without errors
- [ ] Theme switcher works
- [ ] Filter panel opens/closes
- [ ] Chat queries return responses
- [ ] Filter queries show data tables
- [ ] Charts render correctly

---

## 🎯 Part 5: Update README

Add this section to your README.md:

```markdown
## 🌐 Live Demo

**Frontend**: https://ingres-chatbot.vercel.app
**Backend API**: https://ingres-groundwater-api.onrender.com
**API Docs**: https://ingres-groundwater-api.onrender.com/docs

Try asking:
- "Which state has the highest groundwater availability?"
- "Show rainfall in Punjab for 2023-24"
- "Top 5 states by groundwater recharge"
```

---

## 🐛 Troubleshooting

### Backend Issues:

**Problem**: Build fails
- **Solution**: Check `requirements.txt` has all dependencies
- **Solution**: Verify Python version is 3.11.0

**Problem**: Database not found
- **Solution**: Ensure `groundwater.db` is committed to GitHub
- **Solution**: Check `.gitignore` doesn't exclude `groundwater.db`

**Problem**: OpenAI API errors
- **Solution**: Verify `OPENAI_API_KEY` is set correctly
- **Solution**: Check API key has credits

### Frontend Issues:

**Problem**: Cannot connect to backend
- **Solution**: Verify `VITE_API_URL` is set correctly
- **Solution**: Check backend is running (visit backend URL)

**Problem**: CORS errors
- **Solution**: Update `ALLOWED_ORIGINS` in backend environment variables
- **Solution**: Add your Vercel URL to allowed origins

**Problem**: Build fails
- **Solution**: Check `package.json` has all dependencies
- **Solution**: Verify Node version compatibility

---

## 📊 Monitoring

### Render (Backend):
- View logs: Dashboard → Your Service → Logs
- Monitor metrics: Dashboard → Your Service → Metrics
- Check health: Visit `/health` endpoint

### Vercel (Frontend):
- View deployments: Dashboard → Your Project → Deployments
- Check analytics: Dashboard → Your Project → Analytics
- View logs: Click on deployment → View Function Logs

---

## 💰 Cost Considerations

### Free Tier Limits:

**Render Free Plan:**
- 750 hours/month
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds

**Vercel Free Plan:**
- 100 GB bandwidth/month
- Unlimited deployments
- No spin-down

**OpenAI API:**
- Pay per token
- GPT-4o-mini: ~$0.15 per 1M input tokens
- Monitor usage at https://platform.openai.com/usage

---

## 🔄 Updating Deployment

### Backend Updates:
1. Push changes to GitHub `main` branch
2. Render auto-deploys (if enabled)
3. Or manually trigger: Dashboard → Deploy → Manual Deploy

### Frontend Updates:
1. Push changes to GitHub `main` branch
2. Vercel auto-deploys
3. Or manually trigger: Dashboard → Deployments → Redeploy

---

## 🎉 Success!

Your groundwater chatbot is now live and accessible worldwide!

**Share your deployment:**
- Frontend URL: `https://your-app.vercel.app`
- API Docs: `https://your-api.onrender.com/docs`

**Next Steps:**
- Add custom domain (optional)
- Set up monitoring/alerts
- Gather user feedback
- Iterate and improve

---

## 📞 Support

If you encounter issues:
1. Check logs in Render/Vercel dashboards
2. Verify environment variables are set
3. Test endpoints individually
4. Check GitHub repository is up to date

**Happy Deploying! 🚀**
