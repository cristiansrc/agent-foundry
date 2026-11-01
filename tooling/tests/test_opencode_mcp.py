"""MCP protocol and safety regression tests without a live OpenCode server."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLING = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLING))
spec = importlib.util.spec_from_file_location("opencode_mcp", TOOLING / "opencode_mcp.py")
mcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp)


class MCPTests(unittest.TestCase):
    def call(self, name, args=None):
        return mcp.handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                           "params": {"name": name, "arguments": args or {}}}, Path("/tmp"), "http://127.0.0.1:4096")

    def test_tools_only_expose_reads(self):
        tools = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, Path("/tmp"), "http://127.0.0.1:4096")
        self.assertEqual({"list_projects", "list_sessions", "get_session_status", "get_session_events", "get_session_messages"},
                         {item["name"] for item in tools["result"]["tools"]})
        self.assertEqual(-32602, self.call("approve_permission")["error"]["code"])

    def test_validation_prevents_backend_call(self):
        with patch.object(mcp.bridge, "session") as backend:
            for args in ({"project": "p", "session_id": "../other"}, {"project": "p", "session_id": "ok", "limit": True},
                         {"project": "p", "session_id": "ok", "extra": "x"}, {"session_id": "ok"},
                         {"project": "../other", "session_id": "ok"}, {}):
                self.assertEqual(-32602, self.call("get_session_messages", args)["error"]["code"])
            backend.assert_not_called()

    def test_errors_do_not_expose_backend_details(self):
        with patch.object(mcp.bridge, "authorized_project", side_effect=ValueError("secret /private/path")):
            output = self.call("list_sessions", {"project": "p"})
        self.assertTrue(output["result"]["isError"])
        self.assertNotIn("secret", json.dumps(output))
        self.assertNotIn("/private/path", json.dumps(output))

    def test_stdio_handshake_and_tool_list(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "one").mkdir()
            (root / "one" / ".opencode").mkdir()
            messages = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_projects", "arguments": {}}},
            ]
            run = subprocess.run([sys.executable, str(TOOLING / "opencode_mcp.py"), "--projects-root", temp],
                                 input="\n".join(json.dumps(m) for m in messages) + "\n",
                                 capture_output=True, text=True, check=True)
            replies = [json.loads(line) for line in run.stdout.splitlines()]
            self.assertEqual([1, 2, 3], [reply["id"] for reply in replies])
            self.assertEqual("2025-06-18", replies[0]["result"]["protocolVersion"])
            self.assertEqual('[{"project": "one"}]', replies[2]["result"]["content"][0]["text"])
            self.assertEqual("", run.stderr)

    def test_project_is_required_per_call(self):
        with patch.object(mcp.bridge, "authorized_project") as selected, patch.object(mcp.bridge, "sessions", return_value=[]):
            self.call("list_sessions", {"project": "one"})
            self.call("list_sessions", {"project": "two"})
        self.assertEqual(["one", "two"], [call.args[1] for call in selected.call_args_list])
        self.assertEqual(-32602, self.call("list_sessions")["error"]["code"])


if __name__ == "__main__":
    unittest.main()
