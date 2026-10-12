"""Una eval no puede aprobar por logs, prompts o fallos de ejecución."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("eval_runner", Path(__file__).resolve().parents[2] / "evals/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class EvalEvidenceTests(unittest.TestCase):
    def test_tool_output_is_not_model_verdict(self):
        output = json.dumps({"type": "tool_use", "part": {"text": "verdict: ready"}})
        self.assertEqual("__NO_RESPONSE__", runner.response_text(output))

    def test_only_text_events_are_evaluated(self):
        output = '\n'.join(["provider log verdict: ready", json.dumps({"type": "text", "part": {"text": "verdict: revision-needed"}})])
        self.assertEqual("verdict: revision-needed", runner.response_text(output))

    def test_execution_error_cannot_pass_by_matching_expected_string(self):
        ok, _ = runner.evaluate("__EXECUTION_ERROR__ (1)\nverdict: ready", "verdict: ready", None, None)
        self.assertFalse(ok)

    def test_timeout_partial_text_cannot_pass(self):
        ok, _ = runner.evaluate("__TIMEOUT__ (45s)\nverdict: ready", "verdict: ready", None, None)
        self.assertFalse(ok)

    def test_claimed_write_without_artifact_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            errors = runner.verify_files(Path(directory), {"report.md": {"contains": ["verdict: ready"]}})
            self.assertTrue(errors)
        self.assertFalse(runner.evaluate("__ARTIFACT_ERROR__\nverdict: ready", "verdict: ready", None, None)[0])

    def test_fixture_cannot_escape_sandbox(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                runner.sandbox_path(Path(directory), "../outside.md")

    def test_candidate_stages_new_prompt_preserving_installed_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate, home, sandbox = root / "candidate", root / "home", root / "sandbox"
            (candidate / "agents").mkdir(parents=True)
            (candidate / "skills").mkdir()
            (home / ".config/opencode/agents").mkdir(parents=True)
            generated = "---\ndescription: (IDIOMA: ESPAÑOL) Validador\nmodel: provider/new\npermission:\n  edit: deny\n---\n\nNew durable delivery policy"
            installed = "---\nmodel: provider/installed\npermission:\n  edit: allow\n---\n\nOld policy"
            (candidate / "agents/spec-validator.md").write_text(generated)
            (home / ".config/opencode/agents/spec-validator.md").write_text(installed)
            with patch.object(Path, "home", return_value=home):
                hashes = runner.stage_candidate(candidate, sandbox, "spec-validator")
            staged = (sandbox / ".opencode/agents/spec-validator.md").read_text()
            self.assertIn("New durable delivery policy", staged)
            self.assertIn("provider/installed", staged)
            self.assertIn("edit: deny", staged)
            self.assertEqual(installed, (home / ".config/opencode/agents/spec-validator.md").read_text())
            self.assertIn("agents/spec-validator.md", hashes)
            config = json.loads((sandbox / "opencode.json").read_text())
            self.assertIn("New durable delivery policy", config["agent"]["spec-validator"]["prompt"])
            self.assertEqual([str(sandbox / ".opencode/skills")], config["skills"]["paths"])
            self.assertEqual("(IDIOMA: ESPAÑOL) Validador", config["agent"]["spec-validator"]["description"])


if __name__ == "__main__":
    unittest.main()
