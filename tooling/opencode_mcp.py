#!/usr/bin/env python3
"""Read-only, explicitly project-scoped MCP stdio adapter for OpenCode."""

import argparse
import json
import sys
from pathlib import Path

import opencode_bridge as bridge

PROTOCOL_VERSION = "2025-06-18"
INSTRUCTIONS = ("Read-only OpenCode metadata. Select an authorized project on every query. "
                "Missing events do not prove no execution. This server cannot start sessions, "
                "grant permissions, or change files.")
PROJECT = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$"}
SESSION = {"type": "string", "pattern": "^[A-Za-z0-9_-]{1,128}$"}
LIMIT = {"type": "integer", "minimum": 1, "maximum": 100}
TOOLS = [
    {"name": "list_projects", "description": "List authorized direct child projects by name.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "list_sessions", "description": "List limited session metadata for one project.",
     "inputSchema": {"type": "object", "properties": {"project": PROJECT}, "required": ["project"], "additionalProperties": False}},
    {"name": "get_session_status", "description": "Get status type for one verified project session.",
     "inputSchema": {"type": "object", "properties": {"project": PROJECT, "session_id": SESSION},
                     "required": ["project", "session_id"], "additionalProperties": False}},
    {"name": "get_session_events", "description": "Get recent observer metadata for one verified project session.",
     "inputSchema": {"type": "object", "properties": {"project": PROJECT, "session_id": SESSION, "limit": LIMIT},
                     "required": ["project", "session_id"], "additionalProperties": False}},
    {"name": "get_session_messages", "description": "Get message metadata for one verified project session.",
     "inputSchema": {"type": "object", "properties": {"project": PROJECT, "session_id": SESSION, "limit": LIMIT},
                     "required": ["project", "session_id"], "additionalProperties": False}},
]


def error(code, message, request_id):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(request, projects_root: Path, base: str):
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        return error(-32600, "Invalid request", request.get("id") if isinstance(request, dict) else None)
    request_id = request.get("id")
    method = request.get("method")
    if request_id is None:
        return None
    if method == "initialize":
        result = {"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {}},
                  "serverInfo": {"name": "agent-foundry-opencode-readonly", "version": "2.0.0"},
                  "instructions": INSTRUCTIONS}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = request.get("params")
        if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict):
            return error(-32602, "Invalid parameters", request_id)
        name, args = params.get("name"), params.get("arguments", {})
        schemas = {tool["name"]: tool["inputSchema"] for tool in TOOLS}
        if not isinstance(name, str) or name not in schemas:
            return error(-32602, "Unknown tool", request_id)
        schema = schemas[name]
        if set(args) - set(schema["properties"]) or set(schema.get("required", [])) - set(args):
            return error(-32602, "Invalid tool arguments", request_id)
        if "project" in args and (not isinstance(args["project"], str) or
                                  bridge.PROJECT_NAME.fullmatch(args["project"]) is None):
            return error(-32602, "Invalid project", request_id)
        if "session_id" in args and not bridge.valid_session_id(args["session_id"]):
            return error(-32602, "Invalid session ID", request_id)
        limit = args.get("limit", 50 if name == "get_session_messages" else 100)
        if "limit" in args and (type(limit) is not int or not 1 <= limit <= 100):
            return error(-32602, "Invalid limit", request_id)
        try:
            if name == "list_projects":
                data = bridge.projects(projects_root)
            else:
                project = bridge.authorized_project(projects_root, args["project"])
                if name == "list_sessions":
                    data = bridge.sessions(base, project)
                elif name == "get_session_status":
                    data = bridge.status(base, project, args["session_id"])
                elif name == "get_session_events":
                    bridge.verify_session(base, project, args["session_id"])
                    data = bridge.events(project, args["session_id"], limit)
                else:
                    data = bridge.session(base, project, args["session_id"], limit)
        except (OSError, ValueError, UnicodeError, TypeError):
            result = {"content": [{"type": "text", "text": "Consulta no disponible o sesión fuera del proyecto"}], "isError": True}
        else:
            result = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}
    else:
        return error(-32601, "Method not found", request_id)
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects-root", required=True, type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:4096")
    args = parser.parse_args()
    if not args.projects_root.is_absolute() or args.projects_root.is_symlink() or not args.projects_root.is_dir():
        parser.error("raíz de proyectos inválida")
    try:
        base = bridge.client_base(args.base_url)
    except ValueError as exc:
        parser.error(str(exc))
    root = args.projects_root.resolve(strict=True)
    while line := sys.stdin.buffer.readline(65537):
        if len(line) > 65536:
            if not line.endswith(b"\n"):
                while chunk := sys.stdin.buffer.readline(65537):
                    if chunk.endswith(b"\n"):
                        break
            continue
        try:
            request = json.loads(line)
        except (json.JSONDecodeError, UnicodeError):
            response = error(-32700, "Parse error", None)
        else:
            response = handle(request, root, base)
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
