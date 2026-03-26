# Chat9 Compatibility

## Scope

This document explains how the public `chat9-sdks` Phase 1 token contract relates to the private Chat9 product backend.

The SDK contract is intentionally smaller and stricter than product behavior. Phase 1 optimizes for deterministic cross-language parity, not for maximum field flexibility.

## Compatibility Fields

Product-level fields may exist outside the core SDK-required contract. Example:

- `tenant_id`

Rules:

- compatibility fields are allowed in SDK payloads
- compatibility fields are preserved during canonical serialization
- compatibility fields are preserved on successful verification
- compatibility fields are not required by the SDK core contract

Product systems may still enforce additional business rules on top of successful token verification.

## Current Product Relationship

The current private Chat9 backend already uses a signed HMAC-based token flow for optional widget identity. That product flow is related, but it is not the normative source for public SDK behavior.

The public SDK contract differs from the existing product flow in several important ways:

- Base64 is standard and padded
- error codes are explicit and typed
- validation rules are tighter and fully documented
- canonicalization rules are normative across languages
- fixture-based determinism is a release gate

If product behavior evolves, SDK token-format compatibility must still be preserved unless a breaking version is explicitly released.

## Secret Rotation

Phase 1 SDK APIs stay single-secret for simplicity.

Secret rotation remains an integration and backend concern. Integrators should:

- provision a new secret out of band
- roll out token generation with the new secret
- keep verification overlap on the receiving system during rotation
- retire the old secret after overlap ends

Public SDKs should not persist or manage secret rotation state.

## Security Notes

HMAC provides integrity, not confidentiality.

Important consequences:

- token payloads are encoded, not encrypted
- anyone holding the token can inspect payload contents
- do not place secrets in token fields
- do not place sensitive PII in token fields unless product policy explicitly permits it
- SDKs must never store the signing secret
- SDKs must never log the signing secret

## Backend Validation Boundary

Successful SDK verification means:

- token structure is valid
- signature is valid
- token is not expired
- core field shapes satisfy the Phase 1 spec

Successful SDK verification does not guarantee:

- tenant authorization
- product entitlement checks
- user existence
- business-rule eligibility

Those remain backend responsibilities.
