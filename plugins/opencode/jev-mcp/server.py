#!/usr/bin/env python3
"""MCP stdio server for Agent Foundry routing decisions.

The server intentionally uses only the Python standard library so it can be
launched by OpenCode without installing a second runtime package. Provider
credentials are read from the environment and never returned in tool output.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from typing import Any


def provider_config() -> tuple[str, str, str]:
    provider = os.getenv("FOUNDRY_JEV_PROVIDER", "vercel").lower()
    if provider == "typesafe":
        return (
            "https://thejevai.com/v1/systemone",
            os.getenv("JEV_API_KEY", ""),
            "jev-latest",
        )
    return (
        os.getenv("FOUNDRY_JEV_VERCEL_URL", "https://ai-gateway.vercel.sh/v1/evaluate"),
        os.getenv("AI_GATEWAY_API_KEY", ""),
        "typesafe-ai/jev",
    )


def call_jev(arguments: dict[str, Any]) -> dict[str, Any]:
    url, key, model = provider_config()
    if not key:
        raise RuntimeError("Missing provider credential: configure AI_GATEWAY_API_KEY or JEV_API_KEY")
    questions = arguments.get("questions") or default_questions(arguments)
    if provider_config()[0].startswith("https://ai-gateway.vercel.sh"):
        questions = {
            key: ({**question, "type": "boolean"} if question.get("type") == "noul" else question)
            for key, question in questions.items()
        }
    body = {
        "model": model,
        "state": arguments["state"],
        "questions": questions,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return normalize(payload)


def default_questions(arguments: dict[str, Any]) -> dict[str, Any]:
    agents = arguments.get("available_agents") or [
        "planner", "solution-architect", "enterprise-architect",
        "bug-diagnostician", "security-reviewer", "final-validation",
    ]
    return {
        "next_agent": {
            "type": "choice",
            "instructions": "Choose the next authorized Agent Foundry agent for this task.",
            "criteria": {name: name for name in agents},
        },
        "reasoning_level": {
            "type": "choice",
            "instructions": "Choose the minimum reasoning level needed: low, medium, high, or critical.",
            "criteria": {
                "low": "Mechanical or fully specified work",
                "medium": "Several dependencies or moderate interpretation",
                "high": "Architecture, security, RCA, or high-impact decisions",
                "critical": "Irreversible or highly consequential decisions",
            },
        },
        "needs_human_clarification": {
            "type": "noul",
            "instructions": "Does the task require a human decision before routing?",
        },
    }


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    # Vercel uses probability; the native TypeSafe endpoint uses confidence for
    # Choice/Score. Preserve the provider response and expose a common shape.
    answers = payload.get("answers", payload.get("data", {}).get("answers", {}))
    result: dict[str, Any] = {"answers": answers, "model": payload.get("model")}
    result["confidence"] = {
        key: value.get("confidence", value.get("probability"))
        for key, value in answers.items()
        if isinstance(value, dict)
        and ("confidence" in value or "probability" in value)
    }
    return result


def response(request_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
    message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error:
        message["error"] = error
    else:
        message["result"] = result
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        method = request.get("method")
        request_id = request.get("id")
        if method == "initialize":
            response(request_id, {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "foundry-jev", "version": "0.1.0"},
            })
        elif method == "ping":
            response(request_id, {})
        elif method == "tools/list":
            response(request_id, {"tools": [{
                "name": "foundry_route",
                "description": "Select an authorized Agent Foundry agent and reasoning level using Jev.",
                "inputSchema": {
                    "type": "object",
                    "required": ["state"],
                    "properties": {
                        "state": {"description": "Compact routing context as text or JSON.", "type": ["string", "object", "array"]},
                        "available_agents": {"type": "array", "items": {"type": "string"}},
                        "questions": {"type": "object"},
                    },
                },
            }]})
        elif method == "tools/call":
            params = request.get("params", {})
            try:
                result = call_jev(params.get("arguments", {}))
                response(request_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "structuredContent": result})
            except Exception as exc:
                response(request_id, {"content": [{"type": "text", "text": str(exc)}], "isError": True})
        elif method == "notifications/initialized":
            continue
        else:
            response(request_id, error={"code": -32601, "message": f"Method not found: {method}"})


if __name__ == "__main__":
    main()
