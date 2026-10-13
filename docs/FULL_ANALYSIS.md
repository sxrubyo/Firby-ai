# FIRBY — Análisis Completo del Proyecto

**Fecha:** 2026-07-20
**Analizado por:** 6 agentes en paralelo vía SSH (3.130.46.55)
**Propósito:** Documentación exhaustiva para agentes futuros y referencia técnica

---

## 1. ¿QUÉ ES FIRBY?

Firby es un **asistente virtual con IA** multicanal para clínicas y negocios en Latinoamérica. Atiende pacientes por WhatsApp y Telegram, agenda citas, resuelve objeciones, capta leads, y escala a humanos cuando no sabe algo.

**Arquitectura general:**

```
                     ┌─────────────────────────────────┐
                     │     Reverse Proxy (Caddy)         │
                     │         HTTPS → HTTP:8001         │
                     └──────────┬────────────────────────┘
                                │
                     ┌──────────▼────────────────────────┐
                     │    FastAPI App (app.py)             │
                     │  Firby v9.6.1 on port 8001        │
                     │                                    │
                     │  /webhook/{secret}                 │
                     │    └─ Telegram / WhatsApp Cloud     │
                     │       Evolution / Baileys Bridge    │
                     │  /telegram/shared/{secret}         │
                     │  /admin/{instance_id}/...          │
                     │  /trainer/*                        │
                     │  /health                           │
                     └──────────┬────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼──────┐     ┌─────────▼──────┐     ┌─────────▼──────┐
│ Telegram Bot  │     │ WhatsApp Bridge│     │ Nova Governance│
│              │     │ (Baileys)      │     │ (Rule Engine)  │
│              │     │ Port 8002      │     │                │
└──────────────┘     └────────────────┘     └────────┬───────┘
                                                     │
                              ┌──────────────────────┤
                              │                      │
                    ┌─────────▼──────┐    ┌──────────▼───────┐
                    │ SQLite DB      │    │ FirbyUltra      │
                    │ (firby.db)    │    │ (Core Runtime)   │
                    │ (instances/*/) │    │ ~29K lines       │
                    └────────────────┘    └──────────────────┘
```

### Canales Soportados
| Canal | Estado | Puerto |
|-------|--------|--------|
| Telegram | ✅ Producción | API Bot |
| WhatsApp Cloud | ✅ Producción | API Meta |
| WhatsApp Bridge (Baileys) | ✅ Producción | 8002 |
| Slack | 🟡 Implementado pero no conectado | - |
| CLI | 🟡 Interno (herramienta admin) | - |
| Voice/Audio | ✅ Transcripción multi-provider | - |

### Stack Tecnológico
- **Backend:** Python 3.12, FastAPI
- **LLMs:** Gemini (primario), Groq, OpenRouter, OpenAI (cascada)
- **Base de datos:** SQLite (single file, WAL mode)
- **Infra:** Ubuntu, PM2, Caddy (reverse proxy)
- **Frontend:** React (Next.js) — estático, server-side rendering
- **Monitor:** Omni (herramienta CLI/web propia)

---

## 2. ESTRUCTURA DEL PROYECTO

```
/home/ubuntu/firby/
├── src/
│   ├── core/           ← Runtime antiguo (monolítico, ~12K lines)
│   ├── firby/
│   │   ├── brain/      ← Motor de IA (LLM, memoria, detección)
│   │   ├── channels/   ← Adaptadores de canales (Telegram, Slack, etc.)
│   │   ├── core/       ← Config, router, sesiones, messenger
│   │   ├── admin/      ← Dashboard, API admin, comandos
│   │   ├── production/ ← Sistema de producción (domino, guard, handoff)
│   │   ├── api/        ← Rutas API
│   │   ├── demo/       ← Sistema de demo
│   │   ├── integrations/ ← Calendario, pagos, web search, Notion
│   │   └── plugins/    ← MCP plugin system
│   ├── interfaces/
│   │   └── web/        ← FastAPI app + frontend estático
│   ├── domain/         ← Prompts, onboarding, demo, swarm
│   └── infrastructure/ ← LLM providers (DUPLICADO)
├── v7/                 ← Nueva arquitectura de agentes (router + agents)
├── instances/          ← Instancias (clinica-de-las-americas, etc.)
├── tests/              ← Tests unitarios (30 archivos)
├── scripts/            ← Scripts de admin, parches, utilidades
├── tools/              ← Herramientas de operación (omni, cron, watchdog)
├── docs/               ← Documentación existente
├── personas/           ← Perfiles YAML de personalidad
├── templates/sectors/  ← Plantillas por sector
├── nova/               ← Reglas de gobierno Nova
├── landing/            ← Landing page HTML
└── npm/                ← Proyecto Node.js
```

