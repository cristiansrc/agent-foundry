#!/usr/bin/env python3
"""Self-test end-to-end del puente foundry-vision -> LM Studio.

Genera una imagen de prueba con texto conocido y verifica que el modelo VLM
la lea correctamente. Uso:

    uv run --with fastmcp --with requests --with pillow \
        python adapters/lmstudio/selftest.py [VLM_MODEL]
"""
import base64
import io
import json
import os
import sys

import requests
from PIL import Image, ImageDraw

BASE_URL = os.environ.get("VLM_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
MODEL = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VLM_MODEL", "")
SECRETO = "FOUNDRY-2026-VISION-OK"


def make_test_image() -> bytes:
    img = Image.new("RGB", (640, 200), "#1e1e2e")
    d = ImageDraw.Draw(img)
    d.text((30, 40), SECRETO, fill="#cdd6f4", font_size=42)
    d.text((30, 120), "Si lees esto, tu vision local funciona.",
           fill="#a6adc8", font_size=20)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> int:
    if not MODEL:
        print("Uso: selftest.py <id-del-modelo-en-lm-studio>")
        print("Ej: python selftest.py qwen/qwen3-vl-8b")
        return 1

    png = make_test_image()
    data_uri = "data:image/png;base64," + base64.b64encode(png).decode()
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text",
                 "text": f"Transcribe EXACTAMENTE el codigo alfanumerico grande "
                         f"que aparece en la imagen. Responde solo ese codigo."},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }],
        "temperature": 0.0,
        "max_tokens": -1,
    }
    print(f"Probando {MODEL} contra {BASE_URL} ...")
    try:
        r = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=300)
        r.raise_for_status()
        answer = r.json()["choices"][0]["message"]["content"].strip()
        print(f"Respuesta del modelo: {answer!r}")
        # Coincidencia difusa: OCR real puede tener 1-2 caracteres de error
        import difflib
        clean = answer.replace(" ", "").upper()
        ratio = difflib.SequenceMatcher(None, SECRETO, clean).ratio()
        if SECRETO in clean:
            print("\nVISION LOCAL FUNCIONANDO ✓ (lectura exacta)")
            return 0
        if ratio >= 0.85:
            print(f"\nVISION LOCAL FUNCIONANDO ✓ (lectura {ratio:.0%} similar — "
                  "OCR con errores menores, normal en VLM)")
            return 0
        print(f"\nEl modelo respondio pero NO leyo el secreto ({SECRETO}). "
              "¿Seguro que es un modelo multimodal?")
        return 1
    except requests.exceptions.RequestException as e:
        detail = e.response.text[:300] if e.response is not None else ""
        print(f"FALLO: {e}\n{detail}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
