"""Construction Intelligence API. AI observations are preliminary, never engineering certification."""
import base64
import json
import os
from datetime import datetime, timezone
from typing import Literal

from dotenv import load_dotenv
load_dotenv()

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Multimodal Construction Intelligence API", version="1.0.0")
allowed_origins = [v.strip() for v in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if v.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_methods=["GET", "POST"], allow_headers=["*"])
MAX_BYTES = 6 * 1024 * 1024
DISCLAIMER = "Preliminary AI assistance only. Not a structural certification, PPE compliance inspection, or professional engineering advice."

class Finding(BaseModel):
    label: str
    severity: Literal["low", "medium", "high", "critical", "unknown"] = "unknown"
    details: str
    action: str

class Analysis(BaseModel):
    mode: Literal["ai", "demo"]
    kind: Literal["safety", "crack"]
    summary: str
    classification: str
    severity: Literal["low", "medium", "high", "critical", "unknown"]
    probable_causes: list[str]
    findings: list[Finding]
    recommendations: list[str]
    limitations: list[str]
    disclaimer: str = DISCLAIMER

class PlanningInput(BaseModel):
    area_sqft: float = Field(gt=0, le=10000000)
    cost_per_sqft_inr: float = Field(gt=0, le=1000000)
    land_value_inr: float = Field(ge=0, le=100000000000)
    completion_pct: float = Field(ge=0, le=100)
    duration_months: int = Field(ge=1, le=120)
    contingency_pct: float = Field(ge=0, le=50, default=10)
    structure: str = Field(default="Residential", max_length=80)

class AssistantInput(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    context: str = Field(default="", max_length=3000)

class AdvisoryInput(BaseModel):
    weather: Literal["normal", "heavy_rain", "high_wind", "extreme_heat", "cold"]
    activity: str = Field(default="General site work", max_length=150)

@app.get("/api/health")
def health():
    return {"status": "ok", "ai_configured": bool(os.getenv("GEMINI_API_KEY")), "timestamp": datetime.now(timezone.utc).isoformat()}

async def image_bytes(file: UploadFile) -> tuple[bytes, str]:
    supported = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in supported:
        raise HTTPException(415, "Upload a JPG, PNG, or WebP image.")
    content = await file.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES:
        raise HTTPException(413, "Image must be nonempty and at most 6 MB.")
    signatures = {"image/jpeg": content.startswith(b"\xff\xd8\xff"), "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"), "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP"}
    if not signatures[file.content_type]:
        raise HTTPException(415, "File content does not match the image format.")
    return content, file.content_type

def demo_analysis(kind: str) -> Analysis:
    if kind == "crack":
        return Analysis(mode="demo", kind="crack", summary="Demonstration response: the uploaded image has NOT been visually analyzed. Connect Gemini for image-grounded results.", classification="Not assessed", severity="unknown", probable_causes=["Cannot infer causes without image analysis and on-site investigation"], findings=[Finding(label="Visual assessment unavailable", details="Demo mode does not infer crack type, width, orientation, or structural significance.", action="Configure Gemini and obtain an inspection by a qualified professional where needed.")], recommendations=["Document the location, scale, and changes over time.", "Refer concerning cracks to a licensed structural engineer."], limitations=["No visual AI inference in demo mode", "Crack width cannot be reliably measured from an uncalibrated photo"])
    return Analysis(mode="demo", kind="safety", summary="Demonstration response: the uploaded image has NOT been visually analyzed. Connect Gemini for image-grounded results.", classification="Not assessed", severity="unknown", probable_causes=[], findings=[Finding(label="Safety inspection unavailable", details="Demo mode cannot confirm helmets, harnesses, vests, or site hazards.", action="Use a qualified site safety inspection and configure a vision-capable model.")], recommendations=["Review PPE, fall protection, electrical hazards, and access routes on site."], limitations=["No visual AI inference in demo mode", "Photo framing may omit hazards"])

async def gemini_json(system: str, parts: list[dict]):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.15}}
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, params={"key": key}, json=body)
        response.raise_for_status()
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(502, f"AI service unavailable or invalid response: {type(exc).__name__}. Check API key/model and retry.")

