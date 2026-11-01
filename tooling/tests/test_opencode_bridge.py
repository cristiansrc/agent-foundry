"""El puente limita salida, proyecto y decisiones a simulación."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("opencode_bridge", Path(__file__).resolve().parents[1] / "opencode_bridge.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def test_authorized_projects_and_real_paths(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            for name in ("one", "two", "plain"):
                (root / name).mkdir()
            (root / "one" / ".opencode").mkdir()
            (root / "two" / "install-manifest.yaml").write_text("x")
            (root / "external").symlink_to(outside, target_is_directory=True)
            self.assertEqual([{"project": "one"}, {"project": "two"}], bridge.projects(root))
            self.assertEqual(root / "two", bridge.authorized_project(root, "two"))
            for name in ("plain", "external", "../one", "/one", "."):
                with self.assertRaises(ValueError):
                    bridge.authorized_project(root, name)

    def test_session_isolation_between_two_projects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            one, two = root / "one", root / "two"
            one.mkdir()
            two.mkdir()
            rows = [{"id": "s-one", "directory": str(one)}, {"id": "s-two", "directory": str(two)}]
            with patch.object(bridge, "get_json", return_value=rows):
                self.assertEqual(["s-one"], [item["id"] for item in bridge.sessions("http://localhost:4096", one)])
                self.assertEqual(["s-two"], [item["id"] for item in bridge.sessions("http://localhost:4096", two)])
            with patch.object(bridge, "get_json", return_value={"directory": str(two)}):
                with self.assertRaises(ValueError):
                    bridge.verify_session("http://localhost:4096", one, "s-two")

    def test_local_url_only(self):
        self.assertEqual("http://127.0.0.1:4096", bridge.client_base("http://127.0.0.1:4096"))
        for url in ("https://127.0.0.1:4096", "http://example.com", "http://user:pass@localhost:4096", "http://localhost:4096/other"):
            with self.assertRaises(ValueError):
                bridge.client_base(url)

    def test_host_address_requires_kernel_local_route(self):
        with patch.object(bridge, "local_route", return_value=True) as route:
            self.assertEqual("http://100.119.146.13:4096", bridge.client_base("http://100.119.146.13:4096"))
            route.assert_called_once_with("100.119.146.13")
        with patch.object(bridge, "local_route", return_value=False):
            with self.assertRaises(ValueError):
                bridge.client_base("http://100.119.146.13:4096")

    def test_local_route_fails_closed(self):
        route = type("Route", (), {"stdout": "local 100.119.146.13 dev lo table local\n"})()
        with patch.object(bridge.subprocess, "run", return_value=route):
            self.assertTrue(bridge.local_route("100.119.146.13"))
        route.stdout = "100.119.146.13 via 192.168.2.1 dev enp6s0\n"
        with patch.object(bridge.subprocess, "run", return_value=route):
            self.assertFalse(bridge.local_route("100.119.146.13"))

    def test_sessions_filter_project_and_sensitive_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = [{"id": "a", "directory": str(root), "title": "secret", "time": {"created": 1}},
                    {"id": "b", "directory": "/other", "title": "other"}]
            with patch.object(bridge, "get_json", return_value=data):
                self.assertEqual([{"id": "a", "parent_id": None, "created": 1, "updated": None}], bridge.sessions("http://localhost:4096", root))

    def test_message_metadata_only_and_project_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = [{"info": {"id": "m", "role": "assistant", "agent": "master-orchestrator", "secret": "hidden"},
                     "parts": [{"type": "text", "text": "secret"}, {"type": "tool", "tool": "read", "state": {"input": "secret"}}]}]
            with patch.object(bridge, "get_json", side_effect=[{"directory": str(root)}, data]):
                result = bridge.session("http://localhost:4096", root, "s", 10)
            self.assertNotIn("secret", json.dumps(result))
            with patch.object(bridge, "get_json", return_value={"directory": "/other"}):
                with self.assertRaises(ValueError):
                    bridge.session("http://localhost:4096", root, "s", 10)

    def test_statuses_filter_project_and_details(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            listed = [{"id": "ours", "directory": str(root)}, {"id": "other", "directory": "/other"}]
            states = {"ours": {"type": "busy", "secret": "hidden"},
                      "other": {"type": "retry", "secret": "other"}}
            with patch.object(bridge, "get_json", side_effect=[listed, states]):
                self.assertEqual([{"session_id": "ours", "status": "busy"}], bridge.statuses("http://localhost:4096", root))

    def test_simulation_never_approves(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inside = str(root / "a")
            for action, resources, expected in (("read", [inside], "read-candidate"),
                                                ("write", [inside], "escalate-to-human"),
                                                ("read", ["/outside"], "escalate-to-human"),
                                                ("read", ["relative"], "escalate-to-human"),
                                                ("read", [], "escalate-to-human")):
                result = bridge.simulate(root, {"action": action, "resources": resources})
                self.assertEqual(expected, result["recommendation"])
                self.assertTrue(result["requires_real_approval"])
                self.assertNotIn(inside, json.dumps(result))

    def test_event_allowlist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / ".opencode/.foundry"
            folder.mkdir(parents=True)
            rows = [
                {"schema": "foundry/event/v1", "session_id": "ours", "type": "tool.started", "tool": "read", "prompt": "secret"},
                {"schema": "foundry/event/v1", "session_id": "other", "type": "tool.started", "tool": "write", "prompt": "secret"},
            ]
            (folder / "events.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
            result = bridge.events(root, "ours", 10)
            self.assertEqual(1, len(result))
            self.assertNotIn("secret", json.dumps(result))
            self.assertNotIn("other", json.dumps(result))

    def test_event_limits_and_rejects_unstructured_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / ".opencode/.foundry"
            folder.mkdir(parents=True)
            file = folder / "events.jsonl"
            rows = [
                {"schema": "foundry/event/v1", "session_id": "ours", "type": "tool.started", "tool": "secret value"},
                {"schema": "foundry/event/v1", "session_id": "ours", "type": "session.idle"},
                {"schema": "foundry/event/v1", "session_id": "ours", "type": "session.error"},
            ]
            file.write_text("".join(json.dumps(row) + "\n" for row in rows))
            result = bridge.events(root, "ours", 2)
            self.assertEqual(["session.idle", "session.error"], [row["type"] for row in result])
            self.assertNotIn("secret", json.dumps(result))

    def test_event_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".opencode").symlink_to(Path(temp).parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                bridge.events(root, "ours", 10)

    def test_status_verifies_session_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(bridge, "get_json", return_value={"directory": "/elsewhere"}):
                with self.assertRaises(ValueError):
                    bridge.status("http://localhost:4096", root, "ours")


if __name__ == "__main__":
    unittest.main()