### Las 4 Instancias Registradas
| Instancia | Rol | Puerto | Estado |
|-----------|-----|--------|--------|
| `base` | admin-base | 8001 | Producción |
| `clinica-de-las-americas` | production-client-admin | 8003 | Producción |
| `melissa-x` | demo-quarantine | 8006 | Demo |
| `ovni` | control-ovni | 8008 | Control |

---

## 3. HALLAZGOS CRÍTICOS

### 🔴 CRÍTICOS (bugs que causan crashes o datos corruptos)

1. **`handoff.py` columna inexistente**: `SELECT patient_raw FROM handoff_queue` pero la schema solo tiene `client_message` → crash silencioso en el sistema de aprendizaje de handoff.

2. **`production/monitor.py`**: La detección de `wants_human` está dentro de un bloque `try/except ImportError`. Si falla el import, **pacientes que piden humano nunca son escalados**.

3. **`v7/orchestrator.py`**: `_notify_escalation()` solo logea — **no notifica al admin**. El agente marca `next_agent="human"` pero nadie recibe la alerta.

4. **Shutdown crash**: `TaskManager` no tiene método `stop()` → crash en cada apagado, riesgo de corrupción de DB.

5. **Código de proveedores LLM duplicado**: Las clases `LLMProvider`, `GroqProvider`, `GeminiProvider`, `OpenRouterProvider`, `OpenAIProvider`, `LLMEngine` existen en **dos archivos**:
   - `src/firby/brain/llm_engine.py` (2710 lines)
   - `src/infrastructure/llm_providers/engine.py` (487 lines)
   - Bug fixes en uno no propagan al otro. Import conflict si ambos son cargados.

6. **`brain/llm_engine.py`**: `_simple_embedding()` usa `math.sqrt` pero **falta `import math`** → `NameError` en runtime.

7. **Agentes V7 VACÍOS**: Los 6 agentes en `v7/agents/` son **scaffolds vacíos** que lanzan `NotImplementedError`. La arquitectura multi-agente no existe realmente.

### 🟡 ALTOS (bugs funcionales mayores)

8. **Monkeypatching frágil**: `app.py` parcha `FirbyUltra._handle_admin_or_setup` con `types.MethodType`. Si la clase cambia, el parche falla silenciosamente.

9. **Archivo `app.py` de ~10,685 líneas**: Contiene webhooks, trainer system, API de dev, SPA serving, monkey-patching. Es un god-class de archivo.

10. **`firby/api/routes.py` (~8,967 lines)**: Near-duplicado de `app.py` con diferencias sutiles. Cambios deben hacerse en 2 lugares.

11. **GlobalProxy anti-patrón**: `db = GlobalProxy("db")`, `Config = GlobalProxy("Config")` — errores de tipeo en nombres crash en runtime. Sin type checking.

12. **Admin key en query params**: `_verify_auth()` acepta `?key=` en URL → expuesto en logs y referrer headers.

13. **Sin rate limiting**: Ningún endpoint tiene rate limiting. Posible abuso.

14. **Servicio de reportes semanales**: `firby_cron.py` genera reportes pero **nunca los envía** (`# TODO: wire send_fn`).

15. **Dos archivos `nova_bridge.py`**: 
    - `/home/ubuntu/firby/nova_bridge.py` (async, httpx)
    - `/home/ubuntu/firby/src/interfaces/nova_bridge.py` (sync, subprocess)
    - Mismo nombre de módulo, APIs diferentes. Confusión de imports.

