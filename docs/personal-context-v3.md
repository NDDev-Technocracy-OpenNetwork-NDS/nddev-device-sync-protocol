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
