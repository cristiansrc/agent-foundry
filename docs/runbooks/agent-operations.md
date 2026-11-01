# Controles y observabilidad del flujo OpenCode

## Permission Guardian

El bundle instala `foundry-permission-guardian.ts` dentro del proyecto.
Rechaza delegaciones a agentes ausentes del bundle y herramientas externas
(`webfetch`, `websearch`, `mcp_*`) por defecto. Para habilitar una herramienta
concreta, el usuario debe iniciar OpenCode con
`FOUNDRY_EXTERNAL_TOOLS=mcp_servidor_herramienta`. No se permite `*` como
comodín. La decisión vive fuera de archivos editables por los agentes.

`profiles/permissions.yaml` pide autorización nativa para rutas externas,
herramientas web y comandos shell que no figuran en la pequeña lista de lectura
preautorizada. La autorización de una operación puntual no firma Gate 1 o Gate
2. El shell conserva autoridad del usuario del sistema: estos controles no son
un sandbox de sistema operativo. Probarlos en la versión instalada de OpenCode
antes de confiarles datos sensibles.

## Registro local

`foundry-agent-observer.ts` escribe únicamente metadatos en
`<proyecto>/.opencode/.foundry/events.jsonl`: inicio/fin de tool y eventos de
permiso o sesión. No persiste prompts, argumentos ni respuestas. El instalador
crea `.gitignore` para ese directorio. El router deja modelo solicitado/asignado
en el log estructurado de OpenCode, no en el JSONL.

```bash
python3 tooling/observe.py --project <ruta>
```

Los conteos no prueban que una tarea haya cumplido la spec ni que una
aprobación sea auténtica. Faltan IDs de incremento, hashes de baseline,
resultados de tests, uso real de tokens y costes por paso. Añadirlos requiere
un contrato de eventos con el runtime y pruebas de privacidad.

## Evolución controlada

1. Congelar la versión de fuentes, perfiles, bundle y recibo instalado.
2. Registrar ejecuciones representativas con datos sintéticos o redactados.
3. Convertir fallos observados en casos de regresión.
4. Cambiar una variable por vez: prompt, modelo o política.
5. Comparar calidad, permisos y consumo con repeticiones.
6. Revisar el diff y desplegar primero en un proyecto piloto.
7. Promover o restaurar el bundle anterior según resultados.
