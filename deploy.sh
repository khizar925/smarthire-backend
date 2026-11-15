#!/usr/bin/env bash
#
# Manual deploy for the SmartHire backend to AWS Lambda.
# Builds the container image, pushes it to ECR, and updates the Lambda function.
#
# Usage (from the repo root, after changing backend code):
#     ./deploy.sh
#
# Requires: Docker running, AWS CLI logged in to account 476078999724.
#
set -euo pipefail

REGION=eu-north-1
ACCOUNT=476078999724
REPO=smarthire-backend
FUNCTION=smarthire-backend
REGISTRY="$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"
IMAGE="$REGISTRY/$REPO:latest"

echo "==> Building image (linux/amd64)..."
docker build --platform linux/amd64 -t "$REPO" .

echo "==> Logging in to ECR..."
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

echo "==> Tagging and pushing..."
docker tag "$REPO:latest" "$IMAGE"
docker push "$IMAGE"

echo "==> Updating Lambda function..."
aws lambda update-function-code \
  --function-name "$FUNCTION" \
  --image-uri "$IMAGE" \
  --region "$REGION" \
  --no-cli-pager

echo "==> Done. New image deployed to Lambda '$FUNCTION'."
echo "    Test:  curl https://plu098qlu7.execute-api.$REGION.amazonaws.com/health"
