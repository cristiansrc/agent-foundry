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

    def delivery(self, status="pending", rounds="1"):
        return (
            "## Review delivery\nbaseline_id: A\nbaseline_scope: contract A\n"
            f"remediation_rounds: {rounds}\ndelivery_status: {status}\n"
            "report_path: docs/reviews/validator-A.md\n"
        )

    def test_pending_delivery_cannot_request_human_gate(self):
        errors = self.validate(self.context() + self.delivery())
        self.assertTrue(any("delivery incomplete" in e for e in errors))

    def test_recovery_pending_is_valid_in_review(self):
        self.assertEqual([], self.validate(self.context(state="validator-review", verdict="pending-review") + self.delivery()))

    def test_claimed_complete_without_report_fails(self):
        errors = self.validate(self.context() + self.delivery("complete"))
        self.assertTrue(any("informe durable" in e for e in errors))

    def test_interrupted_projection_then_completed_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "docs/specs/.working/sample-sdd-context.md"
            path.parent.mkdir(parents=True)
            report = root / "docs/reviews/validator-A.md"
            report.parent.mkdir(parents=True)
            report.write_text("verdict: ready\n", encoding="utf-8")
            original = report.read_bytes()
            path.write_text(self.context(state="validator-review") + self.delivery("report-persisted"), encoding="utf-8")
            self.assertEqual([], MODULE.validate_file(path))
            path.write_text(self.context() + self.delivery("complete"), encoding="utf-8")
            self.assertEqual([], MODULE.validate_file(path))
            self.assertEqual(original, report.read_bytes())

    def test_third_round_and_duplicate_counter_fail(self):
        for text in (self.delivery(rounds="3"), self.delivery() + "remediation_rounds: 0\n"):
            with self.subTest(text=text):
                self.assertTrue(self.validate(self.context(state="validator-review") + text))

    def test_report_outside_repo_cannot_complete_delivery(self):
        errors = self.validate(self.context() + self.delivery("complete").replace("docs/reviews/validator-A.md", "../elsewhere.md"))
        self.assertTrue(any("informe durable" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
