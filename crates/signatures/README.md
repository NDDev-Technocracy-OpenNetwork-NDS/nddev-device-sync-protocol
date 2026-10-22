# nddev-device-sync-signatures

Canonical request-signature helpers for the nddev-device-sync control-plane
protocol. The crate encodes the signed-envelope rules that the wire schemas
declare, so consumers and the server verify the same bytes.

Consumers pin this crate by immutable Git revision through the lockfile; see
the root README for the release journal.
