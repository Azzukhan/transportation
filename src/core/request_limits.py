from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from time import time
from typing import Any

from src.core.config import Settings


@dataclass(slots=True)
class RateLimitDecision:
    allowed: bool
    scope: str | None = None
    retry_after_seconds: int | None = None


class RequestRateLimiter:
    def __init__(
        self,
        *,
        window_seconds: int,
        global_max_requests: int,
        auth_max_requests: int,
        upload_max_requests: int,
        export_max_requests: int,
        redis_client: Any | None = None,
    ) -> None:
        self.window_seconds = window_seconds
        self.global_max_requests = global_max_requests
        self.auth_max_requests = auth_max_requests
        self.upload_max_requests = upload_max_requests
        self.export_max_requests = export_max_requests
        self._redis = redis_client
        self._events: dict[str, deque[float]] = {}
        self._lock = asyncio.Lock()

    @classmethod
    def from_settings(
        cls, settings: Settings, redis_client: Any | None = None
    ) -> RequestRateLimiter:
        return cls(
            window_seconds=settings.rate_limit_window_seconds,
            global_max_requests=settings.rate_limit_global_max_requests,
            auth_max_requests=settings.rate_limit_auth_max_requests,
            upload_max_requests=settings.rate_limit_upload_max_requests,
            export_max_requests=settings.rate_limit_export_max_requests,
            redis_client=redis_client,
        )

    async def check(self, *, client_id: str, path: str, method: str) -> RateLimitDecision:
        if self._redis is not None:
            return await self._check_redis(client_id=client_id, path=path, method=method)
        scopes = self._scopes_for_path(path=path, method=method)
        now_ts = time()
        async with self._lock:
            self._cleanup(now_ts)
            for scope, max_requests in scopes:
                if max_requests <= 0:
                    continue
                bucket_key = f"{scope}:{client_id}"
                bucket = self._events.setdefault(bucket_key, deque())
                if len(bucket) >= max_requests:
                    retry = max(1, int(self.window_seconds - (now_ts - bucket[0])))
                    return RateLimitDecision(
                        allowed=False,
                        scope=scope,
                        retry_after_seconds=retry,
                    )

            for scope, max_requests in scopes:
                if max_requests <= 0:
                    continue
                bucket_key = f"{scope}:{client_id}"
                self._events.setdefault(bucket_key, deque()).append(now_ts)
            return RateLimitDecision(allowed=True)

    def _scopes_for_path(self, *, path: str, method: str) -> list[tuple[str, int]]:
        scopes: list[tuple[str, int]] = [("global", self.global_max_requests)]
        upper_method = method.upper()

        if path.endswith("/auth/token") or path.endswith("/auth/token/refresh"):
            scopes.append(("auth", self.auth_max_requests))

        if upper_method in {"POST", "PUT", "PATCH"} and (
            path.endswith("/employee-salaries/import") or "/invoices/signatories" in path
        ):
            scopes.append(("upload", self.upload_max_requests))

        if upper_method == "GET" and (
            path.endswith("/employee-salaries/export")
            or path.endswith("/driver-report/export")
            or path.endswith("/pdf")
        ):
            scopes.append(("export", self.export_max_requests))
        return scopes

    def _cleanup(self, now_ts: float) -> None:
        cutoff = now_ts - self.window_seconds
        for events in self._events.values():
            while events and events[0] < cutoff:
                events.popleft()
        for key in [bucket_key for bucket_key, events in self._events.items() if not events]:
            self._events.pop(key, None)

    async def _check_redis(self, *, client_id: str, path: str, method: str) -> RateLimitDecision:
        scopes = self._scopes_for_path(path=path, method=method)
        for scope, max_requests in scopes:
            if max_requests <= 0:
                continue
            key = f"rl:{scope}:{client_id}"
            count = await self._get_count(key)
            if count >= max_requests:
                ttl = await self._get_ttl(key)
                return RateLimitDecision(
                    allowed=False,
                    scope=scope,
                    retry_after_seconds=max(1, ttl or self.window_seconds),
                )

        for scope, max_requests in scopes:
            if max_requests <= 0:
                continue
            await self._incr_window_key(f"rl:{scope}:{client_id}")
        return RateLimitDecision(allowed=True)

    async def _incr_window_key(self, key: str) -> int:
        redis_client = self._redis
        assert redis_client is not None
        value = int(await redis_client.incr(key))
        if value == 1:
            await redis_client.expire(key, self.window_seconds)
        return value

    async def _get_count(self, key: str) -> int:
        redis_client = self._redis
        assert redis_client is not None
        raw = await redis_client.get(key)
        return int(raw) if raw is not None else 0

    async def _get_ttl(self, key: str) -> int:
        redis_client = self._redis
        assert redis_client is not None
        ttl = int(await redis_client.ttl(key))
        return ttl if ttl > 0 else 0
