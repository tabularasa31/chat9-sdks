from __future__ import annotations

import re
from typing import Any

from .errors import Chat9Error


_EMAIL_SPACE_RE = re.compile(r"\s")
_LOCALE_RE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z]{4})?(-([A-Za-z]{2}|[0-9]{3}))?$")
_TIMEZONE_RE = re.compile(r"^[A-Za-z_]+(?:/[A-Za-z0-9_+\-]+)+$")


def _raise(code: str, message: str) -> None:
    raise Chat9Error(code, message)


def require_secret(secret: Any) -> str:
    if not isinstance(secret, str) or secret == "":
        _raise("MISSING_SECRET", "secret must be a non-empty string")
    return secret


def require_user_id(value: Any, code: str) -> str:
    if not isinstance(value, str) or value == "" or value.strip() == "":
        _raise(code, "user_id must be a non-empty non-whitespace string")
    return value


def require_ttl(ttl: Any) -> int:
    if isinstance(ttl, bool) or not isinstance(ttl, int):
        _raise("INVALID_TTL", "ttl must be an integer between 60 and 3600")
    if ttl < 60 or ttl > 3600:
        _raise("INVALID_TTL", "ttl must be an integer between 60 and 3600")
    return ttl


def validate_email(value: Any, code: str) -> None:
    if not isinstance(value, str):
        _raise(code, "email must be a string")
    if _EMAIL_SPACE_RE.search(value):
        _raise(code, "email must not contain spaces")
    if value.count("@") != 1:
        _raise(code, "email must contain exactly one @")
    local_part, domain = value.split("@", 1)
    if local_part == "":
        _raise(code, "email local part must be non-empty")
    labels = domain.split(".")
    if len(labels) < 2 or any(label == "" for label in labels):
        _raise(code, "email domain must contain non-empty labels")


def validate_locale(value: Any, code: str) -> None:
    if not isinstance(value, str) or _LOCALE_RE.fullmatch(value) is None:
        _raise(code, "locale must match the Phase 1 locale rule")


def validate_timezone(value: Any, code: str) -> None:
    if not isinstance(value, str) or _TIMEZONE_RE.fullmatch(value) is None:
        _raise(code, "timezone must match the Phase 1 timezone rule")


def validate_custom_attrs(value: Any, invalid_code: str, overflow_code: str) -> None:
    if not isinstance(value, dict):
        _raise(invalid_code, "custom_attrs must be an object")
    if len(value) > 20:
        _raise(overflow_code, "custom_attrs exceeds the maximum key count")
    for key, item in value.items():
        if not isinstance(key, str):
            _raise(invalid_code, "custom_attrs keys must be strings")
        if not isinstance(item, str):
            _raise(invalid_code, "custom_attrs values must be strings")
        if len(item) > 256:
            _raise(overflow_code, "custom_attrs values must be 256 chars or fewer")


def validate_optional_fields(payload: dict[str, Any], code: str, overflow_code: str) -> None:
    if "email" in payload:
        validate_email(payload["email"], code)
    if "locale" in payload:
        validate_locale(payload["locale"], code)
    if "timezone" in payload:
        validate_timezone(payload["timezone"], code)
    if "custom_attrs" in payload:
        validate_custom_attrs(payload["custom_attrs"], code, overflow_code)
