# BuildSight AI — Multimodal Construction Intelligence Platform

A **React + Vite frontend** and **Python FastAPI backend** capstone demo supporting safety-image review, crack-image review, transparent construction cost/valuation estimates, scenario-based weather advisory, and a construction Q&A assistant. API responses use typed Pydantic models and the frontend distinguishes **real Gemini AI** from **demonstration mode**.

> **Safety:** This educational system is not a qualified structural inspection, legal code-compliance assessment, project quotation, or certified real-estate valuation. Do not rely on it for life-safety decisions.

## Setup locally

Requirements: Python 3.9+ (Python 3.10/3.11 recommended), Node.js 20+, Git.

### Backend

```bash
cd backend
python -m venv .venv
# macOS / Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
# Optionally edit .env and add GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

The backend loads `.env` automatically using `python-dotenv`. An API key is optional; absence always displays demo responses (never fabricated detections).

API docs: http://localhost:8000/docs  · Health: http://localhost:8000/api/health

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # Windows: copy .env.example .env
npm run dev
```

Open http://localhost:5173.

## Tests

From the `backend` directory: `pip install pytest` then `pytest -q`.

Frontend build: from `frontend`, run `npm run build`.

## Cloud deployment

Deploy backend as a **Python web service** (Render, Railway or another FastAPI-compatible provider). Root directory `backend`; install command `pip install -r requirements.txt`; start command `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set `GEMINI_API_KEY` (optional), `GEMINI_MODEL` (check provider's available model), and `CORS_ORIGINS=https://your-frontend-host`.

Deploy frontend as a **Vite static app** (Vercel, Netlify, Cloudflare Pages or equivalent). Root directory `frontend`; build command `npm run build`; publish directory `dist`. Set environment variable `VITE_API_URL=https://your-backend-host` **at build time**. Rebuild after modifying it.

Validate the deployed frontend → backend connection: top status should say **Backend online**, and `Cost & Valuation` must return a result.

For a completely functional *AI vision analysis* demo, you need a valid Gemini API key on the backend and a model supporting image inputs. Never put the key into the React frontend or commit it to GitHub. If the AI request fails, the backend returns an explicit error; it does not silently substitute fake image results.

## Features / endpoints

| Capability | Method + endpoint | Notes |
|---|---|---|
| Health | `GET /api/health` | Shows connectivity / key configured status, no key disclosure |
| Site safety | `POST /api/analyze/safety` | `multipart/form-data`: image + optional description |
| Crack analysis | `POST /api/analyze/crack` | Structured observations, severity and limitations |
| Planning and valuation | `POST /api/planning` | JSON user assumptions; illustrative, not sourced market rates |
| Weather guidance | `POST /api/weather` | JSON user-selected scenario, not a live forecast |
| Q&A assistant | `POST /api/assistant` | JSON `{question, context}` |

Image uploads: JPEG/PNG/WebP, max 6 MB, checked against file signature. Gemini analysis returns schema-validated JSON and clearly states uncertainties. No image processing is performed in demo mode.

## Suggested mentor demonstration flow

1. Open dashboard and show health connection.
2. Open Planning & Valuation, enter values, calculate and explain assumptions.
3. Open Weather Advisory and select heavy rain.
4. Show Safety and Crack Analysis with an actual image and explain difference between configured Gemini mode and demo mode.
5. Open API documentation and demonstrate validated response fields.
6. Point to code, tests, and engineering limitations.

## SkillWallet submission

1. Create a **new GitHub repository**, upload the project files excluding `.env`, `.venv` and `node_modules`. Paste its URL in **Add GitHub Link**.
2. Deploy **both backend and frontend**; paste the public **frontend URL** in **Add Demo Link**.
3. Update the SkillWallet Kanban cards only as you genuinely complete and verify each activity.
4. Complete the official project-report document from your workspace and any mentor-required recording.

See `docs/PROJECT_MAPPING.md` and `docs/DEPLOYMENT_CHECKLIST.md`.
