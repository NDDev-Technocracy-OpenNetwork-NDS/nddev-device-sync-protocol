# Signatures crate working contract

Keep signing and verification byte-exact against the protocol schemas; any
canonicalization change is a protocol change and travels through the wire
version, never a silent edit. No network, storage or credential code belongs
here. Run the workspace `just check` before review.
