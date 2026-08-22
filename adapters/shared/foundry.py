#!/usr/bin/env python3
"""Utilidades compartidas para los renderizadores de adapters."""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "core"
PROFILES = ROOT / "profiles"

PROVIDERS = ("opencode", "chatgpt", "kiro")


def load_profiles() -> dict:
    return {
        "models": yaml.safe_load((PROFILES / "models.yaml").read_text(encoding="utf-8")),
        "perms": yaml.safe_load((PROFILES / "permissions.yaml").read_text(encoding="utf-8")),
    }


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[4:end].split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:].lstrip("\n")


def core_agents() -> list[tuple[str, dict, str]]:
    """Devuelve [(nombre, frontmatter, cuerpo)] de todos los agentes core."""
    out = []
    for src in sorted(CORE.glob("agents/**/*.md")):
        fm, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        out.append((src.stem, fm, body))
    return out


def copy_skills(out_skills: Path) -> int:
    import shutil
    if out_skills.exists():
        shutil.rmtree(out_skills)
    shutil.copytree(CORE / "skills", out_skills)
    return len(list(out_skills.glob("*/SKILL.md")))


def require_active(models_cfg: dict, provider: str) -> None:
    p = models_cfg["providers"].get(provider, {})
    if not p.get("active"):
        print(f"[{provider}] SIN BINDINGS activos en profiles/models.yaml; "
              f"se genera sin campo model (default del proveedor).")


# Mapeo permisos abstractos -> herramientas Kiro
KIRO_TOOLS_BY_PERMS = {
    (True, True): ["read", "write", "shell"],
    (True, False): ["read", "write"],
    (False, True): ["read", "shell"],
    (False, False): ["read"],
}


def kiro_tools(perms_agent: dict) -> list[str]:
    edit = perms_agent.get("edit") == "allow"
    bash = perms_agent.get("bash") == "allow"
    return KIRO_TOOLS_BY_PERMS[(edit, bash)]
