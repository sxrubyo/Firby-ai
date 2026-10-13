# Firby Architecture Map

## Qué es Firby

Firby es un runtime base para recepcionistas IA orientadas a WhatsApp y Telegram. El repo público contiene el core reusable: conversación, memoria corta, personalidad, canales, API, CLI y sincronización hacia instancias de negocio. El estado vivo de cada negocio queda fuera del repo.

## Entry points reales

- `firby.py`
  Runtime principal. Levanta FastAPI, webhooks, router de mensajes, memoria, base SQLite, auth de admin, conectores de canal, bridge de calendario y capa LLM.
- `firby_cli.py`
  CLI operativo. Crea instancias, sincroniza runtime, inspecciona estado, administra webhooks, expone `bb`, hace doctor y orquesta despliegue local.
- `npm/firby.js`
  Launcher global para `firby-ai`.

## Núcleo conversacional

- `firby_core/persona_registry.py`
  Carga personas desde YAML y resuelve la persona efectiva por clínica/sector/canal.
- `firby_core/conversation_engine.py`
  Router conversacional liviano para casos que no necesitan gastar LLM: probe de identidad, meta-followups y algunos primeros turnos contextuales.
- `firby_core/first_turn_ops.py`
  Helpers puros de primer turno, saludo, normalización y browser admin de conversaciones.
- `firby_brain_v10.py`
  Memoria corta y anti-loop. Extrae señales del historial reciente para evitar repreguntas y elevar calidad contextual.

## Personalidad y voz

- `personas/firby/base/default.yaml`
  Contrato base de voz.
- `personas/firby/base/estetica_whatsapp.yaml`
  Override específico para estética/WhatsApp.
- `firby_core/prompt_ops.py`
  Construcción del prompt compacto y del prompt largo del runtime.
- `firby.py`
  Sigue concentrando la orquestación de respuesta y la capa posterior al LLM:
  - `_apply_output_pipeline`
  - `_retry_until_human`

## Canales y entrega

- `firby.py`
  Expone los webhooks HTTP y la lógica de entrada/salida por:
  - Telegram
  - WhatsApp Cloud
  - bridges compartidos
- `WhatsAppConnector`
  Integración con envío/salida de mensajes.
- `CalendarBridge`
  Resuelve disponibilidad o notifica al admin cuando la agenda no está integrada.

## Datos y persistencia

- `DatabaseManager` en `firby.py`
  Es la capa de persistencia real. Administra clínica, pacientes, conversaciones, feedback, admins, tokens, reglas de confianza, playbooks y memoria operativa.
- `firby.db`
  Base local de desarrollo o runtime local. No debe vivir en el repo público.

## Operación

- `firby_cli.py`
  El CLI tiene cuatro dominios mezclados en un solo archivo:
  - lifecycle de instancias
  - health/doctor/logs
  - entrenamiento operativo
  - sync/runtime propagation
- `firby_cli_bb.py`
  Capa Black Boss extraída del CLI principal: agente, personalidad, prompt maestro y puente hacia trainer/modelo.

## Tamaño real del problema

- `firby.py`: ~28.5k líneas
- `firby_cli.py`: ~11k líneas

El principal cuello de botella de mantenimiento no es el runtime en sí, sino el acoplamiento de demasiadas responsabilidades en esos dos archivos.

## Qué ya está separado

- persona registry
- conversation engine
- first-turn helpers
- prompt building
- memoria corta v10

## Qué falta separar

### Fase 1

- dejar `ResponseGenerator` como orquestador todavía más delgado
- mover builders auxiliares de identidad/contexto que todavía viven dentro de `firby.py`

### Fase 2

- mover browser admin de conversaciones a `firby_admin/conversation_review_ops.py`
- separar auth/admin lifecycle de `firby.py`

### Fase 3

- partir `firby_cli.py` en:
  - `firby_cli_instances.py`
  - `firby_cli_runtime.py`
  - `firby_cli_common.py`

## Cómo usar Firby hoy

### Runtime local

```bash
python3 firby.py
```

### CLI local

```bash
python3 firby_cli.py --help
python3 firby_cli.py guide
python3 firby_cli.py bb config
```

### Global

```bash
npm install -g firby-ai
firby --help
```

## Riesgos actuales

- `firby.py` todavía mezcla HTTP, DB, LLM, prompts, canales y helpers de negocio.
- `firby_cli.py` todavía mezcla UX, PM2, bridge, sync, config y entrenamiento.
- el `conversation_engine` y `ResponseGenerator` todavía comparten parte del territorio del primer turno; ya no es crítico, pero aún no está completamente consolidado.
