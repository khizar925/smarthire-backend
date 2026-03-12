# main.py
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from scorer import score_resumes
from supabase_client import fetch_job, fetch_applications, save_scores

load_dotenv()

app = FastAPI(title="Resume Scorer API", version="1.0.0")

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ── Auth ──────────────────────────────────────────────────────────────────────

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


# ── Schema ────────────────────────────────────────────────────────────────────

class ScoreRequest(BaseModel):
    job_id: str


class SingleScoreRequest(BaseModel):
    resume_text: str
    job_description: str


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.post("/score")
def score(request: ScoreRequest, key: str = Security(verify_api_key)):
    job_id = request.job_id

    # 1. Fetch job description
    job = fetch_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    job_description = job["job_description"]

    # 2. Fetch all applications with resume_text for this job
    applications = fetch_applications(job_id)
    if not applications:
        raise HTTPException(status_code=404, detail="No applications found for this job")

    # 3. Score all resumes
    results = score_resumes(job_description, applications)

    # 4. Save scores to DB
    save_scores(job_id, results)

    return {
        "status": "success",
        "message": f"Successfully scored {len(results)} applications for job '{job_id}'.",
        "scored_count": len(results)
    }


@app.post("/score-single")
def score_single(request: SingleScoreRequest, key: str = Security(verify_api_key)):
    """Score a single resume against a job description. Returns a score 0-100."""
    results = score_resumes(request.job_description, [
        {"id": "single", "full_name": "", "resume_text": request.resume_text}
    ])
    return {"score": results[0]["score"] if results else 0.0}


@app.get("/score-status/{job_id}")
def score_status(job_id: str, key: str = Security(verify_api_key)):
    """Check how many resumes have been scored for a given job."""
    from supabase_client import fetch_scores
    scores = fetch_scores(job_id)
    return {
        "job_id": job_id,
        "scored_count": len(scores),
        "scores": scores
    }


@app.get("/health")
def health():
    return {"status": "ok"}