@app.post("/api/analyze/{kind}", response_model=Analysis)
async def analyze(kind: Literal["safety", "crack"], image: UploadFile = File(...), description: str = Form(default="")):
    if len(description) > 3000:
        raise HTTPException(422, "Description must contain at most 3000 characters")
    content, mime = await image_bytes(image)
    if not os.getenv("GEMINI_API_KEY"):
        return demo_analysis(kind)
    prompt = ("Analyze construction-site visual safety and visible PPE, fall, electrical and access hazards." if kind == "safety" else "Analyze visible surface cracking, orientation, possible classifications and uncertainty. Never infer exact width without a scale reference.")
    system = ("You assist construction professionals with NON-CERTIFYING preliminary image observations. Never invent unseen details. " + prompt + " Return a single JSON object with exactly these keys: summary(string), classification(string), severity(one of low, medium, high, critical, unknown), probable_causes(array of strings), findings(array of objects each with label, severity, details, action), recommendations(array of strings), limitations(array of strings). If insufficient evidence say unknown. Do not claim code compliance, engineer approval, or conclusive structural diagnosis. Return JSON only.")
    data = await gemini_json(system, [{"text": f"Context from user: {description or 'None'}"}, {"inline_data": {"mime_type": mime, "data": base64.b64encode(content).decode("ascii")}}])
    try:
        return Analysis.model_validate({**data, "mode": "ai", "kind": kind, "disclaimer": DISCLAIMER})
    except Exception:
        raise HTTPException(502, "The AI returned a response that did not match the required JSON schema. Please retry.")

@app.post("/api/planning")
def planning(payload: PlanningInput):
    base = round(payload.area_sqft * payload.cost_per_sqft_inr, 2)
    contingency = round(base * payload.contingency_pct / 100, 2)
    total = round(base + contingency, 2)
    spent = round(total * payload.completion_pct / 100, 2)
    rough_valuation = round(payload.land_value_inr + base, 2)
    # Generic illustrative factors; NOT engineered bill of quantities.
    material = {"cement_bags_approx": round(payload.area_sqft * 0.4), "steel_kg_approx": round(payload.area_sqft * 4), "sand_cuft_approx": round(payload.area_sqft * 1.2)}
    phases = [("Site preparation & foundation", .20), ("Structural frame", .35), ("Masonry and services", .25), ("Finishes & handover", .20)]
    months = payload.duration_months
    return {"currency": "INR", "base_cost_inr": base, "contingency_inr": contingency, "estimated_total_inr": total, "estimated_spent_inr": spent, "estimated_remaining_inr": round(total-spent, 2), "illustrative_property_value_inr": rough_valuation, "material_estimates": material, "schedule": [{"phase": name, "approx_months": round(months*portion, 1)} for name,portion in phases], "visualization_prompt": f"Architectural concept illustration of a {payload.structure.lower()} construction project, realistic materials, clean site plan, isometric exterior, daylight", "assumptions": ["Costs use user-supplied area and rate; no market prices are fetched.", "Material coefficients are illustrative, not a bill of quantities.", "Property valuation is a basic land-plus-building-cost illustration, not a certified appraisal.", "Actual phase duration, material requirements, and costs require local professional validation."]}

@app.post("/api/weather")
def weather(payload: AdvisoryInput):
    advice = {"normal": ["Conduct daily toolbox talk and equipment checks.", "Verify access routes and PPE."], "heavy_rain": ["Inspect waterlogging, excavations, and temporary electrical installations.", "Suspend unsafe lifting and work at height; have site supervisor reassess conditions."], "high_wind": ["Review crane and lifting wind limits from manufacturer and site procedures.", "Secure unsecured materials and reassess scaffolding and elevated work."], "extreme_heat": ["Provide water, shade, rest breaks, and heat-illness monitoring.", "Review concrete curing procedures with site engineering staff."], "cold": ["Check slippery surfaces and worker cold-stress protection.", "Review temperature-dependent concrete placement and curing requirements."]}
    return {"weather": payload.weather, "activity": payload.activity, "recommendations": advice[payload.weather], "source": "User-selected weather scenario; no live forecast", "disclaimer": DISCLAIMER}

@app.post("/api/assistant")
async def assistant(payload: AssistantInput):
    if not os.getenv("GEMINI_API_KEY"):
        return {"mode": "demo", "answer": "The AI assistant is in demonstration mode. Configure GEMINI_API_KEY on the backend to receive question-specific answers. For now, verify site practices with applicable local standards and qualified professionals.", "disclaimer": DISCLAIMER}
    system = "You are a construction information assistant. Give concise, helpful guidance, explain uncertainty, and never claim that you have inspected a site. For engineering decisions, advise professional assessment. Reply as JSON with one key: answer (string)."
    d = await gemini_json(system, [{"text": f"Context: {payload.context}\nQuestion: {payload.question}"}])
    if not isinstance(d, dict) or not isinstance(d.get("answer"), str):
        raise HTTPException(502, "AI response schema invalid")
    return {"mode": "ai", "answer": d["answer"], "disclaimer": DISCLAIMER}
