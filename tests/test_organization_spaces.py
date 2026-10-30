"""Independent organization context reuses the closed company payload owner."""
import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate import ROOT, schemas, validator


class OrganizationSpaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        documents, cls.registry = schemas()
        cls.schema = documents["https://nddev.ai/schemas/nddev-device-sync/v3/organizations.schema.json"]

    def valid(self, name, value):
        return validator(self.schema, self.registry, name).is_valid(value)

    def overview(self):
        return {"company": {"company_id": "company", "display_name": "Synthetic", "revision": 1},
                "member": {"user_id": "principal", "email": None, "role": "user", "active": True, "revision": 1}}

    def test_namespace_is_explicit_even_when_organization_and_principal_ids_collide(self):
        context = {"principal_id": "principal", "space": {"kind": "organization", "id": "principal"}, "membership_revision": 1}
        self.assertTrue(self.valid("OrganizationContext", context))
        for kind in ("personal", "admin", "", None):
            self.assertFalse(self.valid("OrganizationContext", context | {"space": context["space"] | {"kind": kind}}))
        for field in ("owner", "tenant_id", "role", "session_token", "vault_key"):
            self.assertFalse(self.valid("OrganizationContext", context | {field: "injected"}))
        for field in context:
            self.assertFalse(self.valid("OrganizationContext", {k:v for k,v in context.items() if k != field}))

    def test_bounded_membership_list_keeps_the_original_personal_context(self):
        value = {"context": {"principal_id": "principal", "space": {"kind": "personal", "id": "principal"}},
                 "organizations": [self.overview()] * 32}
        self.assertTrue(self.valid("OrganizationList", value))
        self.assertFalse(self.valid("OrganizationList", value | {"organizations": [self.overview()] * 33}))
        changed = copy.deepcopy(value)
        changed["context"]["space"]["kind"] = "organization"
        self.assertFalse(self.valid("OrganizationList", changed))
        self.assertFalse(self.valid("OrganizationList", value | {"owner": "rebound"}))
        changed = copy.deepcopy(value)
        changed["organizations"][0]["member"]["session_token"] = "secret"
        self.assertFalse(self.valid("OrganizationList", changed))

    def test_scoped_pages_and_results_require_context_and_the_canonical_payload(self):
        context = {"principal_id": "principal", "space": {"kind": "organization", "id": "company"}, "membership_revision": 1}
        values = {
            "OrganizationOverview": {"context": context, "overview": self.overview()},
            "OrganizationMemberPage": {"context": context, "page": {"members": [], "next_cursor": None}},
            "OrganizationInvitationPage": {"context": context, "page": {"invitations": [], "next_cursor": None}},
            "OrganizationMemberResult": {"context": context, "member": self.overview()["member"]},
        }
        for name, value in values.items():
            self.assertTrue(self.valid(name, value), name)
            del value["context"]
            self.assertFalse(self.valid(name, value), name)

    def test_creation_is_an_immutable_command_without_claimed_role_or_owner(self):
        value = {"operation_id": "01900000-0000-7000-8000-000000000001", "display_name": "Synthetic"}
        self.assertTrue(self.valid("OrganizationCreateRequest", value))
        for field in ("company_id", "user_id", "tenant_id", "role"):
            self.assertFalse(self.valid("OrganizationCreateRequest", value | {field: "chosen"}))
        for invalid in ("", "x" * 129):
            self.assertFalse(self.valid("OrganizationCreateRequest", value | {"display_name": invalid}))

    def test_mutations_require_the_original_membership_revision_and_closed_payload(self):
        value = {"membership_revision": 4, "payload": {"operation_id": "01900000-0000-7000-8000-000000000001"}}
        self.assertTrue(self.valid("OrganizationRevokeRequest", value))
        for revision in (None, 0, -1, 1.5, True, 9007199254740992):
            self.assertFalse(self.valid("OrganizationRevokeRequest", value | {"membership_revision": revision}))
        self.assertFalse(self.valid("OrganizationRevokeRequest", {"payload": value["payload"]}))
        self.assertFalse(self.valid("OrganizationRevokeRequest", value | {"payload": value["payload"] | {"role": "admin"}}))

    def test_every_new_route_requires_a_signed_original_session(self):
        api = yaml.safe_load((ROOT / "openapi/organizations-v3.yaml").read_text())
        self.assertEqual(api["security"], [{"ownerSession": [], "deviceSignature": []}, {"browserSession": [], "deviceSignature": []}])
        for path, item in api["paths"].items():
            for method, operation in item.items():
                if method not in {"get", "post"}:
                    continue
                self.assertNotIn("security", operation)
                parameters = {value["$ref"].rsplit("/", 1)[-1] for value in operation["parameters"]}
                self.assertTrue({"SignatureInput", "Signature", "ContentDigest", "BrowserClient"} <= parameters, (path, method))
