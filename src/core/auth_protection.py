from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from time import time
from typing import Any

from src.core.config import Settings


@dataclass(slots=True)
class AuthAttemptDecision:
    allowed: bool
    reason: str | None = None
    retry_after_seconds: int | None = None


class AuthAttemptGuard:
    def __init__(
        self,
        *,
        window_seconds: int,
        ip_max_attempts: int,
        username_max_attempts: int,
        lockout_threshold: int,
        lockout_base_seconds: int,
        lockout_max_seconds: int,
        redis_client: Any | None = None,
    ) -> None:
        self.window_seconds = window_seconds
        self.ip_max_attempts = ip_max_attempts
        self.username_max_attempts = username_max_attempts
        self.lockout_threshold = lockout_threshold
        self.lockout_base_seconds = lockout_base_seconds
        self.lockout_max_seconds = lockout_max_seconds
        self._redis = redis_client

        self._lock = asyncio.Lock()
        self._ip_attempts: dict[str, deque[float]] = {}
        self._username_attempts: dict[str, deque[float]] = {}
        self._username_failures: dict[str, int] = {}
        self._username_lockout_until: dict[str, float] = {}

    @classmethod
    def from_settings(cls, settings: Settings, redis_client: Any | None = None) -> AuthAttemptGuard:
        return cls(
            window_seconds=settings.auth_rate_limit_window_seconds,
            ip_max_attempts=settings.auth_rate_limit_ip_max_attempts,
            username_max_attempts=settings.auth_rate_limit_username_max_attempts,
            lockout_threshold=settings.auth_lockout_threshold,
            lockout_base_seconds=settings.auth_lockout_base_seconds,
            lockout_max_seconds=settings.auth_lockout_max_seconds,
            redis_client=redis_client,
        )

    async def check_attempt(self, client_ip: str, username: str) -> AuthAttemptDecision:
        if self._redis is not None:
            return await self._check_attempt_redis(client_ip=client_ip, username=username)
        now_ts = time()
        async with self._lock:
            self._cleanup(now_ts)

            lockout_until = self._username_lockout_until.get(username, 0.0)
            if lockout_until > now_ts:
                retry = max(1, int(lockout_until - now_ts))
                return AuthAttemptDecision(
                    allowed=False,
                    reason="Too many failed login attempts for this username.",
                    retry_after_seconds=retry,
                )

            ip_events = self._ip_attempts.setdefault(client_ip, deque())
            if len(ip_events) >= self.ip_max_attempts:
                retry = max(1, int(self.window_seconds - (now_ts - ip_events[0])))
                return AuthAttemptDecision(
                    allowed=False,
                    reason="Too many login attempts from this IP address.",
                    retry_after_seconds=retry,
                )

            username_events = self._username_attempts.setdefault(username, deque())
            if len(username_events) >= self.username_max_attempts:
                retry = max(1, int(self.window_seconds - (now_ts - username_events[0])))
                return AuthAttemptDecision(
                    allowed=False,
                    reason="Too many login attempts for this username.",
                    retry_after_seconds=retry,
                )

            ip_events.append(now_ts)
            username_events.append(now_ts)
            return AuthAttemptDecision(allowed=True)

    async def register_failure(self, username: str) -> int | None:
        if self._redis is not None:
            return await self._register_failure_redis(username=username)
        now_ts = time()
        async with self._lock:
            failures = self._username_failures.get(username, 0) + 1
            self._username_failures[username] = failures
            if failures < self.lockout_threshold:
                return None

            exponent = failures - self.lockout_threshold
            lockout_seconds = min(
                self.lockout_max_seconds,
                self.lockout_base_seconds * (2**exponent),
            )
            self._username_lockout_until[username] = now_ts + lockout_seconds
            return int(lockout_seconds)

    async def register_success(self, username: str) -> None:
        if self._redis is not None:
            redis_client = self._redis
            await redis_client.delete(f"auth:fail:{username}", f"auth:lock:{username}")
            return
        async with self._lock:
            self._username_failures.pop(username, None)
            self._username_lockout_until.pop(username, None)

    def _cleanup(self, now_ts: float) -> None:
        cutoff = now_ts - self.window_seconds
        for events in self._ip_attempts.values():
            while events and events[0] < cutoff:
                events.popleft()
        for events in self._username_attempts.values():
            while events and events[0] < cutoff:
                events.popleft()

        for ip in [key for key, events in self._ip_attempts.items() if not events]:
            self._ip_attempts.pop(ip, None)
        for username in [key for key, events in self._username_attempts.items() if not events]:
            self._username_attempts.pop(username, None)
        for username, lockout_until in list(self._username_lockout_until.items()):
            if lockout_until <= now_ts:
                self._username_lockout_until.pop(username, None)

    async def _check_attempt_redis(self, *, client_ip: str, username: str) -> AuthAttemptDecision:
        lock_key = f"auth:lock:{username}"
        lock_ttl = await self._ttl(lock_key)
        if lock_ttl > 0:
            return AuthAttemptDecision(
                allowed=False,
                reason="Too many failed login attempts for this username.",
                retry_after_seconds=lock_ttl,
            )

        ip_key = f"auth:ip:{client_ip}"
        ip_count, ip_ttl = await self._count_and_ttl(ip_key)
        if ip_count >= self.ip_max_attempts:
            return AuthAttemptDecision(
                allowed=False,
                reason="Too many login attempts from this IP address.",
                retry_after_seconds=max(1, ip_ttl),
            )

        user_key = f"auth:user:{username}"
        user_count, user_ttl = await self._count_and_ttl(user_key)
        if user_count >= self.username_max_attempts:
            return AuthAttemptDecision(
                allowed=False,
                reason="Too many login attempts for this username.",
                retry_after_seconds=max(1, user_ttl),
            )

        await self._incr_with_window(ip_key)
        await self._incr_with_window(user_key)
        return AuthAttemptDecision(allowed=True)

    async def _register_failure_redis(self, *, username: str) -> int | None:
        redis_client = self._redis
        assert redis_client is not None
        fail_key = f"auth:fail:{username}"
        failures = int(await redis_client.incr(fail_key))
        if failures == 1:
            await redis_client.expire(fail_key, max(self.lockout_max_seconds * 4, 3600))
        if failures < self.lockout_threshold:
            return None

        exponent = failures - self.lockout_threshold
        lockout_seconds = int(
            min(self.lockout_max_seconds, self.lockout_base_seconds * (2**exponent))
        )
        await redis_client.set(f"auth:lock:{username}", "1", ex=lockout_seconds)
        return lockout_seconds

    async def _incr_with_window(self, key: str) -> int:
        redis_client = self._redis
        assert redis_client is not None
        count = int(await redis_client.incr(key))
        if count == 1:
            await redis_client.expire(key, self.window_seconds)
        return count

    async def _count_and_ttl(self, key: str) -> tuple[int, int]:
        redis_client = self._redis
        assert redis_client is not None
        raw_value = await redis_client.get(key)
        count = int(raw_value) if raw_value is not None else 0
        ttl = await self._ttl(key)
        return count, ttl

    async def _ttl(self, key: str) -> int:
        redis_client = self._redis
        assert redis_client is not None
        ttl = int(await redis_client.ttl(key))
        return max(1, ttl) if ttl > 0 else 0
