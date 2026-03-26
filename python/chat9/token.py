from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from .errors import SupportBotError
from .validation import require_secret, require_ttl, require_user_id, validate_optional_fields


class _DuplicateKeyError(ValueError):
    pass


def _current_utc_seconds() -> int:
    return int(time.time())


def _raise(code: str, message: str) -> None:
    raise SupportBotError(code, message)


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _canonical_b64(raw_bytes: bytes) -> str:
    return base64.b64encode(raw_bytes).decode("ascii")


def _parse_json_object(raw_text: str) -> dict[str, Any]:
    def _hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise _DuplicateKeyError(key)
            out[key] = value
        return out

    try:
        value = json.loads(raw_text, object_pairs_hook=_hook)
    except (_DuplicateKeyError, json.JSONDecodeError) as exc:
        raise SupportBotError("INVALID_TOKEN_FORMAT", "payload must be valid JSON") from exc

    if not isinstance(value, dict):
        _raise("INVALID_TOKEN_FORMAT", "payload must be a JSON object")
    return value


def _decode_payload_segment(segment: str) -> dict[str, Any]:
    try:
        raw_bytes = base64.b64decode(segment, validate=True)
    except Exception as exc:  # pragma: no cover
        raise SupportBotError("INVALID_TOKEN_FORMAT", "payload segment must be canonical Base64") from exc

    if _canonical_b64(raw_bytes) != segment:
        _raise("INVALID_TOKEN_FORMAT", "payload segment must be canonical Base64")

    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SupportBotError("INVALID_TOKEN_FORMAT", "payload must be UTF-8") from exc

    return _parse_json_object(raw_text)


def _validate_verified_payload(payload: dict[str, Any]) -> None:
    if "exp" not in payload:
        _raise("INVALID_TOKEN_FORMAT", "payload must contain exp")
    exp = payload["exp"]
    if isinstance(exp, bool) or not isinstance(exp, int):
        _raise("INVALID_TOKEN_FORMAT", "exp must be an integer JSON number")

    if "user_id" not in payload:
        _raise("INVALID_TOKEN_FORMAT", "payload must contain user_id")
    require_user_id(payload["user_id"], "INVALID_TOKEN_FORMAT")
    validate_optional_fields(payload, "INVALID_TOKEN_FORMAT", "INVALID_TOKEN_FORMAT")


def generateToken(params: dict[str, Any]) -> str:
    if not isinstance(params, dict):
        _raise("INVALID_FIELD", "params must be an object")

    secret = require_secret(params.get("secret"))

    user = params.get("user")
    if not isinstance(user, dict):
        _raise("MISSING_USER_ID", "user must be an object containing user_id")

    options = params.get("options")
    if options is None:
        options = {}
    if not isinstance(options, dict):
        _raise("INVALID_FIELD", "options must be an object")

    ttl = require_ttl(options.get("ttl", 300))
    algorithm = options.get("algorithm")
    if algorithm is not None and algorithm != "sha256":
        _raise("INVALID_FIELD", 'algorithm must be exactly "sha256"')

    require_user_id(user.get("user_id"), "MISSING_USER_ID")
    validate_optional_fields(user, "INVALID_FIELD", "CUSTOM_ATTRS_OVERFLOW")

    payload = dict(user)
    payload["exp"] = _current_utc_seconds() + ttl
    payload_json = _canonical_json(payload)
    payload_b64 = _canonical_b64(payload_json.encode("utf-8"))
    signature = hmac.new(
        secret.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{signature}"


def verifyToken(token: str, secret: str) -> dict[str, Any]:
    require_secret(secret)

    if not isinstance(token, str):
        _raise("INVALID_TOKEN_FORMAT", "token must be a string")
    parts = token.split(".")
    if len(parts) != 2 or any(part == "" for part in parts):
        _raise("INVALID_TOKEN_FORMAT", "token must contain exactly two non-empty segments")

    payload_segment, provided_signature = parts
    payload = _decode_payload_segment(payload_segment)
    _validate_verified_payload(payload)

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected_signature, provided_signature):
        _raise("INVALID_SIGNATURE", "token signature is invalid")

    if _current_utc_seconds() >= payload["exp"]:
        _raise("EXPIRED_TOKEN", "token has expired")

    return payload
