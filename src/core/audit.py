from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import Request

from src.core.config import Settings
from src.core.exceptions import AppException


class AuditLogger:
    def __init__(self, *, hash_key: str) -> None:
        self._hash_key = hash_key.encode("utf-8")
        self._prev_hash = "0" * 64
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger("transportation.audit")

    @classmethod
    def from_settings(cls, settings: Settings) -> AuditLogger:
        return cls(hash_key=settings.audit_hash_key)

    async def emit(
        self,
        *,
        actor: str,
        tenant_id: int | None,
        resource: str,
        action: str,
        request_id: str,
        outcome: str = "success",
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        timestamp = datetime.now(UTC).isoformat()
        base_event: dict[str, Any] = {
            "actor": actor,
            "tenant_id": tenant_id,
            "resource": resource,
            "resource_id": resource_id,
            "action": action,
            "outcome": outcome,
            "request_id": request_id,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }
        canonical = json.dumps(base_event, sort_keys=True, separators=(",", ":")).encode("utf-8")
        async with self._lock:
            event_hash = hashlib.sha256(
                self._hash_key + self._prev_hash.encode("ascii") + canonical
            ).hexdigest()
            record = {
                **base_event,
                "prev_hash": self._prev_hash,
                "event_hash": event_hash,
            }
            self._prev_hash = event_hash
        self._logger.info(json.dumps(record, sort_keys=True, separators=(",", ":")))


def _request_id_from_request(request: Request) -> str:
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))


async def audit_event(
    request: Request,
    *,
    actor: str,
    tenant_id: int | None,
    resource: str,
    action: str,
    outcome: str = "success",
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    audit_logger = getattr(request.app.state, "audit_logger", None)
    if not isinstance(audit_logger, AuditLogger):
        return
    await audit_logger.emit(
        actor=actor,
        tenant_id=tenant_id,
        resource=resource,
        action=action,
        outcome=outcome,
        resource_id=resource_id,
        metadata=metadata,
        request_id=_request_id_from_request(request),
    )


def enforce_sensitive_export_step_up(request: Request, settings: Settings) -> None:
    if not settings.sensitive_export_step_up_required:
        return
    provided = request.headers.get("X-Step-Up-Token", "").strip()
    expected = settings.sensitive_export_step_up_token.strip()
    if not provided or provided != expected:
        raise AppException(
            "Step-up authentication required for sensitive export/download",
            status_code=403,
            code="step_up_required",
        )
