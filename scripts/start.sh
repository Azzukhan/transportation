#!/usr/bin/env bash
set -euo pipefail

APP_MODULE=${APP_MODULE:-src.main:app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}
USE_GUNICORN=${USE_GUNICORN:-true}
WEB_CONCURRENCY=${WEB_CONCURRENCY:-2}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
GUNICORN_GRACEFUL_TIMEOUT=${GUNICORN_GRACEFUL_TIMEOUT:-30}
GUNICORN_KEEPALIVE=${GUNICORN_KEEPALIVE:-5}

if [[ "${USE_GUNICORN}" == "true" ]]; then
  exec gunicorn "${APP_MODULE}" \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WEB_CONCURRENCY}" \
    --bind "${HOST}:${PORT}" \
    --timeout "${GUNICORN_TIMEOUT}" \
    --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT}" \
    --keep-alive "${GUNICORN_KEEPALIVE}" \
    --access-logfile - \
    --error-logfile - \
    --log-level "${LOG_LEVEL}"
fi

exec uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}" --log-level "${LOG_LEVEL}"
