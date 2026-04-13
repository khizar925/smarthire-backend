# scorer.py
import os

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from text_cleaner import clean
from preprocessor import extract_skill_set

# Load model once at startup (cached for all requests)
print("Loading NLP model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("NLP model loaded.")


# ── Private helpers ───────────────────────────────────────────────────────────

def _jaccard(a: set, b: set) -> float:
    """
    Symmetric overlap score between two sets.
    Returns 0.0 when both sets are empty (avoids division by zero).
    Uses intersection / union so keyword-stuffed resumes are penalised.
    """
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── Public API ────────────────────────────────────────────────────────────────

def score_resumes(job_description: str, applications: list[dict]) -> list[dict]:
    """
    Score all resumes against the job description.

    applications: list of dicts with keys:
        - id            (application id)
        - full_name
        - resume_text

    Returns list of dicts (sorted by score descending):
        - application_id
        - full_name
        - score          (0.00 – 100.00, final weighted score)
        - breakdown      (dict with sub-scores; only present in hybrid mode)

    Scoring mode is controlled by the SCORING_MODE env var:
        "semantic"  — cosine similarity only (default, current behaviour)
        "hybrid"    — weighted combination of semantic + exact skill + category overlap
    """
    if not applications:
        return []

    # ── Read config per call so env changes take effect without restart ───────
    scoring_mode = os.getenv("SCORING_MODE", "semantic").lower()
    w_semantic   = float(os.getenv("W_SEMANTIC",  "0.60"))
    w_skill      = float(os.getenv("W_SKILL",     "0.25"))
    w_category   = float(os.getenv("W_CATEGORY",  "0.15"))

    if scoring_mode == "hybrid":
        assert abs(w_semantic + w_skill + w_category - 1.0) < 0.01, (
            f"Hybrid scoring weights must sum to 1.0 "
            f"(got {w_semantic + w_skill + w_category:.3f}). "
            "Check W_SEMANTIC, W_SKILL, W_CATEGORY env vars."
        )

    # ── Step 1: clean texts ───────────────────────────────────────────────────
    cleaned_jd = clean(job_description)
    cleaned_resumes = [clean(app.get("resume_text") or "") for app in applications]

    # ── Step 2 (hybrid only): extract JD skill signals once ──────────────────
    if scoring_mode == "hybrid":
        jd_skills, jd_categories = extract_skill_set(cleaned_jd)
        if not jd_skills:
            print("WARNING: No known skills extracted from job description. "
                  "Category/skill scores will be 0 for all candidates.")

    # ── Step 3: batch-encode cleaned texts ───────────────────────────────────
    all_texts = [cleaned_jd] + cleaned_resumes
    embeddings = model.encode(all_texts, batch_size=64, show_progress_bar=False)

    job_embedding    = embeddings[0]
    resume_embeddings = embeddings[1:]

    # ── Step 4: vectorised cosine similarity ─────────────────────────────────
    cosine_scores = cosine_similarity([job_embedding], resume_embeddings)[0]

    # ── Step 5: build result per application ─────────────────────────────────
    results: list[dict] = []

    for i, app in enumerate(applications):
        semantic_score = round(float(cosine_scores[i]) * 100, 2)

        if scoring_mode == "hybrid":
            res_skills, res_categories = extract_skill_set(cleaned_resumes[i])

            skill_score    = round(_jaccard(jd_skills,     res_skills)     * 100, 2)
            category_score = round(_jaccard(jd_categories, res_categories) * 100, 2)
            final_score    = round(
                w_semantic * semantic_score
                + w_skill  * skill_score
                + w_category * category_score,
                2,
            )
            result = {
                "application_id": app["id"],
                "full_name": app.get("full_name", "Unknown"),
                "score": final_score,
                "breakdown": {
                    "semantic":  semantic_score,
                    "skill":     skill_score,
                    "category":  category_score,
                    "mode":      "hybrid",
                    "weights": {
                        "semantic":  w_semantic,
                        "skill":     w_skill,
                        "category":  w_category,
                    },
                },
            }
        else:
            result = {
                "application_id": app["id"],
                "full_name": app.get("full_name", "Unknown"),
                "score": semantic_score,
            }

        results.append(result)

    # Sort highest score first
    results.sort(key=lambda x: x["score"], reverse=True)

    return results
