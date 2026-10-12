#!/usr/bin/env python3
"""Sync acotado invocado por sync.sh; conserva prompts, permisos y skills activos."""
import argparse
import json
import re
from pathlib import Path

MODEL_RE = re.compile(r'^model:[ \t]*([^\r\n]+)', re.M)
ROUTING_RE = re.compile(r'(const ROUTING: Record<string, string> = )(\{.*?\})(;)', re.S)


def header(text: str) -> tuple[str, int]:
    if not text.startswith('---\n'):
        raise ValueError('frontmatter no soportado')
    end = text.find('\n---', 4)
    if end < 0:
        raise ValueError('frontmatter incompleto')
    return text[:end], end


def read_model(text: str) -> str:
    matches = MODEL_RE.findall(header(text)[0])
    if len(matches) != 1:
        raise ValueError('exige un único model en frontmatter')
    return matches[0].strip().strip('"\'')


def replace_model(text: str, model: str) -> str:
    front, end = header(text)
    read_model(text)
    return MODEL_RE.sub(lambda _: f'model: {model}', front, count=1) + text[end:]


def replace_routes(text: str, models: dict[str, str]) -> str:
    match = ROUTING_RE.search(text)
    if not match:
        raise ValueError('ROUTING instalado no reconocido')
    routing_text = match[2]
    routes = json.loads(routing_text)
    for name, model in models.items():
        if name not in routes:
            raise ValueError(f'ruta instalada ausente: {name}')
        pattern = re.compile(r'(' + re.escape(json.dumps(name)) + r'\s*:\s*)"[^"\n]*"')
        routing_text, count = pattern.subn(lambda m: m[1] + json.dumps(model), routing_text)
        if count != 1:
            raise ValueError(f'ruta ambigua: {name}')
    return text[:match.start(2)] + routing_text + text[match.end(2):]


def plan_sync(generated: Path, installed: Path, agents: list[str]) -> dict[Path, str]:
    if not agents or len(set(agents)) != len(agents):
        raise ValueError('lista de agentes vacía/duplicada')
    changes, models = {}, {}
    for name in agents:
        if not re.fullmatch(r'[a-z][a-z0-9-]*', name):
            raise ValueError('nombre de agente inválido')
        model = read_model((generated / 'agents' / f'{name}.md').read_text())
        path = installed / 'agents' / f'{name}.md'
        current = path.read_text()
        changes[path] = replace_model(current, model)
        models[name] = model
    # Sólo bindings; el resto del plugin se conserva, aunque out cambió por otra tarea.
    plugin = installed / 'plugins/foundry-model-router.ts'
    changes[plugin] = replace_routes(plugin.read_text(), models)
    generated_routes = json.loads(ROUTING_RE.search((generated / 'plugin/foundry-model-router.ts').read_text())[2])
    if any(generated_routes.get(name) != model for name, model in models.items()):
        raise ValueError('modelo generado y routing generado no coinciden')
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generated', type=Path, required=True)
    parser.add_argument('--installed', type=Path, required=True)
    parser.add_argument('agents', nargs='+')
    args = parser.parse_args()
    # Preflight completo antes de escribir cualquiera de los archivos.
    changes = plan_sync(args.generated, args.installed, args.agents)
    for path, content in changes.items():
        path.write_text(content)
    for name in args.agents:
        path = args.installed / 'agents' / f'{name}.md'
        print(f'{name}: {read_model(path.read_text())}')


if __name__ == '__main__':
    main()
