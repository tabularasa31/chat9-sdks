# chat9-sdks

Public SDK monorepo for Chat9 customer-facing token generation and verification.

Phase 1 covers:

- Python
- Go
- PHP

The normative contract lives in [`docs/token-spec.md`](docs/token-spec.md).

## Phase 1 Layout

```text
chat9-sdks/
├── README.md
├── LICENSE
├── docs/
├── fixtures/
├── python/
├── go/
├── php/
└── .github/workflows/
```

Later phases may add:

- Node.js
- Java
- Ruby

These are roadmap items only in Phase 1 and are intentionally not scaffolded yet.

## Security

- HMAC provides integrity, not confidentiality
- token payloads are encoded, not encrypted
- do not place secrets or sensitive PII in token fields
- SDKs must never store or log the signing secret

## Phase 1 Status

This repository currently contains:

- normative docs
- shared fixtures
- a reference Python SDK implementation

Go and PHP package implementations are planned as part of the same Phase 1 rollout.
