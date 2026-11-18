# nddev-device-sync-protocol working contract

Keep schemas generic, versioned and free of private estate data. Every event must define
redaction expectations, idempotency behavior and compatibility rules. Generated clients
belong in consuming repositories; this repository owns the source schemas.

Keep the smallest versioned schema that preserves idempotency, redaction, compatibility
and explicit failure outcomes. Do not add fields without an owner and migration rule.

`just setup` prepares locked binary Python packages, JavaScript dependencies and
Rust sources without compilation. `just check` validates canonical schemas and
OpenAPI semantics, Rust formatting and the frozen dependency policy without
tests or consumer builds. Run `just test`, `just build` and `just verify` only
on execution hosts or runners. Preserve every existing rejection, signature and
real Rust/Dart round-trip gate while the validator implementation is migrated.
