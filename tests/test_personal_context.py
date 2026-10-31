"""Explicit personal context and retained canonical inventory shape."""
import copy
import sys
from pathlib import Path
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate import ROOT, schemas, validator, validate_api


class PersonalContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        documents, cls.registry = schemas()
        cls.schema = documents['https://nddev.ai/schemas/nddev-device-sync/v3/personal.schema.json']

    def valid(self, name, value):
        return validator(self.schema, self.registry, name).is_valid(value)

    def test_closed_context_cannot_embed_credentials_or_organization_authority(self):
        value = {'principal_id': 'principal', 'space': {'kind': 'personal', 'id': 'principal'}}
        self.assertTrue(self.valid('PersonalContext', value))
        for field in ('tenant_id', 'session_token', 'authorization_id', 'role', 'vault_key'):
            with self.subTest(field=field):
                self.assertFalse(self.valid('PersonalContext', value | {field: 'injected'}))
        for kind in ('organization', 'admin', '', None):
            self.assertFalse(self.valid('PersonalContext', value | {'space': value['space'] | {'kind': kind}}))
        for bad in ('', 'x' * 129, 'person/other'):
            self.assertFalse(self.valid('PersonalContext', value | {'principal_id': bad}))

    def test_inventory_reuses_canonical_device_and_page_constraints(self):
        item = {'created_at': '2026-10-28T00:00:00Z', 'device_id': 'device',
                'display_name': 'Synthetic device', 'platform': 'linux',
                'public_key': 'A' * 43, 'status': 'active'}
        value = {'context': {'principal_id': 'principal', 'space': {'kind': 'personal', 'id': 'principal'}},
                 'devices': [item] * 32, 'next_cursor': None}
        self.assertTrue(self.valid('PersonalDeviceList', value))
        self.assertFalse(self.valid('PersonalDeviceList', value | {'devices': [item] * 33}))
        for field in ('context', 'next_cursor'):
            changed = copy.deepcopy(value)
            del changed[field]
            self.assertFalse(self.valid('PersonalDeviceList', changed))
        self.assertFalse(self.valid('PersonalDeviceList', value | {'devices': [item | {'user_id': 'foreign'}]}))

    def test_device_policy_is_closed_bounded_and_carries_no_identity_change(self):
        context = {'principal_id': 'principal', 'space': {'kind': 'personal', 'id': 'principal'}}
        policy = {'mode': 'fullauto', 'purposes': ['desktop', 'dev-desktop'], 'revision': 1}
        value = {'context': context, 'device_id': 'device', 'policy': policy}
        self.assertTrue(self.valid('PersonalDevicePolicy', value))
        for field in ('public_key', 'display_name', 'user_id', 'session_token'):
            self.assertFalse(self.valid('PersonalDevicePolicy', value | {field: 'injected'}))
            self.assertFalse(self.valid('DevicePolicy', policy | {field: 'injected'}))
        for mode in ('auto', 'admin', '', None):
            self.assertFalse(self.valid('DevicePolicy', policy | {'mode': mode}))
        for purposes in ([], ['desktop', 'desktop'], ['admin'], ['desktop'] * 7):
            self.assertFalse(self.valid('DevicePolicy', policy | {'purposes': purposes}))
        for revision in (0, -1, 9007199254740992, '1', 1.5):
            self.assertFalse(self.valid('DevicePolicy', policy | {'revision': revision}))
        update = {'expected_revision': 1, 'mode': 'manual', 'purposes': ['server-hosting']}
        self.assertTrue(self.valid('DevicePolicyUpdate', update))
        self.assertFalse(self.valid('DevicePolicyUpdate', update | {'device_id': 'other'}))
        self.assertFalse(self.valid('DevicePolicyUpdate', {k: v for k, v in update.items() if k != 'expected_revision'}))

    def test_openapi_parameter_refs_cannot_use_noncanonical_array_indices(self):
        path = ROOT / 'openapi/personal-v3.yaml'
        original = yaml.safe_load(path.read_text())
        for index in ('01', '-1', '-', 'named'):
            changed = copy.deepcopy(original)
            changed['paths']['/v3/personal/devices']['get']['parameters'][0]['$ref'] = f'control-plane-v2.yaml#/paths/~1v2~1devices/get/parameters/{index}'
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_api(changed, path)
