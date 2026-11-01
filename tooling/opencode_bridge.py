#!/usr/bin/env python3
"""Puente local de solo lectura para sesiones/eventos y simulación de permisos.

No contiene métodos de escritura HTTP ni rutas para responder permisos.
"""
import argparse
import base64
import json
import os
import re
import subprocess
from collections import deque
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


def client_base(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Solo se admite un servidor HTTP local sin credenciales en la URL")
    try:
        host = parsed.hostname
        port = parsed.port
        address = ip_address(host) if host != "localhost" else ip_address("127.0.0.1")
    except (ValueError, TypeError):
        raise ValueError("Dirección local inválida") from None
    if not port or not (address.is_loopback or local_route(str(address))):
        raise ValueError("El servidor debe tener una ruta local por loopback")
    return value.rstrip("/")


def local_route(address: str) -> bool:
    """Permit a non-loopback IP only when Linux routes it to this host via lo."""
    try:
        result = subprocess.run(["ip", "route", "get", address], capture_output=True,
                                text=True, timeout=2, check=True)
    except (OSError, subprocess.SubprocessError):
        return False
    first_line = result.stdout.splitlines()[0].split() if result.stdout else []
    return len(first_line) >= 4 and first_line[0:2] == ["local", address] and \
        any(first_line[i:i + 2] == ["dev", "lo"] for i in range(len(first_line) - 1))


def get_json(base: str, endpoint: str):
    headers = {"Accept": "application/json"}
    password = os.environ.get("OPENCODE_SERVER_PASSWORD")
    if password:
        username = os.environ.get("OPENCODE_SERVER_USERNAME", "opencode")
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    request = Request(client_base(base) + endpoint, headers=headers, method="GET")
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, msg, headers, newurl):
            raise ValueError("Redirección HTTP rechazada")

    # Never let HTTP_PROXY/ALL_PROXY receive the Basic header.
    with build_opener(ProxyHandler({}), NoRedirect).open(request, timeout=5) as response:
        return json.load(response)


PROJECT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z")
SESSION_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
MAX_SESSIONS = 100


def authorized_project(root: Path, name: str) -> Path:
    """Only direct, real children with an OpenCode or Foundry project marker."""
    if not isinstance(name, str) or not PROJECT_NAME.fullmatch(name) or name in {".", ".."}:
        raise ValueError("Nombre de proyecto inválido")
    if root.is_symlink():
        raise ValueError("Raíz de proyectos enlazada")
    parent = root.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("Raíz de proyectos inválida")
    candidate = parent / name
    if candidate.is_symlink() or not candidate.is_dir() or candidate.resolve(strict=True).parent != parent:
        raise ValueError("Proyecto no autorizado")
    markers = (candidate / ".opencode", candidate / "install-manifest.yaml")
    if not any(not marker.is_symlink() and (marker.is_dir() if marker.name == ".opencode" else marker.is_file())
               for marker in markers):
        raise ValueError("Proyecto no autorizado")
    return candidate


def projects(root: Path):
    parent = root.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("Raíz de proyectos inválida")
    result = []
    for child in parent.iterdir():
        try:
            authorized_project(parent, child.name)
        except (OSError, ValueError):
            continue
        result.append({"project": child.name})
    return sorted(result, key=lambda item: item["project"])[:MAX_SESSIONS]


def same_project(directory: str, project: Path) -> bool:
    if not isinstance(directory, str):
        return False
    path = Path(directory)
    if not path.is_absolute() or ".." in path.parts or path.is_symlink():
        return False
    try:
        return path.resolve(strict=True) == project.resolve(strict=True) and \
            path.parent.resolve(strict=True) == project.resolve(strict=True).parent
    except (OSError, ValueError):
        return False


def valid_session_id(session_id: str) -> bool:
    return isinstance(session_id, str) and SESSION_ID.fullmatch(session_id) is not None


def string_or_none(value):
    return value if isinstance(value, str) else None


def time_or_none(value):
    return value if type(value) in (int, float) else None


