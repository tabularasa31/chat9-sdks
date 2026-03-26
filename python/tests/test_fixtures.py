from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from chat9 import Chat9Error, generateToken, verifyToken
import chat9.token as token_module


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT_DIR / "fixtures"


def _load_json(name: str) -> Any:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _load_json("generate_cases.json"))
def test_generate_token_matches_fixtures(monkeypatch: pytest.MonkeyPatch, case: dict[str, Any]) -> None:
    monkeypatch.setattr(token_module, "_current_utc_seconds", lambda: case["now"])
    params = {
      "secret": case["secret"],
      "user": case["user"],
      "options": case.get("options") or {},
    }

    expected_error = case.get("expected_error")
    if expected_error:
        with pytest.raises(Chat9Error) as exc_info:
            generateToken(params)
        assert exc_info.value.code == expected_error
        return

    token = generateToken(params)
    assert token == case["expected_token"]
    assert verifyToken(token, case["secret"]) == case["expected_payload"]


@pytest.mark.parametrize("case", _load_json("verify_cases.json"))
def test_verify_token_matches_fixtures(monkeypatch: pytest.MonkeyPatch, case: dict[str, Any]) -> None:
    monkeypatch.setattr(token_module, "_current_utc_seconds", lambda: case["now"])

    expected_error = case.get("expected_error")
    if expected_error:
        with pytest.raises(Chat9Error) as exc_info:
            verifyToken(case["token"], case["secret"])
        assert exc_info.value.code == expected_error
        return

    assert verifyToken(case["token"], case["secret"]) == case["expected_payload"]


_GOLDEN = _load_json("golden_tokens.json")


@pytest.mark.parametrize("case", _GOLDEN.values(), ids=_GOLDEN.keys())
def test_golden_tokens(monkeypatch: pytest.MonkeyPatch, case: dict[str, Any]) -> None:
    """Cross-language canonical tokens — every SDK must produce and accept these exact bytes."""
    monkeypatch.setattr(token_module, "_current_utc_seconds", lambda: case["now"])

    expected_error = case.get("expected_error")
    if expected_error:
        with pytest.raises(Chat9Error) as exc_info:
            verifyToken(case["token"], case["secret"])
        assert exc_info.value.code == expected_error
        return

    assert verifyToken(case["token"], case["secret"]) == case["expected_payload"]
