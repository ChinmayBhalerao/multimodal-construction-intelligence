# Deployment and submission checklist

- [ ] Verify local frontend builds: `cd frontend && npm run build`.
- [ ] Verify backend API tests: `cd backend && pytest -q`.
- [ ] Create GitHub repository, push source files (do NOT commit `.env` secrets).
- [ ] Deploy backend service and verify `/api/health`.
- [ ] Deploy frontend static build with `VITE_API_URL` set to public backend origin.
- [ ] Set backend `CORS_ORIGINS` to frontend origin and redeploy backend.
- [ ] Test site safety, crack, cost/valuation, weather, and assistant screens.
- [ ] For real AI behavior, set valid Gemini API key on backend and retest with sample images.
- [ ] Capture screenshots of features and document limitations honestly.
- [ ] Add GitHub URL to SkillWallet.
- [ ] Add live **frontend** URL to SkillWallet; do not paste the backend `/docs` URL as the demo.
- [ ] Update milestone board only for tasks actually completed.
- [ ] Prepare mentor demo recording and the workspace's required project report.