### 🔶 MEDIOS (bugs de funcionalidad)

16. **Sin webhook de pagos**: `payments.py` genera links de pago pero **no hay webhook** para confirmar pagos recibidos.

17. **`audio.py`**: `from firby_config import Config` — import path no estándar. Fallará en producción sin symlink.

18. **SlackAdapter existe pero no hay endpoint webhook**: El adapter está implementado pero ningún endpoint HTTP recibe eventos de Slack.

19. **`shared_telegram_routes.json` vacío**: `{"routes": {}}` — el router multi-instancia de Telegram no está operativo.

20. **Comentado SPA static mounting**: `app.py` tiene el mounting de Next.js estático comentado. El frontend React no carga.

21. **`app.py` línea ~390**: `app.mount("/_next/static", ...)` comentado → SPA no funciona.

22. **Múltiples errores Gemini 503/429**: Los 7 keys de Gemini frecuentemente devuelven errores. La cascada funciona pero añade latencia (1.3-8.9s por call).

23. **`global.py` y `runtime.py` enormes**: ~12K líneas combinadas. Arquitectura monolítica V6 mezclada con V7.

24. **Volumen extremo de logs**: 1.15M líneas de error. Más de 15MB en logs de error.

### 🔵 BAJOS (code smells, deuda técnica)

25. **6 archivos de test vacíos**: `test_learning.py`, `test_patient_greeting_flow.py`, `test_production_monitor_wiring.py`, `test_redundant_opening_filter.py`, `test_smart_handoff.py`, `test_terminal_capabilities.py` — archivos que existen pero están vacíos.

26. **Sin tests end-to-end**: Ningún test que envíe un mensaje y verifique la respuesta completa.

27. **Sin tests de agentes**: 6 agentes declarados, 0 implementados, 0 tests.

28. **Hardcoded para Colombia**: Ubicación (Medellín), teléfono (formato 3XX-XXX-XXXX), zona horaria (UTC-5), moneda (COP), coloquialismos.

29. **Rutas absolutas hardcodeadas**: `/home/ubuntu/firby/` aparece en múltiples archivos.

30. **Sin tests de seguridad ni performance**: Zero tests de inyección SQL, prompt injection, o carga.

---

## 4. ANÁLISIS POR MÓDULO

### 4.1 Core Runtime (`src/core/` + `src/firby/core/`)

**Archivos clave:**
- `runtime.py` — ~6K lines, maneja el bucle principal de conversación
- `globals.py` — Variables globales compartidas entre módulos
- `orchestrator.py` — Orquestador de la conversación
- `admin_engines.py` — Motores de auto-mejora admin
- `production_monitor.py` — Monitor de producción
- `config.py`, `cron.py`, `messenger.py`, `models.py`, `proxy.py`, `router.py`, `session.py`, `tasks.py`

**Lo que funciona:**
- La cascada de proveedores LLM es robusta (fallthrough en errores)
- El messenger envía mensajes por múltiples plataformas
- El sistema de sesiones mantiene contexto por chat

**Lo que está mal:**
- **`runtime.py` es un monolito** de ~6K líneas
- `production_monitor.py` tiene el bug crítico de `wants_human` dentro de `ImportError`
- El shutdown crash es reproducible
- `router.py` (core) tiene un import faltante de `firby_config`

### 4.2 Brain / Engine (`src/firby/brain/`)

**Archivos clave:**
- `llm_engine.py` (2710 lines) — El archivo más grande. God class.
- `engine.py` (804 lines) — Brain v10.1
- `intelligence.py` (1164 lines) — V8/V9 intelligence suite
- `humanity.py` (1602 lines) — V9 humanization
- `database.py` (1569 lines) — SQLite manager
- `memory.py`, `learning.py`, `filters.py`, `uncertainty.py`, `smart_features.py`

