"""Una eval no puede aprobar por logs, prompts o fallos de ejecución."""
import importlib.util
import json
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
