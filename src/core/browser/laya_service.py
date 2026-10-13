# -*- coding: utf-8 -*-
"""
Firby Laya System-1 Microservice
================================
Expone el protocolo wire de Jev / Laya (POST /v1/systemone) para decisiones
ultrarrápidas de navegación y scroll cinemático en menos de 10 milisegundos.
Ejecutado de forma persistente en PM2 como `laya-service` en el puerto 8005.
"""
from __future__ import annotations

import time
import re
import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("laya.service")

app = FastAPI(
    title="Laya System-1 Decision Service",
    description="Microservicio ultra veloz para decisiones atómicas de navegación y scroll humano en Firby",
    version="1.0.0"
)

# Palabras clave y heurísticas de alta velocidad en memoria
SCROLL_KEYWORDS = {
    "planes": "#planes",
    "precios": "#planes",
    "precio": "#planes",
    "starter": "#planes",
    "pro": "#planes",
    "equipos": "#planes",
    "costo": "#planes",
    "como funciona": "#como-funciona",
    "funciona": "#como-funciona",
    "flujo": "#como-funciona",
    "seguridad": "#seguridad-cumplimiento",
    "privacidad": "#seguridad-cumplimiento",
    "datos": "#seguridad-cumplimiento",
    "cumplimiento": "#seguridad-cumplimiento",
    "problema": "#problema",
    "dolor": "#problema",
    "hero": "#hero",
    "inicio": "#hero",
    "arriba": "#hero"
}


@app.get("/health")
async def health_check():
    """Health check compatible con probes de Laya y PM2."""
    return {
        "status": "ok",
        "service": "laya-systemone",
        "port": 8005,
        "latency_target": "<10ms",
        "timestamp": time.time()
    }


@app.post("/v1/systemone")
async def handle_system_one(request: Request):
    """
    Endpoint Jev / Laya /v1/systemone.
    Resuelve la siguiente operación de interfaz en sub-10ms.
    """
    t_start = time.perf_counter()
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Formato JSON inválido")

    state = str(body.get("state") or "")
    goal = str(body.get("goal") or "")
    if not goal and "Goal:" in state:
        # Extraer goal de state_repr
        g_match = re.search(r"Goal:\s*([^\n]+)", state)
        if g_match:
            goal = g_match.group(1).strip()

    goal_lower = goal.lower()
    chosen_op = "WAIT"
    target_selector = None
    strike_keyword = None
    confidence = 0.85
    reasoning = "Evaluación no-autoregresiva System-1"

    # 1. Chequeo de metas completadas
    if any(w in goal_lower for w in ["gracias", "listo", "termina", "chao", "adios"]):
        chosen_op = "DONE"
        confidence = 0.99
        reasoning = "Conversación o meta completada"

    # 2. Decisión de Navegación y Scroll Lento Guiado
    elif any(k in goal_lower for k in [
        "scroll", "baja", "muéstrame", "ver", "ir a", "navegar", "donde esta",
        "plan", "precio", "costo", "funciona", "seguridad", "guíame", "guiame", "tour"
    ]):
        chosen_op = "SCROLL_SLOW"
        confidence = 0.95
        # Determinar sección objetivo
        for kw, target_id in SCROLL_KEYWORDS.items():
            if kw in goal_lower:
                target_selector = target_id
                break
        if not target_selector:
            target_selector = "#como-funciona" if "funciona" in goal_lower or "guiame" in goal_lower or "tour" in goal_lower else "#planes"
        
        # Detectar palabra a tachar / contrastar si aplica
        strike_match = re.search(r"(?:antes|tacha|sin|no mas|elimina)\s+([a-zA-Z0-9_]+)", goal_lower)
        if strike_match:
            strike_keyword = strike_match.group(1)
        reasoning = f"Scroll suave guiado hacia {target_selector}"

    # 3. Decisión de Clic en Acción o Registro
    elif any(k in goal_lower for k in ["crear cuenta", "registro", "probar", "iniciar prueba", "empezar"]):
        chosen_op = "CLICK"
        target_selector = "#firby-google-auth-btn" if "google" in goal_lower else "/sign-up"
        confidence = 0.92
        reasoning = f"Acción de clic orientada a conversión: {target_selector}"

    # 4. Fallback estándar
    else:
        chosen_op = "WAIT"
        confidence = 0.80
        reasoning = "Esperando entrada o confirmación del usuario"

    latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

    return {
        "model": "laya-browser-systemone-v1",
        "answers": {
            "operation": {
                "choice": chosen_op,
                "confidence": confidence,
                "target": target_selector,
                "strike_keyword": strike_keyword
            }
        },
        "usage": {
            "input_tokens": max(1, len(state.split())),
            "output_tokens": 4
        },
        "latency_ms": latency_ms,
        "reasoning": reasoning
    }


if __name__ == "__main__":
    port = int(os.environ.get("LAYA_PORT", "8005"))
    logger.info(f"Iniciando Laya System-1 Decision Service en puerto {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
