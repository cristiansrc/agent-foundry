#!/usr/bin/env python3
"""Resumen local de eventos de Agent Foundry, sin leer prompts ni respuestas."""
import argparse
import json
from collections import Counter
from pathlib import Path


def summarize(project: Path) -> dict:
    path = project.resolve() / ".opencode/.foundry/events.jsonl"
    counts, tools, sessions = Counter(), Counter(), set()
    if not path.is_file():
        return {"events": 0, "types": {}, "tools": {}, "sessions": 0,
                "note": "sin eventos; no acredita que el plugin esté instalado o activo"}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("schema") != "foundry/event/v1":
            continue
        counts[item.get("type", "unknown")] += 1
        if item.get("tool"):
            tools[item["tool"]] += 1
        if item.get("session_id"):
            sessions.add(item["session_id"])
    return {"events": sum(counts.values()), "types": dict(counts),
            "tools": dict(tools), "sessions": len(sessions),
            "note": "metadatos parciales; no incluye tokens, coste ni resultado funcional"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.project), ensure_ascii=False, indent=2))
