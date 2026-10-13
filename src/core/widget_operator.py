"""
Firby AI — Autonomous Operator & Multi-Tenant Cognitive Engine
Arquitectura de Agente Conversacional con Memoria Persistente en SQLite (firby_ultra.db).

Cimientos de Producto de Alta Gama:
1. Arquitectura de Prompts Semánticos XML (inspirada en Claude 3.7 / Anthropic).
2. Slot-Filling State Machine: Rastrear Nombre, Teléfono/WhatsApp, Servicio y Fecha/Hora en segundo plano.
3. Ejecución Real de Herramientas: Inserción atómica en `appointments` y `patients` de SQLite (cero citas simuladas en texto).
4. Notificación Ejecutiva Inmediata al WhatsApp del Dueño (+57 324 369 9856) vía el bridge interno (puerto 8002).
5. Separación Estricta de Modos:
   - Modo Landing de Firby (firby_landing): Venta de la plataforma, prueba gratis 7 días, Google Auth, navegación web.
   - Modo Tenant de Negocio (tenant_id): Operador especializado de la empresa/clínica, catálogo oficial, horarios reales, agendamiento atómico.
6. Guardrails de Seguridad y Estilo: Cero emojis, cero signos invertidos (¿/¡), 1-2 burbujas breves (|||).
"""

import os
import json
import re
import time
import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import httpx

log = logging.getLogger("firby.widget_operator")


# ═════════════════════════════════════════════════════════════════════════════
# PROMPTS SEMÁNTICOS XML (ESTILO ANTHROPIC / CLAUDE 3.7)
# ═════════════════════════════════════════════════════════════════════════════

FIRBY_LANDING_SYSTEM_PROMPT = """<identity>
Eres Firby, la persona de atención y asesoría oficial de https://firbyai.com.
Atiendes a los visitantes con total naturalidad humana, calidez, rapidez y visión ejecutiva.
No eres un chatbot genérico: eres un operador digital autónomo que vive en sitios web de empresas para atender 24/7 y agendar citas confirmadas.
</identity>

<target_audience>
Tu interlocutor es un dueño de negocio, director de clínica, líder comercial o consultor independiente. Invirtió en su página web y pierde prospectos fuera de horario o gasta tiempo valioso en responder las mismas preguntas repetitivas.
</target_audience>

<business_grounding>
- Qué es Firby: El operador digital autónomo para sitios web. Resuelve consultas comerciales en tiempo real con las políticas oficiales del negocio y agenda citas confirmadas sin trabajo manual.
- Dos Canales Estrictos:
  1. En la Web: Atiende a los visitantes y pacientes en tiempo real. Agenda citas y resuelve trámites. Firby NUNCA atiende visitantes por WhatsApp.
  2. En WhatsApp (+57 324 369 9856): Línea ejecutiva privada y continua EXCLUSIVAMENTE con el dueño del negocio. Le envía alertas de citas confirmadas y pide visto bueno para excepciones.
- Instalación: Se integra pegando una sola línea de código en cualquier página (WordPress, Webflow, Shopify, HTML, React) en menos de 60 segundos.
- Planes vigentes (#planes):
  * Starter: $290.000 COP / mes (~$72 USD). Operador autónomo 24/7 en tu web, atención comercial y agendamiento confirmado (hasta 500 interacciones y citas al mes). Prueba 7 días gratis.
  * Pro: $490.000 COP / mes (~$125 USD) [Más Popular]. Autonomía avanzada, supervisión operativa, reprogramación autónoma con código OTP y reglas de gobernanza a la medida (hasta 2.500 interacciones y citas al mes). Prueba 7 días gratis.
  * Equipos: $890.000 COP / mes (~$225 USD). Para empresas con múltiples especialistas o sedes. Hasta 5 agendas concurrentes, roles de equipo y webhooks (hasta 7.500 interacciones al mes).
- Oferta y Garantía: Prueba 7 días gratis. Se activa en 1 minuto vinculando método de pago para verificación de identidad (estilo Netflix/Canva, no se cobra nada durante los 7 días). Cancela cuando quieras en 1 clic sin costo.
- Seguridad (#seguridad-cumplimiento): Cero improvisaciones, solo políticas oficiales, validación de identidad por OTP y visto bueno del dueño para excepciones.
- Acceso a Google Calendar: Firby se sincroniza exclusivamente con la agenda corporativa del negocio para revisar disponibilidad y agendar citas confirmadas. Firby NUNCA accede ni solicita acceso al calendario personal ni citas privadas del visitante.
</business_grounding>

<available_actions>
- Para registro o iniciar prueba gratis:
  [ACTION:GOOGLE_AUTH:Crear cuenta con Google:/auth/google]
  [ACTION:BUTTON:Registrarme con Correo:/sign-up]
- Para hablar con un asesor o dirección:
  [ACTION:BUTTON:Contactar al equipo:https://wa.me/573243699856?text=Hola,%20quiero%20conocer%20mas%20de%20Firby]
- Para desplazar la pantalla del usuario a una sección:
  [CMD:NAV:#planes]
  [CMD:NAV:#como-funciona]
  [CMD:NAV:#seguridad-cumplimiento]
  [CMD:NAV:#problema]
- Para ofrecer opciones rápidas de 1 clic al final:
  [CHIPS: Opción 1 | Opción 2 | Opción 3]
</available_actions>

<cognitive_guidelines>
1. ESTADO DEL DIÁLOGO: {conversation_state_hint}
2. TONO Y EMPATÍA HUMANA:
   - Sé amable, simpático, cercano y sumamente profesional.
   - Si saludan cordialmente, saluda con calidez y naturalidad.
   - Si hacen una pregunta puntual (cálculo, definición, dato oficial), responde directo al grano sin rodeos ni rodeos comerciales.
3. CONVERSACIÓN PERTINENTE Y CIERRE NATURAL:
   - Responde con precisión y veracidad a lo solicitado por el usuario.
   - NO fuerces discursos comerciales ni intentes vender en consultas no comerciales (cálculos, definiciones, chitchat casual).
   - Solo incluye preguntas de seguimiento orientadas cuando el usuario esté explorando opciones y la orientación aporte valor real. En consultas fácticas o directas, concluye con un punto final claro y sobrio.
4. REGLA ANTI-SALUDO: Si ya hay mensajes previos en el historial, QUEDA PROHIBIDO decir "Hola", "Buenas", "Bienvenido" o saludar de nuevo. Responde con calidez y ve directo al punto.
5. LENGUAJE: Español de negocios real, directo y conversacional. Cero clichés tipo "solución integral", "revoluciona" o "en la era digital".
6. RESTRICCIÓN ABSOLUTA DE EMOJIS: Cero emojis o iconos en todo el texto y chips.
7. CERO SIGNOS INVERTIDOS: No uses '¿' ni '¡'. Usa únicamente '?' o '!' al final si formulas una pregunta.
8. RITMO Y CONCISIÓN: Responde en 1 sola burbuja estructurada (máximo 2 si es estrictamente indispensable).
9. ACEPTACIÓN DE TÉRMINOS Y CONDICIONES: Si el usuario dice "Sí, acepto", "acepto los términos" o confirma el consentimiento, responde con calidez, agilidad ejecutiva y proactividad: "Listo, quedamos conectados. Cuéntame, qué te gustaría conocer de Firby o cómo te puedo orientar hoy?". NUNCA uses frases robotizadas ni navegues a ninguna sección sin que lo pidan.
10. RECORRIDO GUIADO Y SCROLL SUAVE: Si el usuario te pide que lo guíes, que hagas un recorrido o que vayas scrolleando suavemente por la página (ej. "guíame y ve scrolleando suavemente por mí", "haz un tour", "scrollea lento"):
    DEBES responder con amabilidad aceptando guiarlo con calma e iniciar el recorrido emitiendo [CMD:NAV:#como-funciona]. Explica brevemente cómo opera Firby y ofrece chips para pasar a la siguiente sección (ej. [CHIPS: Siguiente: Canales | Ver planes | Seguridad]).
</cognitive_guidelines>

<output_contract>
- Formato: Mensaje cohesivo y limpio en una sola burbuja.
- Si corresponde navegar: [CMD:NAV:#seccion] o [CMD:NAV:/ruta].
- Opciones rápidas: [CHIPS: Opción 1 | Opción 2 | Opción 3] solo cuando la consulta sea comercial o de navegación de negocio. En consultas matemáticas, definiciones o chitchat, NO agregues chips.
</output_contract>
"""


