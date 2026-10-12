"""Sync de modelo no debe desplegar cambios de flujo/permiso pendientes."""
import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('model_sync', Path(__file__).resolve().parents[1] / 'sync_model_bindings.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class ModelSyncTests(unittest.TestCase):
    def test_only_model_changes_and_body_permissions_preserved(self):
        before = '---\nmodel: old/model\npermission:\n  edit: deny\n---\n\nPrompt viejo\nmodel: body-example\n'
        after = sync.replace_model(before, 'new/model')
        self.assertEqual(before.replace('model: old/model', 'model: new/model'), after)

    def test_routing_preserves_other_roles_and_code(self):
        before = 'const ROUTING: Record<string, string> = {"a": "old", "b": "keep"};\nconst code = 1;'
        after = sync.replace_routes(before, {'a': 'new'})
        self.assertEqual(before.replace('"old"', '"new"'), after)

    def test_ambiguous_frontmatter_rejected(self):
        with self.assertRaises(ValueError):
            sync.replace_model('---\nmodel: old\nmodel: another\n---\n', 'new')

    def test_missing_route_rejected(self):
        with self.assertRaises(ValueError):
            sync.replace_routes('const ROUTING: Record<string, string> = {};', {'missing': 'new'})


if __name__ == '__main__':
    unittest.main()