def sessions(base: str, project: Path):
    data = get_json(base, "/session")
    if not isinstance(data, list):
        raise ValueError("Respuesta de sesiones inesperada")
    result = []
    for item in data:
        if not isinstance(item, dict) or not same_project(item.get("directory"), project):
            continue
        timestamp = item.get("time")
        if not isinstance(timestamp, dict):
            timestamp = {}
        if not valid_session_id(item.get("id")):
            continue
        result.append({"id": item["id"],
                       "parent_id": item.get("parentID") if valid_session_id(item.get("parentID")) else None,
                       "created": time_or_none(timestamp.get("created")),
                       "updated": time_or_none(timestamp.get("updated"))})
        if len(result) == MAX_SESSIONS:
            break
    return result


def statuses(base: str, project: Path):
    """Return only status types for sessions whose directory was verified."""
    allowed = {item["id"] for item in sessions(base, project) if isinstance(item.get("id"), str)}
    data = get_json(base, "/session/status")
    if not isinstance(data, dict):
        raise ValueError("Respuesta de estados inesperada")
    return [{"session_id": sid, "status": status["type"]}
            for sid, status in data.items()
            if sid in allowed and isinstance(status, dict)
            and status.get("type") in {"idle", "busy", "retry"}]


def status(base: str, project: Path, session_id: str):
    if not valid_session_id(session_id):
        raise ValueError("ID de sesión inválido")
    verify_session(base, project, session_id)
    data = get_json(base, "/session/status")
    if not isinstance(data, dict):
        raise ValueError("Respuesta de estados inesperada")
    state = data.get(session_id)
    kind = state.get("type") if isinstance(state, dict) else None
    return {"session_id": session_id, "status": kind if isinstance(kind, str) and
            kind in {"idle", "busy", "retry"} else None}


def verify_session(base: str, project: Path, session_id: str):
    if not valid_session_id(session_id):
        raise ValueError("ID de sesión inválido")
    details = get_json(base, f"/session/{quote(session_id, safe='')}")
    if not isinstance(details, dict) or not same_project(details.get("directory"), project):
        raise ValueError("Sesión ajena al proyecto o sin directorio verificable")


