set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

setup:
    python3 -m venv .venv
    .venv/bin/python -m pip install --require-hashes -r requirements.lock
    bun install --frozen-lockfile --ignore-scripts

schema-check:
    .venv/bin/python scripts/validate.py

test: codegen-check signatures-check
    .venv/bin/python -m unittest discover -s tests -v

codegen-check:
    .venv/bin/python scripts/check-codegen.py

signatures-check:
    cargo fmt --all -- --check
    cargo test --workspace --locked --jobs 4
    cargo clippy --workspace --all-targets --locked --jobs 4 -- -D warnings
    cargo deny --locked check licenses sources

check: schema-check
    just --fmt --check
    cargo fmt --all -- --check
    cargo deny --locked check licenses sources

# Run the complete schema, generated consumer and native signature gates.
verify: check test
    cargo audit --deny warnings
