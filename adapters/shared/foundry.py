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


def validate_bindings(models_cfg: dict) -> list[str]:
    """Slots colgantes en models.yaml -> lista de errores legibles.

    Un tier o un fallback que nombran un slot inexistente reventaba con un
    KeyError desnudo en los renders (kiro/chatgpt) o, peor, caía al segundo
    candidato sin avisar (opencode). Verificado 2026-10-03 al quitar `terra`
    del bloque `chatgpt`: el build de Codex moría en `p["models"][slot]`.
    """
    errors: list[str] = []
    tiers = set(models_cfg.get("tiers") or {})
    for pname, provider in (models_cfg.get("providers") or {}).items():
        models = provider.get("models") or {}
        bindings = provider.get("tier_bindings") or {}
        for tier, slots in bindings.items():
            if tiers and tier not in tiers:
                errors.append(f"{pname}: tier_bindings declara tier desconocido: {tier}")
            for slot in slots or []:
                if slot not in models:
                    errors.append(f"{pname}.{tier}: slot '{slot}' no existe en models")
        for slot, chain in (provider.get("fallbacks") or {}).items():
            if slot not in models:
                errors.append(f"{pname}.fallbacks: origen '{slot}' no existe en models")
            for fb in chain or []:
                if fb not in models:
                    errors.append(f"{pname}.fallbacks[{slot}]: destino '{fb}' no existe en models")
    for agent, info in (models_cfg.get("agent_tiers") or {}).items():
        if info.get("tier") not in tiers:
            errors.append(f"agent_tiers.{agent}: tier desconocido: {info.get('tier')}")
    return errors


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