def session(base: str, project: Path, session_id: str, limit: int):
    if not valid_session_id(session_id):
        raise ValueError("ID de sesión inválido")
    endpoint = f"/session/{quote(session_id, safe='')}"
    verify_session(base, project, session_id)
    data = get_json(base, f"{endpoint}/message?limit={limit}")
    if not isinstance(data, list):
        raise ValueError("Respuesta de mensajes inesperada")
    result = []
    for item in data:
        if not isinstance(item, dict):
            continue
        info = item.get("info")
        parts = item.get("parts")
        if not isinstance(info, dict):
            info = {}
        if not isinstance(parts, list):
            parts = []
        timestamp = info.get("time")
        if not isinstance(timestamp, dict):
            timestamp = {}
        result.append({"id": info.get("id") if valid_session_id(info.get("id")) else None,
                       "role": info.get("role") if isinstance(info.get("role"), str) and
                               info["role"] in {"user", "assistant"} else None,
                       "agent": info.get("agent") if isinstance(info.get("agent"), str) and
                                re.fullmatch(r"[A-Za-z0-9_-]{1,64}", info["agent"]) else None,
                       "created": time_or_none(timestamp.get("created")),
                       "tools": [part.get("tool") for part in parts
                                 if isinstance(part, dict) and part.get("type") == "tool" and
                                 isinstance(part.get("tool"), str) and
                                 re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", part["tool"])][:20]})
    return result[:limit]


EVENT_TYPES = {"tool.started", "tool.finished", "permission.asked", "permission.replied", "session.idle", "session.error"}


def events(project: Path, session_id: str, limit: int):
    if not valid_session_id(session_id) or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Parámetros de eventos inválidos")
    root = project.resolve()
    folder = root / ".opencode" / ".foundry"
    file = folder / "events.jsonl"
    if any(path.is_symlink() for path in (root / ".opencode", folder, file)):
        raise ValueError("Registro de eventos enlazado fuera del proyecto")
    if not file.is_file():
        return []
    # Bound output and never propagate unrecognized fields from an event.
    rows = deque(maxlen=limit)
    with file.open(encoding="utf-8") as stream:
        while line := stream.readline(65537):
            if len(line) > 65536:
                if not line.endswith("\n"):
                    while chunk := stream.readline(65537):
                        if chunk.endswith("\n"):
                            break
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and item.get("schema") == "foundry/event/v1" and \
                    item.get("session_id") == session_id and isinstance(item.get("type"), str) and \
                    item["type"] in EVENT_TYPES:
                row = {"schema": "foundry/event/v1", "session_id": session_id, "type": item["type"]}
                if isinstance(item.get("at"), str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", item["at"]):
                    row["at"] = item["at"]
                for key in ("call_id", "permission_id"):
                    if valid_session_id(item.get(key)):
                        row[key] = item[key]
                if isinstance(item.get("tool"), str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", item["tool"]):
                    row["tool"] = item["tool"]
                rows.append(row)
    return list(rows)


def simulate(project: Path, request: dict):
    """Classify a proposed action; every result remains a non-binding recommendation."""
    if not isinstance(request, dict):
        raise ValueError("Solicitud inválida")
    action = request.get("action")
    resources = request.get("resources")
    if not isinstance(action, str) or not isinstance(resources, list) or not all(isinstance(x, str) for x in resources):
        raise ValueError("Se requieren action y resources (lista de cadenas)")
    root = project.resolve(strict=True)
    outside = False
    for resource in resources:
        if not resource.startswith("/"):
            outside = True
            continue
        try:
            Path(resource).resolve().relative_to(root)
        except ValueError:
            outside = True
    risky = action not in {"read", "list", "glob", "grep"} or outside or not resources
    return {"mode": "simulation", "recommendation": "escalate-to-human" if risky else "read-candidate",
            "requires_real_approval": True, "reason": "acción fuera del proyecto o con efectos" if risky else "lectura dentro del proyecto",
            "resource_count": len(resources)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects-root", type=Path, default=None,
                        help="Raíz multiproyecto; cuando se usa, --project es un nombre validado")
    parser.add_argument("--project", required=True, help="Nombre de proyecto (con --projects-root) o ruta (modo legado)")
    parser.add_argument("--base-url", default="http://127.0.0.1:4096")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sessions")
    sub.add_parser("statuses")
    item = sub.add_parser("session")
    item.add_argument("id")
    item.add_argument("--limit", type=int, default=50)
    event = sub.add_parser("events")
    event.add_argument("id")
    event.add_argument("--limit", type=int, default=100)
    sim = sub.add_parser("simulate")
    sim.add_argument("--request", required=True, type=Path, help="JSON con action y resources")
    args = parser.parse_args()
    if args.projects_root is not None:
        if not args.projects_root.is_absolute() or args.projects_root.is_symlink() or not args.projects_root.is_dir():
            parser.error("raíz de proyectos inválida")
        try:
            project = authorized_project(args.projects_root.resolve(strict=True), args.project)
        except (OSError, ValueError) as error:
            parser.exit(2, f"Error: {error}\n")
    else:
        legacy = Path(args.project)
        if legacy.is_symlink() or not legacy.is_dir():
            parser.error("proyecto inexistente")
        try:
            project = legacy.resolve(strict=True)
        except (OSError, ValueError) as error:
            parser.exit(2, f"Error: {error}\n")
    limit = getattr(args, "limit", 1)
    if not 1 <= limit <= 500:
        parser.error("limit debe estar entre 1 y 500")
    try:
        if args.command == "sessions":
            output = sessions(args.base_url, project)
        elif args.command == "statuses":
            output = statuses(args.base_url, project)
        elif args.command == "session":
            output = session(args.base_url, project, args.id, args.limit)
        elif args.command == "events":
            verify_session(args.base_url, project, args.id)
            output = events(project, args.id, args.limit)
        else:
            output = simulate(project, json.loads(args.request.read_text(encoding="utf-8")))
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
