set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

setup:
    python3 -m venv .venv
    .venv/bin/python -m pip install --only-binary=:all: --require-hashes -r requirements.lock
    bun install --frozen-lockfile --ignore-scripts
    cargo fetch --locked

schema-check:
    .venv/bin/python scripts/validate.py

contract-test:
    .venv/bin/python -m unittest discover -s tests -v

codegen-check:
    .venv/bin/python scripts/check-codegen.py

signatures-source:
    cargo fmt --all -- --check
    cargo-deny --frozen check licenses sources

signatures-check:
    cargo test --workspace --locked --jobs 4
    cargo clippy --workspace --all-targets --locked --jobs 4 -- -D warnings

check: schema-check signatures-source

test: contract-test codegen-check signatures-check

build:
    cargo build --release --workspace --locked --jobs 4
    cargo audit --deny warnings

verify: check test build
