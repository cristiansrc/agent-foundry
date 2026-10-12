"""Regresiones de gates históricos/comentados y estado/carril ambiguos."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "validate_states", Path(__file__).resolve().parents[1] / "validate-states.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StateGateTests(unittest.TestCase):
    def validate(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample-sdd-context.md"
            path.write_text(text, encoding="utf-8")
            return MODULE.validate_file(path)

    def context(self, state="awaiting-human-plan-approval", verdict="ready"):
        return (
            f"## Current status\nstate: {state}\n"
            "## Spec Validator Approval\n"
            f"verdict: {verdict}\ninvalidated_by_changes_since: none\n"
        )

    def test_current_exact_ready_accepts(self):
        self.assertEqual([], self.validate(self.context()))

    def test_historical_ready_does_not_authorize(self):
        text = self.context(verdict="revision-needed") + "## History\nverdict: ready\n"
        self.assertTrue(self.validate(text))

    def test_ready_with_minor_changes_does_not_authorize(self):
        self.assertTrue(self.validate(self.context(verdict="ready with minor changes")))

    def test_invalidated_ready_does_not_authorize(self):
        text = self.context().replace("invalidated_by_changes_since: none", "invalidated_by_changes_since: runtime delta")
        self.assertTrue(self.validate(text))

    def test_commented_human_signature_does_not_authorize(self):
        text = self.context(state="in_progress") + "<!--\n## Human Plan Approval: approved_by_user\n-->"
        self.assertTrue(self.validate(text))

    def test_human_signature_and_current_ready_authorize_execution(self):
        text = self.context(state="in_progress") + "## Human Plan Approval: approved_by_user\n"
        self.assertEqual([], self.validate(text))

    def test_duplicate_lane_cannot_use_trivial_to_skip_gate(self):
        text = self.context(state="in_progress", verdict="revision-needed") + "## Lane: trivial\n## Lane: feature\n"
        self.assertTrue(any("carril" in error for error in self.validate(text)))

    def test_duplicate_approval_blocks(self):
        text = self.context() + "## Spec Validator Approval\nverdict: ready\n"
        self.assertTrue(any("ambiguos" in error for error in self.validate(text)))

    def test_suffix_approval_is_ambiguous(self):
        text = self.context() + "## Spec Validator Approval — dictamen anterior\nverdict: ready\n"
        self.assertTrue(any("ambiguos" in error for error in self.validate(text)))

    def test_legacy_plain_state_remains_valid(self):
        self.assertEqual([], self.validate(self.context(state="planning").replace("state: planning", "- planning")))

    def test_narrative_status_is_format_error_not_hyphen_state(self):
        errors = self.validate("## Current status\n- **Spec-validator:** verdict: not ready\n")
        self.assertIn("requiere 'state:", errors[0])
        self.assertNotIn("NO canonico '-'", errors[0])

    def test_template_does_not_activate_commented_human_gates(self):
        template = Path(__file__).resolve().parents[2] / "templates/sdd-context.md"
        self.assertEqual([], self.validate(template.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