**Lo que funciona:**
- Pipeline de calidad de respuesta extremadamente sofisticado (7+ capas)
- Excelente español colombiano natural
- Few-shot examples para 20+ sectores
- Estrategia V11 "prompt-first, filter-last" es sólida

**Lo que está mal:**
- **Código duplicado** en `brain/llm_engine.py` vs `infrastructure/llm_providers/engine.py`
- **`_simple_embedding()`** falta `import math`
- **God classes**: `llm_engine.py` (2710), `humanity.py` (1602), `database.py` (1569)
- **Duplicación masiva**: detección de emociones en 3 lugares, detección de lenguaje en 3 lugares
- **Sin tests automatizados** en toda la capa de engine
- **Singletons globales** por todas partes

### 4.3 Sistema de Producción (`src/firby/production/`)

| Archivo | Líneas | Función | Bugs |
|---------|--------|---------|------|
| `domino.py` | 2,670 | Demo state machine para prospección B2B | Prompt larguísimo, detección de etapa frágil |
| `guard.py` | 680 | Pipeline guard: detecta respuestas cortadas | `_DANGLING_WORDS` incluye palabras válidas |
| `handoff.py` | 1,050 | Escalación inteligente a humanos | **BUG CRÍTICO**: columna `patient_raw` no existe |
| `monitor.py` | 460 | Manejo de conversaciones reales (no demo) | **BUG**: `wants_human` dentro de ImportError |

### 4.4 Canales (`src/firby/channels/`)

| Archivo | Función | Estado |
|---------|---------|--------|
| `base.py` | ABC para adaptadores | ✅ Bien diseñado |
| `telegram.py` | Adapter Telegram | 🟡 No usado por runtime |
| `whatsapp.py` | Auto-configuración WhatsApp Cloud | ✅ Usado en setup |
| `slack.py` | Adapter Slack | 🟡 No hay endpoint webhook |
| `voice.py` | Humanización post-LLM | ✅ Usado |
| `audio.py` | Transcripción multi-provider | ✅ Excelente, pero import path roto |
| `onboarding.py` | Wizard de setup omnicanal | ✅ Bueno, pero Gmail flow es fake |
| `cli.py` | Dashboard CLI (463KB!) | 🟡 Monstruoso, debería dividirse |

### 4.5 Interfaz Web (`src/interfaces/web/`)

- **`app.py`**: ~10,685 lines. FastAPI app con webhooks, trainer, admin API, SPA.
- **`admin_api.py`**: Endpoints REST para configuración runtime.
- **`demo_handler.py`**: Manejador de demo (embedded en app.py).

**Problemas:**
- Monkey-patching frágil
- Sin rate limiting
- Admin key en query params
- SPA static mounting comentado
- `routes.py` duplica `app.py`

### 4.6 Agentes V7 (`v7/`)

| Archivo | Función | Estado |
|---------|---------|--------|
| `orchestrator.py` | Orquestador central | ✅ Buen diseño |
| `router.py` | Ruteo de intención 3-capas | ✅ Excelente, >85% cubierto |
| `postprocess.py` | Humanización determinística | ✅ Limpio |
| `agents/base.py` | Clase base abstracta | ✅ Bueno |
| `agents/captacion.py` | Captación de leads | 🟡 Import dudoso |
| `agents/objeciones.py` | Manejo de objeciones | 🟡 Regex frágil |
| `agents/conocimiento.py` | Preguntas técnicas | ✅ |
| `agents/agenda.py` | Agenda de citas | 🟡 `disponible` check frágil |
| `agents/seguimiento.py` | Seguimiento pacientes | 🟡 Mezcla usted/tú |
| `agents/escalacion.py` | Emergencias y escalación | 🟡 Regex muy amplio |
| `memory/patient_profile.py` | Perfil persistente de paciente | ✅ Bueno |

### 4.7 Integraciones (`src/firby/integrations/`)

| Integración | Estado | Bugs |
|-------------|--------|------|
| `calendar.py` | GCal + Calendly | Token refresh frágil |
| `payments.py` | Stripe + Bold | **Sin webhook de confirmación** |
| `search.py` | SerpAPI → Brave → Apify | ✅ Excelente |
| `notion.py` | Sync Notion → KB | ✅ Bueno |
| `knowledge.py` | KB con chunking + keywords | ✅ Bueno, split naive |

