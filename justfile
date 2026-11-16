set shell := ["bash", "-euo", "pipefail", "-c"]

# Lists the commands.
default:
    @just --list

# Prepares locked binary Python packages, JavaScript tools and Rust sources without compilation.
setup:
    python3 -m venv .venv
    .venv/bin/python -m pip install --only-binary=:all: --require-hashes -r requirements.lock
    bun install --frozen-lockfile --ignore-scripts
    cargo fetch --locked

# Validates canonical JSON Schema and OpenAPI semantics with local references.
schema-check:
    .venv/bin/python scripts/validate.py

# Exercises schema rejection and compatibility boundaries on the execution host.
contract-test:
    .venv/bin/python -m unittest discover -s tests -v

# Compiles and round-trips real generated Rust and Dart consumers on the execution host.
codegen-check:
    .venv/bin/python scripts/check-codegen.py

# Checks Rust formatting and the frozen license/source policy without compilation.
signatures-source:
    cargo fmt --all -- --check
    cargo-deny --frozen check licenses sources

# Tests and lints the signature workspace on the execution host.
signatures-check:
    cargo test --workspace --locked --jobs 4
    cargo clippy --workspace --all-targets --locked --jobs 4 -- -D warnings

# Runs every build-free source check without network access.
check: schema-check signatures-source
    just --fmt --check

# Runs the complete contract and native-consumer test gate on the execution host.
test: contract-test codegen-check signatures-check

# Builds the release library and runs the advisory audit on the execution host.
build:
    cargo build --release --workspace --locked --jobs 4
    cargo audit --deny warnings

# Runs the complete source, native test and release verification.
verify: check test build
