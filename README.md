# SmartHire Backend — Resume Scorer API

FastAPI service that scores resumes against a job description using sentence-transformer embeddings, with an optional hybrid mode that blends in exact skill and category overlap.

**Live:** deployed on [Render](https://smarthire-backend-icmj.onrender.com) (free tier), auto-deploys from `main`.

## Run locally (venv)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 7860
```

## Run locally (Docker)

From the repo root (`e:\ubuntu-fyp`):

```
docker compose up
```

Serves on `http://localhost:8000`. Health check: `GET /health`.

## Endpoints

- `POST /score` — score all applications for a job (requires `X-API-Key` header)
- `POST /score-single` — score one resume against a job description
- `GET /score-status/{job_id}` — check scoring progress for a job
- `GET /health` — liveness check, no auth

## Tests

```
pytest tests/ -v
```

## CI

GitHub Actions runs lint (`ruff`) → test (`pytest`) → build (`docker build`) on every push/PR to `main`. `main` is branch-protected — all three must pass before a PR can merge.

## Environment variables

See `.env.example`. Required: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `API_KEY`. Optional: `ALLOWED_ORIGINS`, `SCORING_MODE` (`semantic` or `hybrid`), `W_SEMANTIC`, `W_SKILL`, `W_CATEGORY`.
