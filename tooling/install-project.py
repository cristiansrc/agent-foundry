#!/usr/bin/env python3
"""Instala el bundle generado de Foundry dentro de un proyecto OpenCode.

Por defecto solo informa. --apply copia archivos después de validar conflictos
y guarda un recibo con hashes; nunca escribe en la configuración global.
"""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "install-manifest.yaml"
RECEIPT = Path(".opencode/foundry-install.json")


def validate_target(project: Path, rel: Path) -> Path:
    if rel.is_absolute() or not rel.parts or ".." in rel.parts or rel.parts[0] != ".opencode":
        raise ValueError(f"destino no permitido: {rel}")
    target = project / rel
    if any(p.is_symlink() for p in (target, *target.parents)
           if p != project and project in p.parents):
        raise ValueError(f"destino con symlink: {rel}")
    return target


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mappings() -> dict[Path, Path]:
    cfg = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    result = {}
    for section in ("agents", "skills", "plugins"):
        for entry in cfg.get(section, []):
            source = ROOT / entry["source"]
            dest = Path(entry["destination"])
            if source.is_dir():
                for file in sorted(source.rglob("*")):
                    if file.is_file():
                        result[dest / file.relative_to(source)] = file
            elif source.is_file():
                result[dest] = source
            else:
                raise ValueError(f"fuente generada ausente: {source}")
    if not result:
        raise ValueError("manifiesto sin archivos")
    for rel in result:
        validate_target(ROOT, rel)
    return result


def plan(project: Path) -> tuple[dict[Path, Path], dict, dict]:
    project = project.resolve(strict=True)
    if project == ROOT or not project.is_dir():
        raise ValueError("indica un proyecto destino distinto de agent-foundry")
    target_dir = project / ".opencode"
    if target_dir.is_symlink():
        raise ValueError(".opencode es un symlink")
    receipt_path = project / RECEIPT
    validate_target(project, RECEIPT)
    old = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {"files": {}}
    if not isinstance(old.get("files"), dict):
        raise ValueError("recibo de instalación inválido")
    for name in old["files"]:
        current = validate_target(project, Path(name))
        if current.is_file() and digest(current) != old["files"][name]:
            raise ValueError(f"archivo gestionado modificado fuera del instalador: {name}")
    items = mappings()
    for rel in items:
        target = validate_target(project, rel)
        if target.exists() and rel.as_posix() not in old["files"] and digest(target) != digest(items[rel]):
            raise ValueError(f"conflicto con archivo no gestionado: {rel}")
    config_path = project / ".opencode/opencode.json"
    validate_target(project, Path(".opencode/opencode.json"))
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    default = config.get("default_agent")
    if default not in (None, "master-orchestrator"):
        raise ValueError(f"default_agent existente distinto: {default}")
    config["default_agent"] = "master-orchestrator"
    return items, old, config


def run(project: Path, apply: bool) -> int:
    project = project.resolve(strict=True)
    items, old, config = plan(project)
    stale = set(old["files"]) - {p.as_posix() for p in items}
    changes = {rel: src for rel, src in items.items()
               if not (project / rel).is_file() or digest(project / rel) != digest(src)}
    config_path = project / ".opencode/opencode.json"
    config_text = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    config_changed = not config_path.is_file() or config_path.read_text(encoding="utf-8") != config_text
    print(f"Proyecto: {project}")
    print(f"Archivos nuevos/actualizados: {len(changes)}; obsoletos: {len(stale)}; config: {'cambia' if config_changed else 'igual'}")
    if not apply:
        print("Vista previa. Para instalar: --apply")
        return 0
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = project / ".opencode/backups" / stamp
    validate_target(project, Path(".opencode/backups") / stamp)
    managed_paths = set(changes) | {Path(p) for p in stale}
    if config_changed:
        managed_paths.add(Path(".opencode/opencode.json"))
    for rel in sorted(managed_paths):
        current = project / rel
        if current.is_file():
            destination = backup / rel.relative_to(".opencode")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current, destination)
    for rel, src in changes.items():
        target = project / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    for rel in stale:
        target = project / rel
        if target.is_file():
            target.unlink()
    if config_changed:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(config_text, encoding="utf-8")
    local_state = project / ".opencode/.foundry"
    validate_target(project, Path(".opencode/.foundry"))
    validate_target(project, Path(".opencode/.foundry/.gitignore"))
    local_state.mkdir(parents=True, exist_ok=True)
    (local_state / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")
    receipt = {"schema": "foundry/install/v1", "installed_at": stamp,
               "source": str(ROOT), "files": {rel.as_posix(): digest(src) for rel, src in items.items()}}
    (project / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Instalado. Backup de archivos sustituidos: {backup}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run(args.project, args.apply))
