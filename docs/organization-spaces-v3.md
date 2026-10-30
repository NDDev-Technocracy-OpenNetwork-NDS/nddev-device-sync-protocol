# Independent organization membership

The `/v3/organizations` profile uses the existing verified principal, original
personal context and enrolled-device signature. Listing current memberships
does not select a company or grant access. A principal retains at most 32
membership rows, including removed memberships; rejoining reuses its row.
Creating an organization makes its verified creator an administrator and does
not register another account.

A selected organization has an immutable ID and captured membership revision.
Reads include that revision in the signed URI. Commands include it with their
original UUIDv7 and payload in the signed body. Every scoped response carries
the original principal, organization kind/ID and initiating revision. Consumers
check these before publishing a result and retire the old selected lifetime
before disclosing results in a replacement. Current membership is checked in the
same transaction as reads, mutations and receipt replay. Removal, role change
or rejoin cannot lend a later grant to an earlier command.

Company names, member/invitation payloads, revision limits, last-admin protection
and command deadlines retain their canonical v2 definitions. Invitation creation,
SMTP outcome and verified-email acceptance remain distinct. A pending invitation
may reserve an identity, but normal sign-in is refused until verified acceptance.
An existing principal joining another company keeps its original personal owner.

The server's explicit schema transition retains personal IDs, device proofs,
key envelopes, ciphertext/AAD, pending work, challenges and command receipts.
Old unobserved session revocation remains terminal. Historical conflicting
invitation reservations refuse rather than guess a different recipient.
Organization roles move to one membership authority. Legacy `/v2/company` reads
project only current original-company membership; mutations without the captured
revision refuse. No fallback relabels a request into another organization.

Removing a membership closes its administrative access, preserving personal
sessions, keys, device identity and other memberships. Legacy RDS control keeps
its original-company boundary and personal own-device access; this profile does
not grant new organization-wide RDS or shared Vault authority. Organization key
distribution and new module-state namespaces remain their owning later cohorts.