TENANT_SYSTEM_PROMPT = """<identity>
Eres el operador digital autónomo y recepcionista oficial de {tenant_name}.
Atiendes a los visitantes de este sitio web con amabilidad genuina, simpatía, rapidez y precisión profesional.
Tu misión principal es orientar al visitante sobre los servicios oficiales del negocio y agendar citas confirmadas en el sistema.
</identity>

<business_grounding>
- Nombre del negocio: {tenant_name}
- Dirección / Ubicación: {address}
- Teléfono de contacto: {phone}
- Horarios de atención: {schedule}
- Servicios y Especialidades: {services}
- Información y Políticas Oficiales: {knowledge_base}
</business_grounding>

<lead_state_slots>
Estado actual de los datos recopilados de este visitante:
- Nombre del paciente: {slot_name}
- Teléfono / WhatsApp: {slot_phone}
- Servicio solicitado: {slot_service}
- Fecha y hora preferida: {slot_datetime}
</lead_state_slots>

<available_actions>
- Cuando tengas los datos indispensables (Servicio, Fecha/Hora, Nombre y Teléfono) para agendar la cita, DEBES emitir el comando de reserva para que el servidor la inserte en la base de datos real:
  [ACTION:BOOK_APPOINTMENT:Nombre:Teléfono:Servicio:Fecha y Hora:Notas adicionales]
- Para solicitar verificación de disponibilidad:
  [ACTION:CHECK_AVAILABILITY:Fecha:Hora]
- Para canalizar una excepción comercial fuera de política con el dueño:
  [ACTION:ESCALATE_HUMAN:Motivo de la excepción]
- Para sugerencias rápidas:
  [CHIPS: Opción 1 | Opción 2 | Opción 3]
</available_actions>

<cognitive_guidelines>
1. ESTADO DEL DIÁLOGO: {conversation_state_hint}
2. TONO Y EMPATÍA HUMANA (RECEPCIONISTA PROFESIONAL Y CÁLIDA):
   - Eres una persona amable, atenta y resolutiva. Transmite calidez, tranquilidad y eficiencia.
   - Usa micro-afirmaciones amables: "Con todo gusto", "Claro que si", "Perfecto", "Excelente eleccion".
3. REGLA DE ORO: SIEMPRE TERMINA CON UNA PREGUNTA GUIADA (CONVERSATIONAL MOMENTUM):
   - NUNCA dejes al usuario sin un camino inmediato. Reduce al mínimo su carga cognitiva.
   - Toda respuesta DEBE terminar SIEMPRE con UNA sola pregunta clara y sencilla que oriente el siguiente paso:
     * Al consultar horario: "Te queda mejor en la mañana o prefieres en la tarde?"
     * Al solicitar datos de contacto: "Me indicas tu nombre completo y tu WhatsApp para apartar tu cupo?"
     * Al responder sobre un servicio: "Te gustaría agendar una valoración para este tratamiento o prefieres consultar los horarios primero?"
     * Al confirmar cita: "Tu cita quedó confirmada para mañana a las 3:00 PM. Tienes alguna otra duda sobre cómo llegar o las recomendaciones previas?"
4. ESTRATEGIA DE SLOT-FILLING (CERO INTERROGATORIOS):
   - Si el visitante quiere una cita pero faltan datos, pídelos con naturalidad en pasos cortos (máximo 1 o 2 datos a la vez).
   - Paso 1: Identifica el servicio y el horario preferido (mañana o tarde).
   - Paso 2: Cuando indique horario, solicita su nombre completo y WhatsApp para apartar cupo.
   - Paso 3: Apenas tengas Nombre, Teléfono, Servicio y Horario, EMITE OBLIGATORIAMENTE la acción:
     [ACTION:BOOK_APPOINTMENT:Nombre:Teléfono:Servicio:Fecha y Hora:Notas]
5. NUNCA FINJAS UNA CITA EN TEXTO: No digas "listo, te agendé" si no estás emitiendo el tag [ACTION:BOOK_APPOINTMENT:...].
6. REGLA ANTI-SALUDO: Si ya hay mensajes previos, nunca vuelvas a saludar. Responde directo y con calidez.
7. CERO EMOJIS: Queda estrictamente prohibido el uso de emojis o iconos.
8. CERO SIGNOS INVERTIDOS: No uses '¿' ni '¡'. Usa únicamente '?' o '!' al final.
9. CONCISIÓN: Responde en 1 o máximo 2 burbujas breves separadas por |||.
</cognitive_guidelines>

<output_contract>
- Formato: Burbuja 1 ||| Burbuja 2 (opcional)
- La última burbuja DEBE terminar obligatoriamente con el signo de interrogación '?' de la pregunta guiada.
- Si se agendó cita: incluye [ACTION:BOOK_APPOINTMENT:...] al final.
- Finaliza siempre con [CHIPS: Opción 1 | Opción 2 | Opción 3].
</output_contract>
"""


