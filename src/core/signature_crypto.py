from __future__ import annotations

import json
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.core.config import Settings, get_settings

_ENVELOPE_PREFIX = b"sigenc:v1:"
_DEK_NONCE_LEN = 12
_DATA_NONCE_LEN = 12
_KEY_LENGTH = 32


@dataclass(slots=True)
class DecryptedSignature:
    data: bytes
    key_id: str | None
    encrypted: bool


def _b64_encode(raw: bytes) -> str:
    return urlsafe_b64encode(raw).decode("ascii")


def _b64_decode(value: str) -> bytes:
    return urlsafe_b64decode(value.encode("ascii"))


def _normalize_key(value: str) -> bytes:
    raw = _b64_decode(value)
    if len(raw) != _KEY_LENGTH:
        raise ValueError("Signature encryption key must be exactly 32 bytes after base64 decoding.")
    return raw


class KeyEncryptionProvider(Protocol):
    def has_key(self, key_id: str) -> bool: ...

    def wrap_key(self, *, key_id: str, dek: bytes) -> tuple[bytes, bytes]: ...

    def unwrap_key(self, *, key_id: str, dek_nonce: bytes, wrapped_dek: bytes) -> bytes: ...


class EnvKeyEncryptionProvider:
    def __init__(self, keys: dict[str, bytes]) -> None:
        self.keys = keys

    def has_key(self, key_id: str) -> bool:
        return key_id in self.keys

    def wrap_key(self, *, key_id: str, dek: bytes) -> tuple[bytes, bytes]:
        kek = self.keys[key_id]
        dek_nonce = os.urandom(_DEK_NONCE_LEN)
        wrapped_dek = AESGCM(kek).encrypt(dek_nonce, dek, None)
        return dek_nonce, wrapped_dek

    def unwrap_key(self, *, key_id: str, dek_nonce: bytes, wrapped_dek: bytes) -> bytes:
        kek = self.keys[key_id]
        return AESGCM(kek).decrypt(dek_nonce, wrapped_dek, None)


class SignatureCrypto:
    def __init__(
        self,
        *,
        enabled: bool,
        active_key_id: str,
        key_provider: KeyEncryptionProvider,
    ) -> None:
        self.enabled = enabled
        self.active_key_id = active_key_id
        self.key_provider = key_provider

    @classmethod
    def from_settings(cls, settings: Settings) -> SignatureCrypto:
        keys = {
            key_id: _normalize_key(value)
            for key_id, value in settings.signature_encryption_keys_map.items()
        }
        return cls(
            enabled=settings.signature_encryption_enabled,
            active_key_id=settings.signature_active_key_id,
            key_provider=EnvKeyEncryptionProvider(keys),
        )

    def is_encrypted_payload(self, payload: bytes) -> bool:
        return payload.startswith(_ENVELOPE_PREFIX)

    def decrypt_payload(self, payload: bytes | None) -> DecryptedSignature | None:
        if payload is None:
            return None
        if not payload:
            return DecryptedSignature(data=b"", key_id=None, encrypted=False)
        if not self.enabled:
            return DecryptedSignature(data=payload, key_id=None, encrypted=False)
        if not self.is_encrypted_payload(payload):
            # Backward compatibility with legacy plaintext rows.
            return DecryptedSignature(data=payload, key_id=None, encrypted=False)

        envelope = json.loads(payload[len(_ENVELOPE_PREFIX) :].decode("utf-8"))
        if envelope.get("v") != 1:
            raise ValueError("Unsupported signature encryption envelope version.")
        key_id = envelope.get("kid")
        if not isinstance(key_id, str) or not self.key_provider.has_key(key_id):
            raise ValueError("Signature encryption key ID is invalid or unavailable.")
        wrapped_dek = _b64_decode(envelope["dek_ct"])
        dek_nonce = _b64_decode(envelope["dek_nonce"])
        encrypted_data = _b64_decode(envelope["data_ct"])
        data_nonce = _b64_decode(envelope["data_nonce"])

        dek = self.key_provider.unwrap_key(
            key_id=key_id, dek_nonce=dek_nonce, wrapped_dek=wrapped_dek
        )
        plaintext = AESGCM(dek).decrypt(data_nonce, encrypted_data, None)
        return DecryptedSignature(data=plaintext, key_id=key_id, encrypted=True)

    def encrypt_for_storage(self, payload: bytes | None) -> bytes | None:
        if payload is None:
            return None
        if not self.enabled:
            return payload

        already_decrypted = self.decrypt_payload(payload)
        if already_decrypted is None:
            return None
        if already_decrypted.encrypted and already_decrypted.key_id == self.active_key_id:
            return payload

        if not self.key_provider.has_key(self.active_key_id):
            raise ValueError("Active signature encryption key is not configured.")

        dek = os.urandom(_KEY_LENGTH)
        dek_nonce, wrapped_dek = self.key_provider.wrap_key(key_id=self.active_key_id, dek=dek)
        data_nonce = os.urandom(_DATA_NONCE_LEN)
        encrypted_data = AESGCM(dek).encrypt(data_nonce, already_decrypted.data, None)

        envelope: dict[str, Any] = {
            "v": 1,
            "kid": self.active_key_id,
            "dek_nonce": _b64_encode(dek_nonce),
            "dek_ct": _b64_encode(wrapped_dek),
            "data_nonce": _b64_encode(data_nonce),
            "data_ct": _b64_encode(encrypted_data),
        }
        return _ENVELOPE_PREFIX + json.dumps(envelope, separators=(",", ":")).encode("utf-8")

    def needs_rotation(self, payload: bytes | None) -> bool:
        if payload is None or not self.enabled:
            return False
        decrypted = self.decrypt_payload(payload)
        if decrypted is None:
            return False
        if not decrypted.encrypted:
            return True
        return decrypted.key_id != self.active_key_id


@lru_cache
def get_signature_crypto() -> SignatureCrypto:
    return SignatureCrypto.from_settings(get_settings())
