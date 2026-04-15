# ✅ Deployment Checklist

## Pre-Deployment

- [x] Code is committed to GitHub
- [x] `requirements.txt` is updated
- [x] `groundwater.db` is in repository
- [x] Backend supports environment variables
- [x] Frontend uses `VITE_API_URL`
- [x] CORS is configured
- [x] Health check endpoint exists

## Backend Deployment (Render)

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
- [ ] Add environment variables:
  - [ ] `PYTHON_VERSION=3.11.0`
  - [ ] `DATABASE_PATH=groundwater.db`
  - [ ] `OPENAI_API_KEY=your-key`
  - [ ] `ALLOWED_ORIGINS=*`
- [ ] Deploy and wait for completion
- [ ] Copy backend URL
- [ ] Test `/` endpoint
- [ ] Test `/health` endpoint
- [ ] Test `/docs` endpoint

## Frontend Deployment (Vercel)

- [ ] Create Vercel account
- [ ] Import GitHub repository
- [ ] Set root directory: `frontend`
- [ ] Set framework: Vite
- [ ] Add environment variable:
  - [ ] `VITE_API_URL=https://your-backend.onrender.com`
- [ ] Deploy and wait for completion
- [ ] Copy frontend URL
- [ ] Test page loads
- [ ] Test chat functionality
- [ ] Test filter functionality

## Post-Deployment

- [ ] Update README with live URLs
- [ ] Test all features end-to-end
- [ ] Verify CORS works
- [ ] Check mobile responsiveness
- [ ] Test all 4 themes
- [ ] Verify data accuracy
- [ ] Monitor backend logs
- [ ] Monitor frontend analytics

## Optional Enhancements

- [ ] Add custom domain
- [ ] Set up monitoring alerts
- [ ] Add analytics tracking
- [ ] Create user documentation
- [ ] Set up CI/CD pipeline
- [ ] Add rate limiting dashboard
- [ ] Configure backup strategy

## URLs to Save

**Backend URL**: ___________________________________

**Frontend URL**: ___________________________________

**API Docs**: ___________________________________

**GitHub Repo**: https://github.com/sreekanthteegala/INGRES-ChatBot

---

**Deployment Date**: _______________

**Deployed By**: _______________

**Status**: ⬜ In Progress  ⬜ Completed  ⬜ Issues
