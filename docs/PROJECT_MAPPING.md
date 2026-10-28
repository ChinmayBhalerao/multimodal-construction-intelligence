# Mapping to eight SkillWallet instructions

1. **Environment:** React + Vite in `frontend/`, FastAPI in `backend/`, Node/Python installation steps in README.
2. **Backend / AI:** `backend/main.py` uses the Google Gemini REST API when `GEMINI_API_KEY` is set server-side; never stored in the frontend.
3. **Multimodal inputs:** two JPG/PNG/WebP image-upload views accept optional text descriptions; planning accepts structured numerical data.
4. **Safety/crack analysis:** typed findings, hazard / crack descriptors, severity, probable causes, actions, limitations. Vision is real only if Gemini is configured; demo mode explicitly reports *not assessed*.
5. **Planning / valuation:** transparent construction cost, material heuristics, project phase timeline, illustrative land-plus-building valuation, architectural concept **prompt** (not rendered architectural drawing).
6. **React + FastAPI:** fetch-based REST integration, Pydantic-validated output for image analysis; structured JSON other endpoints.
7. **Testing:** backend pytest test suite validates calculation, bad inputs, image type and demo labeling. Additional visual, browser-based, AI-key, and deployed end-to-end tests are still necessary.
8. **Deployment/demo:** README, environment examples and deployment checklist. Deploy both services, test public links, capture screenshots.

## Known gaps / future enhancements

- Full architectural *image rendering* is NOT implemented; conceptual visualization is provided as a prompt only.
- Real-time weather feeds are NOT integrated; weather conditions are user-selected.
- Materials use generic illustrative ratios; not a certified engineering takeoff.
- Valuation is not a professional market appraisal.
- No automated browser E2E test runner included; perform the manual acceptance checks.
- LLM visual accuracy is uncertain; field observations must be professionally verified.
- Use the full Workspace stories to check any additional acceptance criteria before final submission.
