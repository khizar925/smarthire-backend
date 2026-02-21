# supabase_client.py
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Must be service role key

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_job(job_id: str) -> dict | None:
    """Fetch a single job by id. Returns dict or None."""
    response = (
        supabase
        .table("jobs")
        .select("id, job_description")
        .eq("id", job_id)
        .single()
        .execute()
    )
    return response.data


def fetch_applications(job_id: str) -> list[dict]:
    """
    Fetch all applications for a job that have resume_text.
    Uses batching to overcome the default 1000-row limit.
    """
    all_applications = []
    batch_size = 1000
    start = 0

    while True:
        response = (
            supabase
            .table("applications")
            .select("id, full_name, resume_text")
            .eq("job_id", job_id)
            .not_.is_("resume_text", "null")
            .range(start, start + batch_size - 1)
            .execute()
        )
        
        data = response.data or []
        all_applications.extend(data)
        
        if len(data) < batch_size:
            break
            
        start += batch_size

    return all_applications


def save_scores(job_id: str, results: list[dict]) -> None:
    """
    Upsert scores into the scores table.
    Safe to re-run — will overwrite existing scores for the same job+application.
    """
    now = datetime.now(timezone.utc).isoformat()

    rows = [
        {
            "job_id": job_id,
            "application_id": r["application_id"],
            "score": r["score"],
            "scored_at": now,
        }
        for r in results
    ]

    # upsert on (job_id, application_id) unique constraint
    supabase.table("scores").upsert(
        rows,
        on_conflict="job_id,application_id"
    ).execute()


def fetch_scores(job_id: str) -> list[dict]:
    """Fetch all scores for a job (used by /score-status endpoint)."""
    response = (
        supabase
        .table("scores")
        .select("application_id, score, scored_at")
        .eq("job_id", job_id)
        .order("score", desc=True)
        .execute()
    )
    return response.data or []