### 4.8 Tests (`tests/`)

**30 archivos de test Python:**

| Calidad | Cantidad | Descripción |
|---------|----------|-------------|
| ✅ Alto | ~12 | `test_demo_patient_entry.py`, `test_omnichannel_v10.py`, `test_search_and_llm_runtime.py`, etc. |
| 🟡 Medio | ~8 | `test_admin_api.py`, `test_commands.py`, etc. |
| 🔴 Bajo/Vacío | ~10 | 6 vacíos, scripts sin assertions |
| ❌ No existen | - | Tests de agentes V7, tests E2E, tests de seguridad |

---

## 5. DIAGRAMA DE ARQUITECTURA

### Flujo de un mensaje entrante:

```
Webhook HTTP POST
       │
       ▼
app.py: /webhook/{secret}
       │
       ├─ ¿Telegram?  → parse_telegram()
       ├─ ¿WhatsApp Cloud? → parse_wa_cloud()
       ├─ ¿Evolution? → parse_evolution()
       └─ ¿Baileys?   → parse_baileys_bridge()
       │
       ▼
NormalizedMessage (pero NO se usa la clase base — se parsea inline)
       │
       ▼
FirbyUltra._handle_message()
       │
       ├─ admin/setup? → _handle_admin_or_setup() [MONKEYPATCHED]
       ├─ demo? → demo_handler.handle_demo_message()
       └─ production? → FirbyProduction.handle()
              │
              ├─ Agent Router (V7) → router.route()
              ├─ LLM Engine → cascade Gemini → Groq → OpenRouter
              ├─ Post-processing → voice.py, filters.py, guard.py
              └─ Nova Governance → FirbyGuard.should_send()
       │
       ▼
messenger._send_message()
       │
       ├─ Telegram → httpx POST to api.telegram.org
       ├─ WhatsApp Cloud → httpx POST to graph.facebook.com
       └─ WhatsApp Bridge → httpx POST to localhost:8002
```

### Flujo de inicialización:

```
start.sh
  │
  ├─ PM2 → ecosystem.config.js
  │     ├─ firby (port 8001) → app.py
  │     ├─ whatsapp-bridge (port 8002)
  │     ├─ clinica-de-las-americas (port 8003)
  │     └─ omni (port 8007)
  │
  ├─ app.py lifespan:
  │     ├─ init_db()
  │     ├─ init_llm() → cascade providers
  │     ├─ init_v8_systems() → intelligence, humanity
  │     ├─ init_v8_extended_systems() [FALLA: no definido]
  │     ├─ init_observatory()
  │     ├─ init_trainer_systems()
  │     ├─ _patch_admin_dispatcher() [monkeypatch]
  │     └─ _init_brain_v10()
  │
  └─ firby_watchdog.py → cada 60s chequea puertos 8002, 8004
```

---

## 6. BUGS POR SEVERIDAD

### 🔴 Críticos (arreglar inmediatamente)

| ID | Archivo | Línea | Bug |
|----|---------|-------|-----|
| C1 | `handoff.py` | ~890 | `SELECT patient_raw FROM handoff_queue` columna no existe |
| C2 | `production/monitor.py` | ~120 | `wants_human` dentro de `except ImportError` — nunca se ejecuta |
| C3 | `v7/orchestrator.py` | ~45 | `_notify_escalation()` solo logea, no notifica |
| C4 | `firby.py` | ~20459 | `TaskManager.stop()` no existe — crash en shutdown |
| C5 | `brain/llm_engine.py` | ~620 | Falta `import math` en `_simple_embedding()` |
| C6 | `brain/llm_engine.py` + `infrastructure/llm_providers/engine.py` | todo | Código de providers duplicado |
| C7 | `instances/*/firby_agents/*.py` | todos | 6 agentes son scaffolds vacíos |

### 🟡 Altos (arreglar pronto)

