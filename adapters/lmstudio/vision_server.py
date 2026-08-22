#!/usr/bin/env python3
"""Micro servidor MCP de visión para agent-foundry.

Puente stdio -> LM Studio (API OpenAI-compatible) para dar capacidad visual
a agentes cuyo modelo principal no tiene visión. Local y privado: las imágenes
nunca salen de la máquina.

Config por variables de entorno:
    VLM_BASE_URL   default http://127.0.0.1:1234/v1
    VLM_MODEL      modelo multimodal cargable en LM Studio (ej: qwen/qwen3-vl-8b)
    VLM_TIMEOUT_S  timeout por llamada (default 300, cubre cold-load del modelo)

Ejecución (sin instalar nada):  uv run --with mcp --with requests python vision_server.py
"""
import base64
import json
import mimetypes
import os
import sys

import requests
try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

BASE_URL = os.environ.get("VLM_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
MODEL = os.environ.get("VLM_MODEL", "")
TIMEOUT_S = int(os.environ.get("VLM_TIMEOUT_S", "300"))

mcp = FastMCP("foundry-vision")


def _to_data_uri(source: str) -> str:
    """Acepta ruta local o URL http(s); devuelve data URI base64."""
    if source.startswith(("http://", "https://")):
        resp = requests.get(source, timeout=30)
        resp.raise_for_status()
        mime = resp.headers.get("content-type", "image/png").split(";")[0]
        raw = resp.content
    else:
        path = os.path.expanduser(source)
        if not os.path.isfile(path):
            raise ValueError(f"Archivo no encontrado: {path}")
        mime = mimetypes.guess_type(path)[0] or "image/png"
        with open(path, "rb") as f:
            raw = f.read()
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def _ask(data_uri: str, prompt: str) -> str:
    if not MODEL:
        return ("[foundry-vision] VLM_MODEL no configurado: define el id del "
                "modelo multimodal en la config del MCP.")
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }],
        "temperature": 0.1,
        "max_tokens": -1,
        "stream": False,
    }
    try:
        r = requests.post(f"{BASE_URL}/chat/completions", json=payload,
                          timeout=TIMEOUT_S)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return (f"[foundry-vision] Timeout ({TIMEOUT_S}s): ¿está corriendo el "
                f"server de LM Studio y es '{MODEL}' un modelo multimodal?")
    except requests.exceptions.RequestException as e:
        detail = ""
        if e.response is not None:
            detail = e.response.text[:200]
        return f"[foundry-vision] Error llamando a {BASE_URL}: {e} {detail}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"[foundry-vision] Respuesta inesperada del backend: {e}"


@mcp.tool()
def describe_image(source: str, question: str = "") -> str:
    """Analiza una imagen local o URL. Pregunta opcional para enfocar el análisis.

    Args:
        source: Ruta absoluta, ~/relativa o URL http(s) de la imagen.
        question: Pregunta específica sobre la imagen (opcional).
    """
    uri = _to_data_uri(source)
    prompt = question.strip() or (
        "Describe esta imagen con detalle: qué muestra, textos visibles, "
        "elementos de interfaz si los hay, y cualquier dato relevante.")
    return _ask(uri, prompt)


@mcp.tool()
def ocr_image(source: str) -> str:
    """Extrae TODO el texto visible de una imagen preservando el formato de líneas.

    Args:
        source: Ruta absoluta, ~/relativa o URL http(s) de la imagen.
    """
    uri = _to_data_uri(source)
    return _ask(uri, (
        "Extrae transcribiendo TODO el texto visible en esta imagen, línea por "
        "línea, preservando el formato original. No agregues comentarios ni "
        "interpretaciones: solo el texto transcrito."))


@mcp.tool()
def analyze_ui_screenshot(source: str, viewport: str = "desktop") -> str:
    """Analiza un screenshot de UI: layout, componentes, estados visibles y problemas.

    Args:
        source: Ruta absoluta, ~/relativa o URL http(s) del screenshot.
        viewport: desktop | tablet | mobile (afecta qué se espera ver).
    """
    uri = _to_data_uri(source)
    return _ask(uri, (
        f"Analiza este screenshot de interfaz (viewport esperado: {viewport}). "
        "Reporta: 1) estructura y jerarquía visual, 2) componentes identificados "
        "(botones, inputs, tablas...), 3) texto visible relevante, 4) estados "
        "(vacío/cargando/error si son evidentes), 5) problemas potenciales de "
        "usabilidad o recortes. Sé concreto y técnico."))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Diagnóstico sin stdio-MCP: lista modelos y prueba conectividad.
        try:
            r = requests.get(f"{BASE_URL}/models", timeout=10)
            ids = [m["id"] for m in r.json().get("data", [])]
            print(f"Backend OK ({BASE_URL}) | {len(ids)} modelos")
            print(f"Modelo configurado: {MODEL!r} "
                  f"{'✓ presente' if MODEL in ids else '✗ NO está en el catálogo'}")
        except Exception as e:
            print(f"Backend INACCESIBLE: {e}")
        sys.exit(0)
    mcp.run()
