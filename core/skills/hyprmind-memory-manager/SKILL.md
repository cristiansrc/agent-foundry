---
name: hyprmind-memory-manager
description: Gestión de memoria conversacional del orquestador personal con caducidad por inactividad.
---

# Skill: hyprmind-memory-manager

## 🎯 Objetivo
Gestionar el contexto conversacional del agente Jhonny (Orchestrator), permitiendo mantener el hilo de la conversación a través del tiempo y aplicando un umbral de caducidad por inactividad.

## 🗂️ Persistencia
*   **Archivo de Estado:** Todo el contexto de la conversación activa se almacena y lee desde un archivo de texto en la ruta: `~/.cache/hyprmind/session_memory.md`.
*   **Formato:** El archivo debe estructurarse como un log de la conversación (`[Timestamp] Persona: Mensaje`).

## ⏳ Lógica del Tiempo de Caducidad (2 Horas)
Al iniciar una nueva iteración de voz, el sistema evalúa la última vez que se modificó el archivo de estado (`session_memory.md`).
1.  **Si han pasado MENOS de 2 horas:** 
    El agente lee el contexto, asume que es una continuación directa de la charla y añade la nueva interacción al archivo.
2.  **Si han pasado MÁS de 2 horas (o el usuario cambia radicalmente de tema de la nada):**
    El agente Jhonny NO debe responder inmediatamente a la nueva petición sin antes aclarar el estado.
    *   **Acción de Jhonny:** Interrumpe amigablemente: *"Oye parcero, hace rato estábamos hablando sobre [Resumen ultra-rápido de 1 línea del archivo]. ¿Seguimos en esa nota o borro el casete y empezamos con esto nuevo que me dices?"*
    *   **Decisión:** 
        *   Si el usuario dice "retomemos" o similar: Jhonny continúa con el contexto anterior.
        *   Si el usuario dice "borra eso", "nuevo tema", o "no, hablemos de esto": El sistema **BORRA** o vacía el archivo `session_memory.md` e inicia un contexto en blanco con la nueva petición.
