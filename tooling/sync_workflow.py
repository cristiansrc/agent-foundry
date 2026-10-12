#!/usr/bin/env python3
"""Actualiza prompts/permisos de workflow y skills allowlisted, preservando modelos."""
import argparse
import shutil
import re
from pathlib import Path

FIELD_RE = {key: re.compile(rf"^{key}:[ \t]*[^\n]*$", re.M) for key in ("model", "variant", "temperature")}


def split_agent(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("frontmatter ausente")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("frontmatter incompleto")
    return text[4:end], text[end + 4:].lstrip("\n")


def compose_agent(generated: str, installed: str) -> str:
    new_meta, new_body = split_agent(generated)
    old_meta, _ = split_agent(installed)
    frontmatter = new_meta
    for key, pattern in FIELD_RE.items():
        old = pattern.findall(old_meta)
        new = pattern.findall(frontmatter)
        if len(old) > 1 or len(new) > 1:
            raise ValueError(f"frontmatter ambiguo: {key}")
        if old:
            if new:
                frontmatter = pattern.sub(lambda _: old[0], frontmatter, count=1)
            else:
                frontmatter += "\n" + old[0]
        elif new:
            frontmatter = pattern.sub("", frontmatter, count=1)
    frontmatter = frontmatter.strip("\n")
    return f"---\n{frontmatter}\n---\n\n{new_body}"


def sync(generated: Path, installed: Path, skills: list[str]) -> list[Path]:
    source_agents, target_agents = generated / "agents", installed / "agents"
    if not source_agents.is_dir() or not target_agents.is_dir():
        raise ValueError("directorios agents generados/instalados requeridos")
    agent_updates = []
    for source in sorted(source_agents.glob("*.md")):
        target = target_agents / source.name
        if not target.is_file():
            raise ValueError(f"agente instalado inexistente; no se crea automáticamente: {target.name}")
        agent_updates.append((target, compose_agent(source.read_text(encoding="utf-8"),
                                                    target.read_text(encoding="utf-8"))))
    for name in skills:
        source, target = generated / "skills" / name, installed / "skills" / name
        if not (source / "SKILL.md").is_file() or not target.is_dir():
            raise ValueError(f"skill generada/instalada requerida: {name}")
    # Validar todo antes de escribir.
    for target, content in agent_updates:
        target.write_text(content, encoding="utf-8")
    for name in skills:
        source, target = generated / "skills" / name, installed / "skills" / name
        shutil.rmtree(target)
        shutil.copytree(source, target)
    return [target for target, _ in agent_updates] + [installed / "skills" / name for name in skills]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", type=Path, required=True)
    parser.add_argument("--installed", type=Path, required=True)
    parser.add_argument("--skills", nargs="+", required=True)
    args = parser.parse_args()
    for path in sync(args.generated, args.installed, args.skills):
        print(path)


if __name__ == "__main__":
    main()