| ID | Archivo | Bug |
|----|---------|-----|
| H1 | `app.py` | Monkeypatching frágil |
| H2 | `app.py` + `routes.py` | ~20K lines duplicadas entre ambos |
| H3 | `app.py` | SPA static mounting comentado |
| H4 | `app.py` | Sin rate limiting |
| H5 | `admin_api.py` | Admin key en query params |
| H6 | `brain/humanity.py` + `intelligence.py` | Duplicación de detección emocional |
| H7 | `firby_cron.py` | Reportes semanales generados pero no enviados |
| H8 | `dashboard.py` | Admin key en localStorage |
| H9 | `src/interfaces/nova_bridge.py` | Dos `nova_bridge.py` con APIs diferentes |
| H10 | `channels/audio.py` | Import path `firby_config` no estándar |
| H11 | `brain/database.py` | Sin connection pooling |
| H12 | `brain/llm_engine.py` | God class de 2710 líneas |

### 🔶 Medios

| ID | Bug |
|----|-----|
| M1 | Sin webhook de pagos |
| M2 | SlackAdapter sin endpoint |
| M3 | `shared_telegram_routes.json` vacío |
| M4 | 6 archivos de test vacíos |
| M5 | Sin tests E2E ni de agentes |
| M6 | Sin tests de seguridad |
| M7 | Gemini 503/429 frecuentes |
| M8 | 1.15M líneas de error en logs |
| M9 | Hardcoded Colombia (ubicación, teléfono, moneda) |
| M10 | Rutas absolutas `/home/ubuntu/firby/` |

---

## 7. LO QUE FUNCIONA BIEN ✅

1. **Cascada de proveedores LLM**: Gemini → Groq → OpenRouter con fallthrough y key rotation. Robusta.
2. **Sistema de demo**: Onboarding progresivo, detección de negocio por regex + LLM, 5 sectores con prompts diferenciados.
3. **Pipeline de calidad de respuesta**: 7+ capas de validación, retry, post-procesamiento. Colombiano natural excelente.
4. **Few-shot examples**: 20+ sectores con ejemplos conversacionales completos.
5. **Sistema de handoff**: Escalación a humanos con tickets, TTL, aprendizaje de respuestas.
6. **Búsqueda web**: 3 providers en cascada (SerpAPI → Brave → Apify) con key rotation.
7. **Transcripción de audio**: Gemini → Groq Whisper → OpenRouter Whisper. Triple fallback.
8. **Sistema de memoria**: TF-IDF + cosine similarity para recall. Pragmático (evita dependencias pesadas).
9. **Filtro anti-robot**: Estrategia V11 "prompt-first, filter-last". Excelentes patrones de español colombiano.
10. **Sistema de instancias**: Auto-contenidas con .env, DB, soul, personas. Clonables.
11. **Dashboard en tiempo real**: Monitoreo de conversaciones, búsqueda, análisis cognitivo.
12. **Sistema de entrenamiento admin**: Comandos `/aprender`, `/desaprender`, `/control` para enseñar en lenguaje natural.

---

## 8. LO QUE FALTA ❌

1. **Base de datos vectorial**: Usa TF-IDF en vez de embeddings reales. Escala mal.
2. **Tests end-to-end**: No hay un test que envíe un mensaje real y verifique la respuesta.
3. **Tests de agentes V7**: 6 agentes, 0 tests.
4. **Webhook de pagos**: Stripe/Bold generan links pero nunca confirman el pago.
5. **Conexión Slack**: Adapter existe pero no hay endpoint.
6. **Rate limiting**: Ningún endpoint protegido.
7. **CI/CD**: No hay configuración de integración continua.
8. **Fine-tuning**: No hay ML real — solo matching de keywords y prompts.
9. **Dashboard de analytics**: No hay visualización de conversiones, métricas, etc.
10. **Internacionalización**: Hardcoded para Colombia.
11. **Pruebas de carga**: No hay tests de performance.
12. **Migraciones de DB**: Usa try/except ALTER TABLE en vez de sistema de migraciones.
13. **Documentación de API**: No hay OpenAPI/Swagger completo (FastAPI lo genera automático, pero no hay descripciones).

