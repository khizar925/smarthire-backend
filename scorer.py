# scorer.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Load model once at startup (cached for all requests)
print("Loading NLP model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("NLP model loaded.")


def score_resumes(job_description: str, applications: list[dict]) -> list[dict]:
    """
    Score all resumes against the job description.

    applications: list of dicts with keys:
        - id            (application id)
        - full_name
        - resume_text

    Returns list of dicts:
        - application_id
        - full_name
        - score  (0.00 – 100.00)
    """
    if not applications:
        return []

    # Extract texts
    resume_texts = [app.get("resume_text") or "" for app in applications]

    # Encode job description + all resumes in one batch (fast)
    all_texts = [job_description] + resume_texts
    embeddings = model.encode(all_texts, batch_size=64, show_progress_bar=False)

    job_embedding = embeddings[0]
    resume_embeddings = embeddings[1:]

    # Cosine similarity — vectorised, near instant
    scores = cosine_similarity([job_embedding], resume_embeddings)[0]

    results = []
    for i, app in enumerate(applications):
        results.append({
            "application_id": app["id"],
            "full_name": app.get("full_name", "Unknown"),
            "score": round(float(scores[i]) * 100, 2)
        })

    # Sort highest score first
    results.sort(key=lambda x: x["score"], reverse=True)

    return results