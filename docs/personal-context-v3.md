# Original personal context, profile v3

`GET /v3/personal/devices` returns the authenticated principal's device inventory
with an explicit personal-space context. The context's `principal_id` and
`space.id` equal the same stable user ID, and `space.kind` is `personal`.
Request fields cannot choose another user, company or storage namespace.

The original authenticated session and retained `(user_id, tenant_id)` storage
binding still own the query. This profile does not rename a key, ciphertext,
device ID, cursor or database record. Personal and organization IDs with the same
text are different namespaces; no organization authority follows from this
observation. Session/store revalidation remains required at the real read boundary.

The canonical schema is `contracts/v3/personal.schema.json`. Device fields and
cursor constraints reference the existing v2 schema. This profile additionally
limits a response to 32 devices, with at most 128 retained identities over bounded
pages. Both required nullable cursor presence and closed objects are preserved.
The provider and consuming client enforce that both context IDs match the
initiating principal; JSON shape validation alone does not prove that relationship.
Credentials, session binding digests and legacy storage ownership stay outside
the context DTO. Public identifiers are not grants or secret-bearing telemetry.

The v2 inventory endpoint and DTO remain unchanged for their existing consumers.
A client adopting explicit personal context requires this new profile; it must
not silently downgrade to a context-free response. HTTP 404 from the fixed new
route becomes a typed compatibility refusal before enrollment or other dependent
work. Other failures and a mismatched context also refuse; pages never mix
profiles. Deploy/adopt the compatible Server before updating such clients.
Existing old source locks keep their original v2 behavior. This transition does
not change authorization expiry or imply a live upgrade.

Browser requests retain the existing exact-origin/header and HttpOnly session
contract. Responses are bounded and `Cache-Control: no-store`. This read profile
adds no mutation, signing protocol, organizational selection or remote operation.
Actual Server/Accounts and retained-data acceptance qualify those boundaries;
DTO generation and source validation do not establish them.

## Device control policy

`GET /v3/personal/devices/{device_id}/policy` returns one owned device's purpose
profiles and authenticated `fullauto`/`manual` control mode (ADR 0018) with the
same personal context. `PUT` replaces it by compare-and-set on `revision`:
`expected_revision` must equal the current value, otherwise the response is
`409 operation_conflict` and the caller reads again. Only the device's own active
owner can replace it; revoked or foreign devices are refused without disclosing
their existence. Widening `manual` into `fullauto` returns
`403 recent_authentication_required` unless the session's sign-in proof is recent;
narrowing and reclassification need only an active session.

New enrollments start as `fullauto`/`desktop`; devices enrolled before this
profile are `manual`/`desktop` at revision 1, so the transition never widens an
existing module checklist. A policy revision never changes the device ID,
display name, public key or enrollment proof. Purposes describe intent and grant
nothing. The mode is stored control state; clients must not accept it as a
per-command flag, and an unreachable server never widens a client's cached mode.
The existing `Device` and inventory DTOs are unchanged for current consumers.
