#!/usr/bin/env bash
set -euo pipefail

# Example deployment script. Copy and customize for your environment.
IMAGE_NAME=${IMAGE_NAME:-your-registry/transportation-api}
IMAGE_TAG=${IMAGE_TAG:-latest}
CONTAINER_NAME=${CONTAINER_NAME:-transportation-api}
ENV_FILE=${ENV_FILE:-.env}
PORT=${PORT:-8000}
PULL_FIRST=${PULL_FIRST:-false}

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing env file: ${ENV_FILE}"
  exit 1
fi

if [[ "${PULL_FIRST}" == "true" ]]; then
  docker pull "${IMAGE_NAME}:${IMAGE_TAG}"
else
  docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
fi

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  --env-file "${ENV_FILE}" \
  -p "${PORT}:8000" \
  "${IMAGE_NAME}:${IMAGE_TAG}"

echo "Deployed ${IMAGE_NAME}:${IMAGE_TAG} as ${CONTAINER_NAME}"
