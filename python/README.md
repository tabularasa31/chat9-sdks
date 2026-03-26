# Chat9 Python SDK

Phase 1 Python implementation of the Chat9 token contract.

## Public API

- `generateToken(params: dict) -> str`
- `verifyToken(token: str, secret: str) -> dict`

## Example

```python
from chat9 import generateToken, verifyToken

token = generateToken(
    {
        "secret": "secret_minimal_123",
        "user": {"user_id": "user-123"},
        "options": {"ttl": 300},
    }
)

payload = verifyToken(token, "secret_minimal_123")
```

See [`../docs/token-spec.md`](../docs/token-spec.md) for the normative contract.