---

## 9. RECOMENDACIONES PRIORIZADAS

### Inmediato (semana 1)
1. ✅ Arreglar `SELECT patient_raw` en `handoff.py` — cambiar a `client_message`
2. ✅ Sacar `wants_human` del bloque `ImportError` en `monitor.py`
3. ✅ Implementar `_notify_escalation()` real en `v7/orchestrator.py`
4. ✅ Arreglar `TaskManager.stop()` en `firby.py`
5. ✅ Agregar `import math` en `brain/llm_engine.py`
6. ✅ Eliminar archivo duplicado `infrastructure/llm_providers/engine.py` (o el de brain)

### Corto plazo (semana 2-3)
7. Separar `app.py` (~10K lines) en módulos: webhooks, admin, trainer, dev
8. Eliminar o mergear `routes.py` con `app.py`
9. Implementar webhook de pagos (Stripe/Bold)
10. Agregar rate limiting a endpoints críticos
11. Implementar tests E2E con pytest + TestClient
12. Implementar agentes V7 reales o eliminar scaffolds

### Mediano plazo (mes 1-2)
13. Dividir `brain/llm_engine.py` en 3-5 archivos
14. Dividir `brain/humanity.py` en módulos separados
15. Dividir `brain/database.py` en DAOs por dominio
16. Reemplazar GlobalProxy con dependency injection real
17. Agregar base de datos vectorial (Chroma, FAISS, o SQLite + embeddings)
18. Completar modularización de `firby.py`

### Largo plazo (mes 3+)
19. Migrar a base de datos escalable (PostgreSQL)
20. Agregar fine-tuning de modelos por cliente
21. Internacionalización multi-país
22. Dashboard de analytics completo
23. Sistema de A/B testing para prompts
24. CI/CD completo con tests automatizados

---

## 10. COMANDOS ÚTILES

```bash
# SSH a la instancia
ssh -i ~/.ssh/Innvisor.pem ubuntu@3.130.46.55

# Ver estado de PM2
pm2 list
pm2 logs firby --lines 50
pm2 monit

# Ver logs de error
tail -f /home/ubuntu/firby/instances/clinica-de-las-americas/logs/error.log

# Correr tests
cd /home/ubuntu/firby && python -m pytest tests/ -v

# Recargar instancia
pm2 restart firby-clinica-de-las-americas

# Ver health
curl http://localhost:8001/health

# Ver dashboard admin
curl http://localhost:8001/admin/clinica-de-las-americas/status
```

---

## 11. ARQUITECTURA DE ARCHIVOS (no tocar código)

Este proyecto tiene **3 eras arquitectónicas coexistiendo**:

| Era | Filosofía | Archivos | Estado |
|-----|-----------|----------|--------|
| **V6 (Legacy)** | Monolítico, template-based | `firby.py`, `runtime.py` | Produce aún |
| **V8-V11 (Transición)** | Prompt engineering, capas de calidad | `brain/*.py`, `production/*.py` | Activo |
| **V7 (Nuevo)** | Agentes especializados + router | `v7/` | Scaffold |

**Regla de oro:** Si tocas V6, asegúrate de que V7 o V8-V11 no dependan de ello. Si tocas V7, los scaffolds vacíos son intencionales (por ahora). No los implementes sin approval.

**Patrones a seguir:**
- Usa `GlobalProxy` para dependencias circulares (es el estándar aquí)
- Los logs deben ir a `log.warning()` — el sistema tiene logging centralizado
- Los tests usan `pytest` con `AsyncMock` y `pytest.mark.anyio`
- Las personas van en YAML, no en código

**Patrones a evitar:**
- NO agregues más código a `firby.py`, `app.py`, `llm_engine.py` — están en refactor
- NO crees más singletons globales — usa `GlobalProxy`
- NO agregues rutas absolutas hardcodeadas
- NO crees nuevos archivos de 1000+ líneas

---

*Documentación generada por 6 agentes de análisis paralelo el 2026-07-20*
