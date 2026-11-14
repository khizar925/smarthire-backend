FROM public.ecr.aws/lambda/python:3.11

# Cache the NLP model inside the image and load it offline at runtime.
# Lambda's filesystem is read-only except /tmp, so the model must already be
# baked in and loaded without any network/cache writes.
ENV HF_HOME=/opt/hf-cache \
    SENTENCE_TRANSFORMERS_HOME=/opt/hf-cache \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLP model into the image (avoids first-request download)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy app code into the Lambda task root
COPY . ${LAMBDA_TASK_ROOT}

# Lambda calls this: module "main", function "handler" (the Mangum adapter)
CMD ["main.handler"]
