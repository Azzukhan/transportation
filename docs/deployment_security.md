# Deployment Security Hardening

This project enforces strict startup checks in production (`APP_ENV=production`).

## Required Production Settings

Set all of these before deploy:

- `SECRET_KEY`: strong random secret (>=32 chars).
- `JWT_PREVIOUS_SECRET_KEYS`: optional comma-separated previous JWT keys for key rotation verification.
- `AUDIT_HASH_KEY`: strong random secret (>=32 chars), used for tamper-evident audit hash chaining.
- `DATABASE_URL`: non-sqlite database URL.
- `AUTH_COOKIE_SECURE=true`
- `RATE_LIMIT_BACKEND=redis`
- `REDIS_URL`: Redis connection string for shared auth/rate-limit protections.
- `CORS_ALLOWED_ORIGINS`: HTTPS origins only (no localhost/127.0.0.1).
- `SIGNATURE_ENCRYPTION_ENABLED=true`
- `SIGNATURE_ENCRYPTION_KEYS`: `key_id:base64_32_byte_key` list.
- `SIGNATURE_ACTIVE_KEY_ID`: active key id from `SIGNATURE_ENCRYPTION_KEYS`.
- Auth tokens are set only in cookies; do not depend on token values in JSON response bodies.

Optional but recommended for sensitive exports:

- `SENSITIVE_EXPORT_STEP_UP_REQUIRED=true`
- `SENSITIVE_EXPORT_STEP_UP_TOKEN=<strong-random-secret>`

## Key Rotation

### JWT signing key

1. Set new key as `SECRET_KEY`.
2. Move previous `SECRET_KEY` into `JWT_PREVIOUS_SECRET_KEYS`.
3. Deploy.
4. Wait until old access tokens expire.
5. Remove old key from `JWT_PREVIOUS_SECRET_KEYS`.

### Signature blob encryption key

1. Add new key id+value to `SIGNATURE_ENCRYPTION_KEYS`.
2. Set `SIGNATURE_ACTIVE_KEY_ID` to new key id.
3. Deploy.
4. Rotate existing encrypted rows:
   - `uv run python -m src.tools.rotate_signature_encryption`
5. After full rotation, remove old key from `SIGNATURE_ENCRYPTION_KEYS`.

### Audit hash key

Rotate `AUDIT_HASH_KEY` only during planned maintenance. Hash chains before/after rotation will be separate trust segments.

## CI Security Gate

Security regression checks run in GitHub Actions workflow:

- `.github/workflows/security-gate.yml`

The workflow runs security-focused tests and fails the build if controls regress.
It also runs Ruff lint checks before the security suite.