# ═════════════════════════════════════════════════════════════════════════════
# MOTOR COGNITIVO DEL OPERADOR (WIDGET OPERATOR)
# ═════════════════════════════════════════════════════════════════════════════

class SessionLockManager:
    """Serializa la ejecución de turnos concurrentes por sesión (user_id) para evitar carreras."""
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
        self._meta_lock = asyncio.Lock()

    async def get_lock(self, user_id: str) -> asyncio.Lock:
        async with self._meta_lock:
            if user_id not in self._locks:
                self._locks[user_id] = asyncio.Lock()
            return self._locks[user_id]


class FirbyWidgetOperator:
    """
    Operador Autónomo Cognitivo con persistencia en SQLite (firby_ultra.db).
    Garantiza memoria real multi-turno, slot-filling, cero amnesia y agendamiento atómico.
    """

    def __init__(self):
        self.gemini_keys = self._load_gemini_keys()
        self.current_key_idx = 0
        self.current_model_idx = 0
        self.db_path = self._resolve_db_path()
        self._lock_manager = SessionLockManager()

    def _resolve_db_path(self, org_id: str = "") -> str:
        """Determina la base de datos correcta priorizando firby_ultra.db."""
        if org_id and org_id not in ("firby_landing", "firby_default", "firby", ""):
            tenant_db = f"/home/ubuntu/firby/instances/{org_id}/firby_ultra.db"
            if os.path.exists(tenant_db):
                return tenant_db
            tenant_db_alt = f"/home/ubuntu/firby/instances/{org_id}/firby.db"
            if os.path.exists(tenant_db_alt):
                return tenant_db_alt

        candidates = [
            "/home/ubuntu/firby/firby_ultra.db",
            "/home/ubuntu/firby/instances/clinica-de-las-americas/firby.db",
            "/home/ubuntu/firby/firby.db"
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return candidates[0]

    def _load_gemini_keys(self) -> List[str]:
        keys = []
        for i in range(1, 15):
            k_name = f"GEMINI_API_KEY_{i}" if i > 1 else "GEMINI_API_KEY"
            v = os.getenv(k_name)
            if v and len(v) > 20 and v not in keys:
                keys.append(v)

        if not keys:
            env_paths = [
                "/home/ubuntu/firby/.env",
                "/home/ubuntu/firby/instances/clinica-de-las-americas/.env"
            ]
            for env_path in env_paths:
                if not os.path.exists(env_path):
                    continue
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("GEMINI_API_KEY"):
                                parts = line.split("=", 1)
                                if len(parts) == 2:
                                    val = parts[1].strip().strip('"').strip("'")
                                    if val and len(val) > 20 and val not in keys:
                                        keys.append(val)
                except Exception as _e:
                    log.warning(f"Error reading env {env_path}: {_e}")

        log.info(f"[FirbyWidgetOperator] {len(keys)} Gemini keys cargadas con éxito.")
        return keys

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN DE HISTORIAL Y ESTADO DE CONVERSACIÓN (SLOT-FILLING)
    # ─────────────────────────────────────────────────────────────────────────

    def _load_history_from_db(self, chat_id: str, limit: int = 8) -> List[Dict[str, str]]:
        """Recupera el historial real desde la tabla conversations de SQLite."""
        if not os.path.exists(self.db_path):
            return []
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, role TEXT, content TEXT, model_used TEXT, instance_id TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)"
                )
                cursor.execute(
                    "SELECT role, content FROM conversations WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                    (chat_id, limit)
                )
                rows = cursor.fetchall()
                history = []
                for r in reversed(rows):
                    history.append({"role": r["role"], "content": r["content"]})
                return history
        except Exception as e:
            log.warning(f"[FirbyWidgetOperator] Error leyendo historial SQLite: {e}")
            return []

    def _save_turn_to_db(self, chat_id: str, role: str, content: str, model_used: str = ""):
        """Guarda permanentemente cada mensaje en SQLite."""
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, role TEXT, content TEXT, model_used TEXT, instance_id TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)"
                )
                cursor.execute(
                    "INSERT INTO conversations (chat_id, role, content, model_used, instance_id) VALUES (?, ?, ?, ?, ?)",
                    (chat_id, role, content, model_used, "widget_web")
                )
                conn.commit()
        except Exception as e:
            log.warning(f"[FirbyWidgetOperator] Error guardando turno en SQLite: {e}")

    def _get_conversation_state(self, chat_id: str) -> Dict[str, Any]:
        """Recupera o inicializa los slots de la sesión (nombre, teléfono, servicio, fecha)."""
        default_state = {
            "phase": "discovery",
            "slots": {
                "name": None,
                "phone": None,
                "service": None,
                "datetime": None,
                "notes": None
            },
            "turn_count": 0
        }
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS conversation_states (chat_id TEXT PRIMARY KEY, state TEXT, updated_at TEXT)"
                )
                row = cur.execute("SELECT state FROM conversation_states WHERE chat_id = ?", (chat_id,)).fetchone()
                if row and row["state"]:
                    data = json.loads(row["state"])
                    if "slots" in data:
                        return data
        except Exception as e:
            log.warning(f"[FirbyWidgetOperator] Error leyendo conversation_state: {e}")
        return default_state

    def _save_conversation_state(self, chat_id: str, state: Dict[str, Any]):
        """Persiste los slots y fase de la conversación en SQLite."""
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS conversation_states (chat_id TEXT PRIMARY KEY, state TEXT, updated_at TEXT)"
                )
                now_iso = datetime.now().isoformat()
                state["updated_at"] = now_iso
                cur.execute("""
                    INSERT INTO conversation_states (chat_id, state, updated_at) VALUES (?, ?, ?)
                    ON CONFLICT(chat_id) DO UPDATE SET state = excluded.state, updated_at = excluded.updated_at
                """, (chat_id, json.dumps(state, ensure_ascii=False), now_iso))
                conn.commit()
        except Exception as e:
            log.warning(f"[FirbyWidgetOperator] Error guardando conversation_state: {e}")

    def _extract_slots_heuristically(self, text: str, current_slots: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae patrones comunes (teléfonos colombianos, nombres, emails) para enriquecer slots."""
        slots = dict(current_slots)

        # 1. Teléfono celular (ej: 300 123 4567, 3101234567, +573001234567)
        phone_match = re.search(r'(?:\+?57\s*)?3\d{2}[\s.-]?\d{3}[\s.-]?\d{4}', text)
        if phone_match and not slots.get("phone"):
            slots["phone"] = phone_match.group(0).replace(" ", "").replace("-", "").replace(".", "")

        # 2. Nombre del usuario ("mi nombre es Juan Perez", "me llamo Juan", "soy Juan")
        name_match = re.search(r'(?:mi nombre es|me llamo|soy)\s+([A-Za-zÁ-ÿ]{2,20}(?:\s+[A-Za-zÁ-ÿ]{2,20})?)', text, re.I)
        if name_match and not slots.get("name"):
            candidate = name_match.group(1).strip().title()
            if candidate.lower() not in ["un", "una", "el", "la", "interesado", "cliente", "paciente", "nuevo"]:
                slots["name"] = candidate

        # 3. Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match and not slots.get("email"):
            slots["email"] = email_match.group(0).strip().lower()

        return slots

    # ─────────────────────────────────────────────────────────────────────────
    # EJECUCIÓN ATÓMICA DE ACCIONES Y AGENDAMIENTO REAL
    # ─────────────────────────────────────────────────────────────────────────

    def _book_appointment_atomic(self, chat_id: str, patient_name: str, phone: str, service: str, datetime_slot: str, notes: str = "", tenant_id: str = "firby_landing") -> Optional[int]:
        """Inserta de forma real e inmutable la cita en la tabla appointments y actualiza patients con aislamiento multi-tenant."""
        effective_tenant = tenant_id or "firby_landing"
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id TEXT DEFAULT 'firby_landing',
                        chat_id TEXT,
                        patient_name TEXT,
                        patient_phone TEXT,
                        patient_email TEXT,
                        service TEXT,
                        datetime_slot TEXT,
                        duration_minutes INTEGER DEFAULT 45,
                        notes TEXT,
                        status TEXT DEFAULT 'confirmed',
                        reminder_sent INTEGER DEFAULT 0,
                        confirmed_at TEXT,
                        cancelled_at TEXT,
                        cancellation_reason TEXT,
                        rescheduled_from INTEGER,
                        created_at TEXT,
                        updated_at TEXT,
                        google_event_id TEXT,
                        nps_status TEXT
                    )
                """)
                now_iso = datetime.now().isoformat()
                cur.execute("""
                    INSERT INTO appointments (tenant_id, chat_id, patient_name, patient_phone, service, datetime_slot, duration_minutes, notes, status, created_at, confirmed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', ?, ?)
                """, (effective_tenant, chat_id, patient_name, phone, service, datetime_slot, 45, notes, now_iso, now_iso))
                apt_id = cur.lastrowid

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        chat_id TEXT PRIMARY KEY,
                        tenant_id TEXT DEFAULT 'firby_landing',
                        name TEXT,
                        phone TEXT,
                        email TEXT,
                        birthdate TEXT,
                        preferences TEXT,
                        medical_notes TEXT,
                        tags TEXT,
                        visits INTEGER DEFAULT 1,
                        total_spent REAL DEFAULT 0.0,
                        avg_satisfaction REAL,
                        no_shows INTEGER DEFAULT 0,
                        services_used TEXT,
                        last_service TEXT,
                        first_seen TEXT,
                        last_seen TEXT,
                        next_appointment TEXT,
                        metadata TEXT
                    )
                """)
                cur.execute("""
                    INSERT INTO patients (chat_id, tenant_id, name, phone, last_service, next_appointment, first_seen, last_seen, visits)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(chat_id) DO UPDATE SET
                        tenant_id = excluded.tenant_id,
                        last_seen = excluded.last_seen,
                        visits = patients.visits + 1,
                        next_appointment = excluded.next_appointment
                        name = COALESCE(NULLIF(excluded.name, ''), patients.name),
                        phone = COALESCE(NULLIF(excluded.phone, ''), patients.phone),
                        last_service = excluded.last_service,
                        next_appointment = excluded.next_appointment,
                        last_seen = excluded.last_seen,
                        visits = patients.visits + 1
                """, (chat_id, patient_name, phone, service, datetime_slot, now_iso, now_iso))
                conn.commit()

            log.info(f"[FirbyWidgetOperator] Cita #{apt_id} registrada con éxito en {self.db_path} para {patient_name}")

            # Disparar alerta en segundo plano al WhatsApp del dueño (+57 324 369 9856)
            asyncio.create_task(self._notify_owner_whatsapp(apt_id, patient_name, phone, service, datetime_slot))
            return apt_id
        except Exception as e:
            log.error(f"[FirbyWidgetOperator] Error insertando cita en DB: {e}", exc_info=True)
            return None

    async def _notify_owner_whatsapp(self, apt_id: int, name: str, phone: str, service: str, datetime_slot: str):
        """Envía notificación ejecutiva inmediata al WhatsApp del dueño vía whatsapp-bridge (puerto 8002)."""
        try:
            msg = (
                f"🔔 *Nueva Cita Confirmada en tu Web*\n\n"
                f"👤 *Paciente:* {name or 'Por confirmar'}\n"
                f"📱 *Teléfono:* {phone or 'No registrado'}\n"
                f"🩺 *Servicio:* {service or 'Consulta general'}\n"
                f"📅 *Horario:* {datetime_slot or 'A convenir'}\n"
                f"🆔 *Reserva:* #{apt_id}\n\n"
                f"Acción autónoma ejecutada por Firby en tu servidor."
            )
            async with httpx.AsyncClient(timeout=4.0) as client:
                await client.post("http://localhost:8002/send", json={
                    "to": "573124348669",
                    "message": msg
                })
                log.info(f"[FirbyWidgetOperator] Alerta WhatsApp enviada con éxito al dueño para cita #{apt_id}")
        except Exception as e:
            log.warning(f"[FirbyWidgetOperator] No se pudo enviar alerta WhatsApp al dueño: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # CONSULTA DE DATOS DEL NEGOCIO (TENANT)
    # ─────────────────────────────────────────────────────────────────────────

    def _get_tenant_info(self, org_id: str) -> Dict[str, str]:
        """Obtiene datos reales del negocio desde SQLite."""
        info = {
            "name": org_id.replace("-", " ").replace("_", " ").title() if org_id else "Nuestro Negocio",
            "address": "Atención presencial y virtual",
            "phone": "nuestra línea principal",
            "schedule": "Lunes a Viernes de 8:00 AM a 6:00 PM y Sábados de 8:00 AM a 1:00 PM",
            "services": "Consulta general, valoración personalizada y procedimientos especializados",
            "knowledge_base": "Atención profesional, rápida y con agendamiento de citas en tiempo real."
        }

        if os.path.exists(self.db_path):
            try:
                with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clinic'")
                    if cursor.fetchone():
                        cursor.execute("SELECT * FROM clinic LIMIT 1")
                        row = cursor.fetchone()
                        if row:
                            r_dict = dict(row)
                            if r_dict.get("name"):
                                info["name"] = r_dict["name"]
                            if r_dict.get("address"):
                                info["address"] = r_dict["address"]
                            if r_dict.get("phone"):
                                info["phone"] = r_dict["phone"]
                            if r_dict.get("schedule"):
                                info["schedule"] = r_dict["schedule"]
                            if r_dict.get("services"):
                                info["services"] = str(r_dict["services"])

                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_base'")
                    if cursor.fetchone():
                        cursor.execute("SELECT raw_text FROM knowledge_base LIMIT 3")
                        kb_rows = cursor.fetchall()
                        if kb_rows:
                            info["knowledge_base"] = " ".join([k["raw_text"] for k in kb_rows if k["raw_text"]])[:1500]
            except Exception as e:
                log.warning(f"Error querying tenant DB {self.db_path}: {e}")

        return info

    # ─────────────────────────────────────────────────────────────────────────
    # ENTRADA PRINCIPAL: PROCESAMIENTO DE MENSAJES
    # ─────────────────────────────────────────────────────────────────────────

    async def handle_message(
        self,
        message: str,
        user_id: str,
        org_id: str = "firby_landing",
        web_context: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        voice_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Atención autónoma con memoria persistente SQLite, seguimiento de slots,
        navegación web copiloto y agendamiento atómico. Serializado por session lock.
        """
        session_lock = await self._lock_manager.get_lock(user_id)
        async with session_lock:
            text = (message or "").strip()
            is_firby_landing = org_id in ("firby_landing", "firby_default", "firby", "")

            # 1. Recuperar historial y estado de slots
            history = self._load_history_from_db(user_id, limit=8)
            conv_state = self._get_conversation_state(user_id)
            conv_state["turn_count"] = conv_state.get("turn_count", 0) + 1
            conv_state["slots"] = self._extract_slots_heuristically(text, conv_state.get("slots", {}))

            # 2. Manejo de Gobernanza: Desafíos y Verificación OTP 2FA
            from src.core.guardrails import guardrails_engine
            pending_otp = guardrails_engine.get_pending_otp(user_id)
            six_digit_match = re.search(r'\b\d{6}\b', text)

            if pending_otp and six_digit_match:
                pin_entered = six_digit_match.group(0)
                verify_res = guardrails_engine.verify_otp(user_id, pin_entered)
                if verify_res.get("success"):
                    action_name = guardrails_engine.actions.get(pending_otp["action_key"], {}).get("name", "Operación Crítica")
                    payload = verify_res.get("action_payload", {})
                    new_email = payload.get("new_email", "")

                    if pending_otp["action_key"] == "change_account_email" and new_email:
                        try:
                            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                                cur = conn.cursor()
                                cur.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, 1))
                                conn.commit()
                                log.info(f"[2FA] Correo de cuenta actualizado exitosamente a: {new_email}")
                        except Exception as _e:
                            log.error(f"[2FA] Error actualizando email en DB: {_e}")

                    success_bubbles = [
                        f"Código verificado con éxito. La acción [{action_name}] ha sido ejecutada de forma segura.",
                        "¿Hay algo más en lo que pueda ayudarte hoy?"
                    ]
                    self._save_turn_to_db(user_id, "user", text)
                    self._save_turn_to_db(user_id, "assistant", " ||| ".join(success_bubbles), model_used="firby-governance-engine")
                    return {
                        "ok": True,
                        "bubbles": success_bubbles,
                        "chips": ["Ver planes", "Cómo funciona Firby", "Seguridad"],
                        "action_card": None,
                        "response": "\n".join(success_bubbles),
                        "ui_action": None
                    }
                else:
                    remaining = verify_res.get("remaining_attempts", 0)
                    fail_bubbles = [
                        "El código ingresado es incorrecto o no coincide con el enviado.",
                        f"Te quedan {remaining} intentos antes de que el token sea revocado por seguridad." if remaining > 0 else "Has superado los 3 intentos permitidos. El token fue revocado."
                    ]
                    self._save_turn_to_db(user_id, "user", text)
                    self._save_turn_to_db(user_id, "assistant", " ||| ".join(fail_bubbles), model_used="firby-governance-engine")
                    return {
                        "ok": True,
                        "bubbles": fail_bubbles,
                        "chips": ["Reenviar código de verificación", "Cancelar operación"],
                        "action_card": None,
                        "response": "\n".join(fail_bubbles),
                        "ui_action": None
                    }

            # 3. Inferencia con DigitalWebOperatorRuntime (Navegación Web, Grounding y Swarm)
            from src.core.operator.runtime import operator_runtime

            async def swarm_llm_caller(prompt: str, hist: List[Dict[str, str]], query: str) -> str:
                res, _ = await self._call_gemini_raw(prompt, hist, query, voice_mode=voice_mode)
                return res or ""

            op_result = await operator_runtime.process_turn(
                message=text,
                user_id=user_id,
                org_id=org_id,
                web_context_dict=web_context,
                history=history,
                llm_caller=swarm_llm_caller,
                agent_id=agent_id,
                voice_mode=voice_mode
            )

            if op_result and op_result.ok:
                # Guardar turno y estado en SQLite
                self._save_turn_to_db(user_id, "user", text)
                if op_result.bubbles:
                    self._save_turn_to_db(
                        user_id,
                        "assistant",
                        " ||| ".join(op_result.bubbles),
                        model_used=f"operator-{op_result.active_agent}"
                    )
                self._save_conversation_state(user_id, conv_state)

                return op_result.to_dict()

            # Fallback de contingencia si el runtime no retornó resultado ok
            log.error("[FirbyWidgetOperator] Conexión LLM fallida. Activando fallback de contingencia.")
            if is_firby_landing:
                fallback_bubbles = [
                    "Puedes comunicarte directamente con nuestro equipo directivo haciendo clic en el botón de abajo."
                ]
                action_card = {
                    "type": "button",
                    "label": "Contactar al equipo",
                    "url": "https://wa.me/573243699856?text=Hola,%20quiero%20conocer%20mas%20de%20Firby"
                }
                chips = ["Ver planes y precios", "Cómo funciona", "Crear mi cuenta"]
            else:
                tenant_info = self._get_tenant_info(org_id)
                fallback_bubbles = [
                    f"Tuvimos una breve pausa en el sistema de {tenant_info['name']}.",
                    f"Puedes comunicarte directamente al {tenant_info['phone']} o intentar de nuevo en un segundo."
                ]
                action_card = None
                chips = ["Agendar una cita", "Horarios de atención", "Servicios disponibles"]

            return {
                "ok": True,
                "bubbles": fallback_bubbles,
                "chips": chips,
                "action_card": action_card,
                "response": "\n".join(fallback_bubbles),
                "ui_action": None
            }

    async def handle_observation(
        self,
        run_id: str,
        observation: Dict[str, Any],
        user_id: str,
        org_id: str = "firby_landing",
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa la observación reportada por la superficie web (frontend), completa la verificación
        y replanifica si la acción falló o retorna la respuesta verificada. Serializado por session lock.
        """
        session_lock = await self._lock_manager.get_lock(user_id)
        async with session_lock:
            from src.core.operator.runtime import operator_runtime
            op_result = await operator_runtime.process_observation(
                run_id=run_id,
                observation_dict=observation,
                user_id=user_id,
                org_id=org_id,
                agent_id=agent_id
            )

            if op_result and op_result.bubbles:
                self._save_turn_to_db(
                    user_id,
                    "assistant",
                    " ||| ".join(op_result.bubbles),
                    model_used=f"operator-{op_result.active_agent}"
                )

            return op_result.to_dict()

    # ─────────────────────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────
    # LLAMADA A GEMINI RAW PARA SWARM Y SUBAGENTES
    # ─────────────────────────────────────────────────────────────────────────

    async def _call_gemini_raw(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        message: str,
        voice_mode: bool = False
    ) -> Tuple[Optional[str], str]:
        """Invoca el pool de inferencia Gemini 3.5 Flash con resiliencia multi-credencial y tokens optimizados."""
        from src.core.inference.gemini_pool import gemini_pool
        max_tokens = 800 if voice_mode else 1200
        return await gemini_pool.generate_turn(
            system_prompt=system_prompt,
            history=history,
            message=message,
            temperature=0.35,
            max_output_tokens=max_tokens
        )

    async def _call_gemini_api_swarm(
        self,
        message: str,
        system_prompt: str = ""
    ) -> Tuple[Optional[str], str]:
        """Interfaz pública/directa para invocar el pool de inferencia Gemini 3.5 Flash."""
        return await self._call_gemini_raw(
            system_prompt=system_prompt,
            history=[],
            message=message
        )

    async def _call_llm(
        self,
        message: str,
        history: List[Dict[str, str]],
        conv_state: Dict[str, Any],
        is_landing: bool,
        org_id: str
    ) -> Tuple[Optional[str], str]:
        turn_count = len(history)
        if turn_count == 0:
            hint = "PRIMER TURNO CON EL VISITANTE. Si saluda cortésmente, saluda con amabilidad. Si pregunta algo puntual, responde su pregunta directamente."
        else:
            hint = f"CONVERSACIÓN EN CURSO (TURNO {turn_count // 2 + 1}). EL VISITANTE YA ESTÁ HABLANDO CONTIGO. QUEDA PROHIBIDO DECIR 'HOLA', 'BUENAS' NI VOLVER A SALUDAR. RESPONDE DIRECTO."

        slots = conv_state.get("slots", {})
        slot_name = slots.get("name") or "Pendiente"
        slot_phone = slots.get("phone") or "Pendiente"
        slot_service = slots.get("service") or "Pendiente"
        slot_datetime = slots.get("datetime") or "Pendiente"

        if is_landing:
            system_prompt = FIRBY_LANDING_SYSTEM_PROMPT.format(conversation_state_hint=hint)
        else:
            t_info = self._get_tenant_info(org_id)
            system_prompt = TENANT_SYSTEM_PROMPT.format(
                tenant_name=t_info["name"],
                address=t_info["address"],
                phone=t_info["phone"],
                schedule=t_info["schedule"],
                services=t_info["services"],
                knowledge_base=t_info["knowledge_base"],
                slot_name=slot_name,
                slot_phone=slot_phone,
                slot_service=slot_service,
                slot_datetime=slot_datetime,
                conversation_state_hint=hint
            )

        from src.core.inference.gemini_pool import gemini_pool
        return await gemini_pool.generate_turn(
            system_prompt=system_prompt,
            history=history,
            message=message,
            temperature=0.25,
            max_output_tokens=1200
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PARSEO DE ACCIONES, COMPONENTES UI Y LIMPIEZA
    # ─────────────────────────────────────────────────────────────────────────

    def _sanitize_response(self, text: str) -> str:
        """Elimina emojis garantizando cero emojis, preservando signos naturales en espanol."""
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff\u2600-\u27bf\u2b50\u231a-\u23f3\u2190-\u21ff]")
        return emoji_pattern.sub("", text).strip()

    @staticmethod
    def is_response_complete(text: str) -> bool:
        """
        Valida que una respuesta conversacional esté íntegra y no sufra truncamiento.
        Detecta terminaciones anómalas en mitad de oración o palabra.
        """
        from src.core.inference.gemini_pool import GeminiInferencePool
        return GeminiInferencePool.is_response_complete(text)

    def _parse_llm_response(self, raw_text: str, is_ongoing: bool):
        ui_action = None
        action_card = None
        chips = []
        booking_action = None

        # 1. Navegación en la web (#sección)
        nav_match = re.search(r'\[CMD:NAV:(#[a-zA-Z0-9_-]+)\]', raw_text)
        if nav_match:
            ui_action = {"type": "navigate", "route": nav_match.group(1)}
            raw_text = raw_text.replace(nav_match.group(0), "")

        # 2. Chips de opciones rápidas
        chips_match = re.search(r'\[CHIPS:(.*?)\]', raw_text)
        if chips_match:
            raw_chips = chips_match.group(1).split("|")
            clean_chips = [self._sanitize_response(c).strip() for c in raw_chips if len(c.strip()) > 1]
            if clean_chips:
                chips = clean_chips
            raw_text = raw_text.replace(chips_match.group(0), "")

        # 3. Google Auth Card
        auth_match = re.search(r'\[ACTION:GOOGLE_AUTH:(.*?):(.*?)\]', raw_text)
        if auth_match:
            action_card = {
                "type": "google_auth",
                "label": self._sanitize_response(auth_match.group(1)).strip() or "Crear cuenta con Google",
                "url": auth_match.group(2).strip() or "/auth/google"
            }
            raw_text = raw_text.replace(auth_match.group(0), "")

        # 4. Botón de acción genérico
        btn_match = re.search(r'\[ACTION:BUTTON:(.*?):(.*?)\]', raw_text)
        if btn_match:
            action_card = {
                "type": "button",
                "label": self._sanitize_response(btn_match.group(1)).strip(),
                "url": btn_match.group(2).strip()
            }
            raw_text = raw_text.replace(btn_match.group(0), "")

        # 5. Acción de Reserva Real (BOOK_APPOINTMENT)
        book_match = re.search(r'\[ACTION:BOOK_APPOINTMENT:(.*?):(.*?):(.*?):(.*?)(?::(.*?))?\]', raw_text)
        if book_match:
            booking_action = {
                "name": book_match.group(1).strip(),
                "phone": book_match.group(2).strip(),
                "service": book_match.group(3).strip(),
                "datetime": book_match.group(4).strip(),
                "notes": book_match.group(5).strip() if book_match.group(5) else ""
            }
            raw_text = raw_text.replace(book_match.group(0), "")

        # 6. Limpieza y división de burbujas (|||)
        raw_parts = [p.strip() for p in raw_text.split("|||") if p.strip()]
        clean_parts = []
        for p in raw_parts:
            p_clean = re.sub(r'\[(CHIPS|CMD|ACTION):[^\]]*\]?', '', p).strip()
            p_clean = re.sub(r'\n{3,}', '\n\n', p_clean).strip()
            if p_clean:
                if is_ongoing:
                    p_clean = re.sub(r'^(Hola[,!.]?|Hola a todos[,!.]?|Buenas[,!.]?|Buen día[,!.]?|Buenas tardes[,!.]?)\s*', '', p_clean, flags=re.IGNORECASE).strip()
                    if p_clean:
                        p_clean = p_clean[0].upper() + p_clean[1:]
                if p_clean:
                    clean_parts.append(p_clean)

        if not chips:
            chips = ["Cómo funciona", "Ver planes y precios", "Crear mi cuenta"] if is_ongoing else ["Cómo funciona", "Ver planes y precios", "Contactar al equipo"]

        return clean_parts or ["Entendido."], ui_action, action_card, chips, booking_action


# Singleton
widget_operator = FirbyWidgetOperator()
