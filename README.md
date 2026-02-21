---
title: Resume Scorer API
emoji: 📄
colorFrom: blue
colorTo: green
sdk: gradio
app_file: app.py
pinned: false
---

# Resume Scorer API

FastAPI backend for scoring job applications using NLP.

## Deployment on Hugging Face Spaces

This repository is configured for deployment on Hugging Face Spaces using Docker.

### Environment Variables

Ensure the following secrets are set in your Hugging Face Space settings:

- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_KEY`: Your Supabase anon/service key.
- `API_KEY`: The API key used for `X-API-Key` header authentication.

### Local Development

1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `uvicorn main:app --reload`