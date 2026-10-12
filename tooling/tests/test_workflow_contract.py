"""Regresiones de protocolo global, permisos efectivos y adapters."""
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "adapters/shared"))
sys.path.insert(0, str(ROOT / "tooling"))
import foundry
import render
import sync_workflow


class WorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.profiles = foundry.load_profiles()

    def test_all_core_sdlc_roles_receive_protocol_once(self):
        agents = foundry.core_agents()
        self.assertEqual(27, len(agents))
        for name, _, body in agents:
            with self.subTest(agent=name):
                self.assertEqual(1, body.count("# Protocolo común SDLC — vigente"))

    def test_opencode_renderer_cannot_drop_common_protocol(self):
        for src in (ROOT / "core/agents/sdlc").glob("**/*.md"):
            if src.stem in self.profiles["perms"]["harness"]["excluded"]:
                continue
            binding = render.resolve_binding(src.stem, self.profiles)
            output = render.render_agent(src, binding)
            with self.subTest(agent=src.stem):
                self.assertEqual(1, output.count("# Protocolo común SDLC — vigente"))

    def test_workers_cannot_delegate_nested_tasks_by_default(self):
        for name in ("executor", "documentation", "test-architect", "spec-validator"):
            with self.subTest(agent=name):
                binding = render.resolve_binding(name, self.profiles)
                self.assertEqual("deny", binding["permission"]["task"])
        tasks = render.resolve_binding("master-orchestrator", self.profiles)["permission"]["task"]
        self.assertEqual("deny", tasks["*"])
        harness = self.profiles["perms"]["harness"]
        self.assertEqual(set(harness["active_subagents"] + harness["optional_subagents"]),
                         {name for name, action in tasks.items() if action == "allow"})

    def test_spec_validators_cannot_edit_certified_artifacts(self):
        for name in ("spec-validator", "enterprise-spec-validator"):
            binding = render.resolve_binding(name, self.profiles)
            self.assertEqual("deny", binding["permission"]["edit"])

    def test_functional_tester_can_write_only_report_scope(self):
        edit = render.resolve_binding("functional-tester-agent", self.profiles)["permission"]["edit"]
        self.assertEqual("deny", edit["*"])
        self.assertEqual({"docs/functional-testing/**", "**/docs/functional-testing/**"}, {path for path, action in edit.items() if action == "allow"})

    def test_remediator_cannot_edit_openapi_or_production(self):
        edit = render.resolve_binding("spec-remediator", self.profiles)["permission"]["edit"]
        self.assertEqual("deny", edit["*"])
        self.assertTrue(all(path.endswith(".md") for path, action in edit.items() if action == "allow"))

    def test_deprecated_routes_have_no_edit_or_shell_permissions(self):
        for name in ("architect-executor", "refactor"):
            profile = self.profiles["perms"]["agents"][name]
            self.assertEqual("deny", profile["edit"])
            self.assertEqual("deny", profile["bash"])

    def test_workflow_sync_preserves_model_and_applies_new_prompt_permissions(self):
        generated = "---\ndescription: (IDIOMA: ESPAÑOL) Nuevo\nmode: subagent\nmodel: openai/new\ntemperature: 0.1\npermission:\n  edit: deny\n---\n\nPrompt nuevo"
        installed = "---\ndescription: (IDIOMA: ESPAÑOL) Viejo\nmode: subagent\nmodel: openai/existing\ntemperature: 0.8\npermission:\n  edit: allow\n---\n\nPrompt viejo"
        result = sync_workflow.compose_agent(generated, installed)
        metadata, body = sync_workflow.split_agent(result)
        self.assertIn("model: openai/existing", metadata)
        self.assertIn("temperature: 0.8", metadata)
        self.assertIn("edit: deny", metadata)
        self.assertIn("Prompt nuevo", body)

    def test_no_pack_activates_deprecated_role(self):
        matrix = yaml.safe_load((ROOT / "core/workflow/matrix.yaml").read_text())
        deprecated = {name for name, entry in matrix["agents"].items() if entry.get("deprecated")}
        for pack in matrix["packs"].values():
            if isinstance(pack["activa"], list):
                self.assertFalse(set(pack["activa"]) & deprecated)


if __name__ == "__main__":
    unittest.main()
