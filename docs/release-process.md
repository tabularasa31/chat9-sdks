# Chat9 Release Process

## Purpose

This document defines the Phase 1 release process for the public `chat9-sdks` repository.

Phase 1 covers Python, Go, and PHP only.

## Release Principles

- `docs/token-spec.md` is the contract
- fixtures are the compatibility proof
- golden vectors are committed and versioned
- implementations must not change token bytes silently
- standard-library-only remains a hard requirement in Phase 1

## Release Order

Release work must follow this order:

1. update normative docs
2. update fixtures if the contract intentionally changes
3. update SDK implementations
4. run all language-local tests
5. run shared fixture conformance checks
6. verify golden-vector stability
7. publish packages

Do not publish a package if docs, fixtures, and implementation are out of sync.

## Breaking-Change Policy

Treat all of the following as breaking changes:

- any change to token bytes for the same frozen input
- any change to accepted or rejected fixture behavior
- any change to error-code behavior
- any change to canonicalization rules
- any change to required or generated payload fields

Breaking changes require:

- explicit review
- fixture updates
- golden-vector updates
- semver-major release

## Golden Vector Workflow

Golden vectors are generated from the normative contract and committed to the repository.

Workflow:

1. update spec and conformance docs
2. regenerate vectors from the approved fixture set
3. review drift explicitly
4. merge only if drift is intended

If vectors drift unexpectedly, stop the release and treat it as a compatibility regression.

## Package Publication

For every Phase 1 language package:

- publish only from a commit that passed CI
- tag versions consistently across docs and package metadata
- include README examples aligned with the normative spec
- include compatibility and security notes in package documentation

## Future Phases

Later language additions must not loosen or redefine the Phase 1 contract.

When Phase 2 and Phase 3 begin:

- new SDKs must consume the same fixtures
- new SDKs must verify existing golden vectors
- prior Phase 1 token bytes must remain unchanged unless a major version is intentionally introduced
