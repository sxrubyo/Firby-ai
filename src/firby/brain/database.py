# -*- coding: utf-8 -*-
"""Motor de Base de Datos modularizado de globals.py."""
from __future__ import annotations
import os
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any, Set

log = logging.getLogger("firby.database")

# Proxies dinámicos para evitar import circular en la inicialización
from src.firby.core.proxy import GlobalProxy

Config = GlobalProxy("Config")
_KB_AVAILABLE = GlobalProxy("_KB_AVAILABLE")
KnowledgeBase = GlobalProxy("KnowledgeBase")
from src.firby.core.models import Task, MCPPlugin, ConversationState, IntentType, MemoryItem
from pathlib import Path
try:
    from src.firby.brain.firby_fts5_memory import FTS5SessionStore, CuratedMemoryStore
except ImportError:
    from firby_fts5_memory import FTS5SessionStore, CuratedMemoryStore

class DatabaseManager:
    """Gestor de base de datos con soporte para vectores y FTS5."""
    
    def __init__(self, db_path: str, vector_path: str):
        self.db_path = db_path
        self.vector_path = vector_path
        self._init_databases()
        try:
            self.fts_store = FTS5SessionStore(Path(db_path))
            memory_dir = Path(db_path).parent / "memories"
            self.curated_memories = CuratedMemoryStore(memory_dir)
        except Exception as _fts_err:
            log.warning(f"[DatabaseManager] FTS5 initialization error: {_fts_err}")
            self.fts_store = None
            self.curated_memories = None
    
    def get_dev_account(self, email: str) -> Optional[Dict]:
        import sqlite3
        try:
            with sqlite3.connect("/home/ubuntu/firby/firby_ultra.db") as c:
                row = c.execute("SELECT email, password_hash, created_at FROM dev_accounts WHERE email = ?", (email,)).fetchone()
                if row:
                    return {"email": row[0], "password_hash": row[1], "created_at": row[2]}
        except Exception as e:
            pass
        return None

    def create_dev_account(self, email: str, password_hash: str) -> bool:
        import sqlite3
        import secrets
        success = False
        try:
            with sqlite3.connect("/home/ubuntu/firby/firby_ultra.db") as c:
                c.execute("CREATE TABLE IF NOT EXISTS dev_accounts (email TEXT PRIMARY KEY, password_hash TEXT, created_at TEXT DEFAULT (datetime('now')))")
                c.execute("INSERT OR REPLACE INTO dev_accounts (email, password_hash) VALUES (?, ?)", (email, password_hash))
            success = True
        except Exception as e:
            try:
                log.error(f"Error creating dev account: {e}")
            except Exception:
                pass
        try:
            with self._conn() as c:
                existing = c.execute("SELECT chat_id FROM admins WHERE email = ?", (email,)).fetchone()
                if existing:
                    c.execute("""
                        UPDATE admins
                        SET password_hash = ?, is_active = 1
                        WHERE email = ?
                    """, (password_hash, email))
                else:
                    c.execute("""
                        INSERT INTO admins (chat_id, email, password_hash, name, role, is_active)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (f"owner_{secrets.token_hex(4)}", email, password_hash, email.split("@")[0], "owner"))
            success = True
        except Exception as e:
            try:
                log.error(f"Error creating admin account: {e}")
            except Exception:
                pass
        return success

    def _init_databases(self):
        """Inicializa ambas bases de datos."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._conn() as c:
            c.executescript("""
            -- Configuración de clínica extendida
            CREATE TABLE IF NOT EXISTS clinic (
                id INTEGER PRIMARY KEY,
                name TEXT DEFAULT '',
                tagline TEXT DEFAULT '',
                address TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                website TEXT DEFAULT '',
                services TEXT DEFAULT '[]',
                schedule TEXT DEFAULT '{}',
                holidays TEXT DEFAULT '[]',
                timezone TEXT DEFAULT 'America/Bogota',
                currency TEXT DEFAULT 'COP',
                
                -- Personalidad de Firby
                persona_config TEXT DEFAULT '{}',
                
                -- Configuración de negocio
                business_rules TEXT DEFAULT '{}',
                pricing TEXT DEFAULT '{}',
                promotions TEXT DEFAULT '[]',
                
                -- Admin
                admin_chat_ids TEXT DEFAULT '[]',
                notification_settings TEXT DEFAULT '{}',
                payment_config TEXT DEFAULT '{}',
                payment_rules TEXT DEFAULT '{}',
                
                -- Estado
                setup_done INTEGER DEFAULT 0,
                setup_step TEXT DEFAULT 'idle',
                setup_buffer TEXT DEFAULT '{}',
                
                -- Metadata
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            INSERT OR IGNORE INTO clinic (id) VALUES (1);

            -- Migracion segura: agregar columna knowledge_base si no existe
            -- (no falla si ya existe en DBs antiguas)

            -- Conversaciones con análisis
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                analysis TEXT DEFAULT '{}',
                tokens_used INTEGER DEFAULT 0,
                model_used TEXT DEFAULT '',
                latency_ms INTEGER DEFAULT 0,
                ts TEXT DEFAULT (datetime('now')),
                instance_id TEXT DEFAULT 'firby'
            );
            CREATE INDEX IF NOT EXISTS idx_conv_chat ON conversations(chat_id);
            CREATE INDEX IF NOT EXISTS idx_conv_ts ON conversations(ts);
            
            -- Citas extendidas
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                patient_name TEXT DEFAULT '',
                patient_phone TEXT DEFAULT '',
                patient_email TEXT DEFAULT '',
                service TEXT DEFAULT '',
                datetime_slot TEXT DEFAULT '',
                duration_minutes INTEGER DEFAULT 60,
                notes TEXT DEFAULT '',
                status TEXT DEFAULT 'pendiente',
                reminder_sent INTEGER DEFAULT 0,
                confirmed_at TEXT,
                cancelled_at TEXT,
                cancellation_reason TEXT DEFAULT '',
                rescheduled_from INTEGER,
                google_event_id TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_apt_chat ON appointments(chat_id);
            CREATE INDEX IF NOT EXISTS idx_apt_status ON appointments(status);
            CREATE INDEX IF NOT EXISTS idx_apt_datetime ON appointments(datetime_slot);
            
            -- Pacientes con perfil completo
            CREATE TABLE IF NOT EXISTS patients (
                chat_id TEXT PRIMARY KEY,
                name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                birthdate TEXT DEFAULT '',
                preferences TEXT DEFAULT '{}',
                medical_notes TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                
                -- Métricas
                visits INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                avg_satisfaction REAL DEFAULT 0,
                no_shows INTEGER DEFAULT 0,
                
                -- Historial
                services_used TEXT DEFAULT '[]',
                last_service TEXT DEFAULT '',
                
                -- Fechas
                first_seen TEXT DEFAULT (datetime('now')),
                last_seen TEXT DEFAULT (datetime('now')),
                next_appointment TEXT DEFAULT ''
            );
            
            -- Estado de conversación
            CREATE TABLE IF NOT EXISTS conversation_states (
                chat_id TEXT PRIMARY KEY,
                state TEXT DEFAULT '{}',
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Rutas de transporte por chat para recordar el canal real
            CREATE TABLE IF NOT EXISTS contact_routes (
                chat_id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                channel_identity TEXT DEFAULT '',
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            -- GOD MODE: Gestión dinámica de modelos
            CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,       -- ej: "gpt-4-turbo"
                provider TEXT,             -- ej: "openai", "anthropic", "gemini"
                model_id TEXT,             -- ej: "gpt-4-0125-preview"
                api_key TEXT,              -- si es override, sino NULL usa env
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            );

            -- GOD MODE: Configuración en caliente
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Memoria semántica
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                category TEXT DEFAULT 'general',
                importance REAL DEFAULT 0.5,
                accessed_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                last_accessed TEXT DEFAULT (datetime('now')),
                metadata TEXT DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_mem_chat ON memories(chat_id);
            CREATE INDEX IF NOT EXISTS idx_mem_category ON memories(category);
            
            -- Tareas autónomas
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                data TEXT DEFAULT '{}',
                result TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                scheduled_for TEXT,
                started_at TEXT,
                completed_at TEXT,
                retries INTEGER DEFAULT 0,
                error TEXT DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_task_scheduled ON tasks(scheduled_for);
            
            -- Plugins MCP
            CREATE TABLE IF NOT EXISTS mcp_plugins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                version TEXT DEFAULT '1.0.0',
                enabled INTEGER DEFAULT 0,
                config TEXT DEFAULT '{}',
                capabilities TEXT DEFAULT '[]',
                endpoints TEXT DEFAULT '{}',
                health_status TEXT DEFAULT 'unknown',
                last_check TEXT,
                installed_at TEXT DEFAULT (datetime('now'))
            );
            
            -- Métricas y analytics
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                dimensions TEXT DEFAULT '{}',
                ts TEXT DEFAULT (datetime('now')),
                instance_id TEXT DEFAULT 'firby'
            );
            CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type, metric_name);
            CREATE INDEX IF NOT EXISTS idx_metrics_ts ON metrics(ts);
            
            -- Optimizaciones aprendidas
            CREATE TABLE IF NOT EXISTS learned_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                trigger_pattern TEXT NOT NULL,
                optimization TEXT NOT NULL,
                success_rate REAL DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            -- Logs de auto-mejora
            CREATE TABLE IF NOT EXISTS self_improvement_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement_type TEXT NOT NULL,
                description TEXT NOT NULL,
                before_state TEXT DEFAULT '{}',
                after_state TEXT DEFAULT '{}',
                impact_score REAL DEFAULT 0,
                applied INTEGER DEFAULT 0,
                ts TEXT DEFAULT (datetime('now')),
                instance_id TEXT DEFAULT 'firby'
            );
            
            -- Feedback de usuarios
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                conversation_id INTEGER,
                rating INTEGER,
                comment TEXT DEFAULT '',
                sentiment REAL DEFAULT 0,
                ts TEXT DEFAULT (datetime('now')),
                instance_id TEXT DEFAULT 'firby'
            );
            
            -- Cache de respuestas
            CREATE TABLE IF NOT EXISTS response_cache (
                hash TEXT PRIMARY KEY,
                response TEXT NOT NULL,
                hit_count INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                last_hit TEXT DEFAULT (datetime('now')),
                ttl_seconds INTEGER DEFAULT 3600
            );

            -- Tokens de activacion (generados por Santiago, enviados a clinicas)
            -- formato: ACTV-{clinic_id}-{32 chars aleatorios}
            CREATE TABLE IF NOT EXISTS activation_tokens (
                token TEXT PRIMARY KEY,
                clinic_label TEXT DEFAULT '',
                created_by TEXT DEFAULT 'santiago',
                created_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                used_at TEXT,
                used_by_chat_id TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1
            );

            -- Administradores por instancia de Firby
            -- Cada Firby puede tener multiples admins con distintos roles
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL UNIQUE,
                email TEXT DEFAULT '',
                password_hash TEXT DEFAULT '',
                name TEXT DEFAULT '',
                role TEXT DEFAULT 'admin',   -- owner | admin | viewer
                activated_by_token TEXT DEFAULT '',
                invited_by_chat_id TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                last_login TEXT DEFAULT '',
                login_attempts INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_admins_chat ON admins(chat_id);
            CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);

            -- Estado de autenticacion por sesion de chat
            CREATE TABLE IF NOT EXISTS auth_sessions (
                chat_id TEXT PRIMARY KEY,
                flow TEXT DEFAULT '',
                step TEXT DEFAULT '',
                temp_data TEXT DEFAULT '{}',
                attempts INTEGER DEFAULT 0,
                started_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Historial de inicios de sesion y registros (Google, Email, Token)
            CREATE TABLE IF NOT EXISTS auth_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                provider TEXT NOT NULL,           -- google, email_password, token, dev_master_key
                action TEXT NOT NULL,             -- login, signup, oauth_callback, logout
                status TEXT NOT NULL DEFAULT 'success', -- success, failed
                name TEXT DEFAULT '',
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                details TEXT DEFAULT '{}',        -- JSON metadata
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_auth_logs_email ON auth_logs(email);
            CREATE INDEX IF NOT EXISTS idx_auth_logs_created ON auth_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_auth_logs_provider ON auth_logs(provider);

            -- Códigos de verificación OTP por email (6 dígitos, TTL 10m, anti-fuerza bruta)
            CREATE TABLE IF NOT EXISTS email_verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                purpose TEXT NOT NULL DEFAULT 'verification',
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 5,
                verified INTEGER DEFAULT 0,
                expires_at TEXT NOT NULL,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_email_verif_lookup ON email_verification_codes(email, verified);
            CREATE INDEX IF NOT EXISTS idx_email_verif_created ON email_verification_codes(created_at);
            CREATE INDEX IF NOT EXISTS idx_email_verif_ip ON email_verification_codes(ip_address, created_at);

            -- Feedback del admin sobre conversaciones especificas
            -- Cuando el admin corrige o elogia una respuesta de Firby
            CREATE TABLE IF NOT EXISTS conversation_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,           -- chat_id del PACIENTE
                message_id TEXT DEFAULT '',      -- referencia al mensaje comentado
                feedback_text TEXT NOT NULL,     -- lo que dijo el admin
                feedback_type TEXT DEFAULT 'correction', -- correction | praise | instruction
                context TEXT DEFAULT '',         -- los mensajes de contexto
                created_by TEXT DEFAULT '',      -- chat_id del admin
                created_at TEXT DEFAULT (datetime('now'))
            );

            -- Carpeta de confianza: reglas de comunicacion aprendidas del feedback
            -- Firby consulta esto antes de responder
            CREATE TABLE IF NOT EXISTS trust_folder (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT DEFAULT 'general', -- objection | tone | closing | product | flow
                rule TEXT NOT NULL,              -- la regla aprendida en lenguaje natural
                example_bad TEXT DEFAULT '',     -- como NO hacerlo
                example_good TEXT DEFAULT '',    -- como SI hacerlo
                source TEXT DEFAULT 'admin',     -- admin | auto
                weight REAL DEFAULT 1.0,         -- importancia (se puede subir/bajar)
                times_applied INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Instrucciones naturales del admin
            CREATE TABLE IF NOT EXISTS admin_instructions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                instruction TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            );

            -- Playbooks aprendidos del dueño
            -- Trigger + ejemplo exacto de cómo responder
            CREATE TABLE IF NOT EXISTS behavior_playbooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT DEFAULT 'general',
                trigger_text TEXT NOT NULL,
                instruction TEXT DEFAULT '',
                response_example TEXT NOT NULL,
                bubble_count INTEGER DEFAULT 1,
                source TEXT DEFAULT 'admin',
                weight REAL DEFAULT 1.0,
                times_used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Memoria permanente — nunca se borra, sobrevive crashes y resets
            -- Es la carpeta de identidad de Firby para esta clínica
            CREATE TABLE IF NOT EXISTS core_memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'identity',  -- identity|clinic|patient|learned
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Canales vinculados (V10 Omnicanal)
            CREATE TABLE IF NOT EXISTS linked_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,                -- slack, telegram, whatsapp
                channel_identity TEXT NOT NULL,        -- bot token, phone number, etc.
                config_json TEXT DEFAULT '{}',         -- JSON con parámetros de configuración extra
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_linked_channels_platform ON linked_channels(platform);
            """)

        # Migraciones seguras
        with self._conn() as c:
            for col_sql in [
                "ALTER TABLE clinic ADD COLUMN knowledge_base_raw TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN wa_phone_id TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN wa_access_token TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN wa_verify_token TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN gcal_refresh_token TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN calendly_link TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN onboarding_done INTEGER DEFAULT 0",
                "ALTER TABLE clinic ADD COLUMN platform TEXT DEFAULT 'telegram'",
                "ALTER TABLE patients ADD COLUMN metadata TEXT DEFAULT '{}'",
                "ALTER TABLE appointments ADD COLUMN google_event_id TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN payment_config TEXT DEFAULT '{}'",
                "ALTER TABLE clinic ADD COLUMN payment_rules TEXT DEFAULT '{}'",
                "ALTER TABLE appointments ADD COLUMN nps_status TEXT DEFAULT 'pending'",
                "ALTER TABLE clinic ADD COLUMN google_maps_review_url TEXT DEFAULT ''",
                "ALTER TABLE clinic ADD COLUMN assistant_name TEXT DEFAULT 'Firby'",
                "ALTER TABLE clinic ADD COLUMN agent_name TEXT DEFAULT 'Firby'",
                "ALTER TABLE contact_routes ADD COLUMN channel_identity TEXT DEFAULT ''",
            ]:
                try:
                    c.execute(col_sql)
                except sqlite3.OperationalError:
                    pass

        log.info(f"✓ Database inicializada: {self.db_path}")
    
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-32000")  # ~32MB cache
        return conn
    
    # ─── Clinic Operations ──────────────────────────────────────────────────────
    
    def get_clinic(self) -> Dict[str, Any]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM clinic WHERE id=1").fetchone()
            if row:
                data = dict(row)
                # Parse JSON fields
                for field in ['services', 'schedule', 'holidays', 'persona_config', 
                             'business_rules', 'pricing', 'promotions', 
                             'admin_chat_ids', 'notification_settings']:
                    try:
                        data[field] = json.loads(data.get(field, '{}') or '{}')
                    except Exception:
                        data[field] = {} if field not in ['services', 'holidays', 'promotions', 'admin_chat_ids'] else []
                return data
            return {}
    
    def update_clinic(self, **kwargs):
        if not kwargs:
            return
        
        # Serialize JSON fields
        for k, v in kwargs.items():
            if isinstance(v, (dict, list)):
                kwargs[k] = json.dumps(v, ensure_ascii=False)
        
        kwargs['updated_at'] = datetime.now().isoformat()
        sets = ", ".join(f"{k}=?" for k in kwargs)
        
        with self._conn() as c:
            c.execute(f"UPDATE clinic SET {sets} WHERE id=1", list(kwargs.values()))
    
    # ─── Conversation Operations ────────────────────────────────────────────────
    
    def save_message(self, chat_id: str, role: str, content: str, 
                    analysis: Dict = None, model: str = "", latency: int = 0):
        # OJO: el chat guardado acá solo se va a poder leer después si
        # get_history() ve el MISMO INSTANCE_ID. Si esta instancia nunca
        # seteó INSTANCE_ID en su .env, cae al default compartido "firby" —
        # que funciona bien solo mientras sea consistente. Advertencia abajo.
        _instance_id = os.getenv("INSTANCE_ID")
        if not _instance_id:
            log.warning(
                "[save_message] INSTANCE_ID no está seteado en el .env de esta "
                "instancia — usando default compartido 'firby'. Si dos instancias "
                "distintas comparten ese mismo default, sus conversaciones se "
                "pueden mezclar o desaparecer entre sí en la misma base de datos."
            )
        with self._conn() as c:
            # DEDUPLICACIÓN: Evitar guardar exactamente el mismo mensaje consecutivamente para un chat
            try:
                last = c.execute(
                    "SELECT role, content FROM conversations WHERE chat_id=? ORDER BY id DESC LIMIT 1",
                    (chat_id,)
                ).fetchone()
                if last and last["role"] == role and last["content"].strip() == content.strip():
                    return
            except Exception as _dedup_err:
                log.warning(f"[save_message] Error en deduplicación: {_dedup_err}")

            c.execute("""
                INSERT INTO conversations 
                (chat_id, role, content, analysis, model_used, latency_ms, instance_id)
                VALUES (?,?,?,?,?,?,?)
            """, (chat_id, role, content, 
                  json.dumps(analysis or {}, ensure_ascii=False), 
                  model, latency, _instance_id or "firby"))

        if self.fts_store:
            try:
                session_id = f"sess_{chat_id}"
                self.fts_store.record_message(
                    session_id=session_id,
                    chat_id=chat_id,
                    role=role,
                    content=content,
                    instance_id=_instance_id or "firby"
                )
            except Exception as _fts_rec_err:
                log.warning(f"[save_message] FTS record error: {_fts_rec_err}")

    def search_fts_messages(self, query: str, chat_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca mensajes usando el motor FTS5 de alta velocidad con BM25 ranking."""
        if not self.fts_store:
            return []
        try:
            return self.fts_store.search(query, chat_id=chat_id, limit=limit)
        except Exception as e:
            log.warning(f"[search_fts_messages] Search error: {e}")
            return []
    
    def add_admin_instruction(self, chat_id: str, instruction: str):
        """Guarda una nueva instruccion natural del admin."""
        try:
            with self._conn() as c:
                c.execute(
                    "INSERT INTO admin_instructions (chat_id, instruction) VALUES (?, ?)",
                    (chat_id, instruction)
                )
        except Exception as e:
            log.warning(f"add_admin_instruction error: {e}")

    def get_active_admin_instructions(self) -> List[str]:
        """Obtiene todas las instrucciones activas del admin."""
        try:
            with self._conn() as c:
                rows = c.execute(
                    "SELECT instruction FROM admin_instructions WHERE is_active=1 ORDER BY created_at ASC"
                ).fetchall()
                return [r["instruction"] for r in rows]
        except Exception:
            return []

    def clear_admin_instructions(self):
        """Desactiva todas las instrucciones actuales."""
        try:
            with self._conn() as c:
                c.execute("UPDATE admin_instructions SET is_active=0")
        except Exception:
            pass

    def get_history(self, chat_id: str, limit: int = None) -> List[Dict]:
        limit = limit or Config.MAX_CONTEXT_MESSAGES
        _instance_id = os.getenv("INSTANCE_ID") or "firby"
        with self._conn() as c:
            rows = c.execute("""
                SELECT role, content, analysis, ts 
                FROM conversations
                WHERE chat_id=? AND instance_id=?
                ORDER BY ts DESC LIMIT ?
            """, (chat_id, _instance_id, limit)).fetchall()

            # Diagnóstico: si no apareció nada, confirmar si es un chat_id
            # genuinamente nuevo o si el problema es que INSTANCE_ID no
            # coincide con lo que se usó al guardar (bug real, no paciente nuevo).
            if not rows:
                try:
                    probe = c.execute(
                        "SELECT COUNT(*), GROUP_CONCAT(DISTINCT instance_id) "
                        "FROM conversations WHERE chat_id=?", (chat_id,)
                    ).fetchone()
                    if probe and probe[0]:
                        log.error(
                            f"[get_history] chat_id={chat_id} tiene {probe[0]} mensajes guardados "
                            f"bajo instance_id={probe[1]!r}, pero esta llamada busca "
                            f"instance_id={_instance_id!r} — NO es un paciente nuevo, es un "
                            f"mismatch de INSTANCE_ID. Revisa el .env de esta instancia."
                        )
                except Exception:
                    pass
        
        history = []
        for r in reversed(rows):
            item = {"role": r["role"], "content": r["content"]}
            try:
                item["analysis"] = json.loads(r["analysis"] or "{}")
            except Exception:
                item["analysis"] = {}
            item["ts"] = r["ts"]
            history.append(item)
        return history
    
    # ─── Patient Operations ─────────────────────────────────────────────────────
    
    def get_or_create_patient(self, chat_id: str) -> Dict[str, Any]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM patients WHERE chat_id=?", (chat_id,)).fetchone()
            
            if row:
                c.execute("""
                    UPDATE patients 
                    SET visits=visits+1, last_seen=datetime('now')
                    WHERE chat_id=?
                """, (chat_id,))
                data = dict(row)
                data['is_new'] = False
                # Parse JSON
                for field in ['preferences', 'tags', 'services_used']:
                    try:
                        data[field] = json.loads(data.get(field, '{}') or '{}')
                    except Exception:
                        data[field] = {} if field == 'preferences' else []
                return data
            else:
                c.execute("INSERT INTO patients (chat_id) VALUES (?)", (chat_id,))
                return {
                    "chat_id": chat_id,
                    "is_new": True,
                    "visits": 0,
                    "name": "",
                    "preferences": {},
                    "tags": [],
                    "services_used": []
                }
    
    def update_patient(self, chat_id: str, **kwargs):
        if not kwargs:
            return
        for k, v in kwargs.items():
            if isinstance(v, (dict, list)):
                kwargs[k] = json.dumps(v, ensure_ascii=False)
        
        sets = ", ".join(f"{k}=?" for k in kwargs)
        with self._conn() as c:
            c.execute(f"UPDATE patients SET {sets} WHERE chat_id=?", 
                     list(kwargs.values()) + [chat_id])

    def remember_contact_route(self, chat_id: str, platform: str, channel_identity: Optional[str] = None):
        with self._conn() as c:
            c.execute("""
                INSERT INTO contact_routes (chat_id, platform, channel_identity, updated_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(chat_id) DO UPDATE SET
                    platform=excluded.platform,
                    channel_identity=excluded.channel_identity,
                    updated_at=datetime('now')
            """, (str(chat_id), str(platform), channel_identity or ""))

    def get_contact_route(self, chat_id: str) -> Optional[str]:
        with self._conn() as c:
            row = c.execute(
                "SELECT platform FROM contact_routes WHERE chat_id=?",
                (str(chat_id),),
            ).fetchone()
        return row["platform"] if row else None

    def get_contact_route_details(self, chat_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            row = c.execute(
                "SELECT platform, channel_identity FROM contact_routes WHERE chat_id=?",
                (str(chat_id),),
            ).fetchone()
        if row:
            return {"platform": row["platform"], "channel_identity": row["channel_identity"]}
        return None

    # ─── Memoria Permanente ─────────────────────────────────────────────────────
    # Esta memoria NUNCA se borra. Sobrevive crashes, resets, migraciones.
    # Es lo más importante que Firby sabe de esta clínica.

    def remember(self, key: str, value: str, category: str = "identity"):
        """Guarda algo en memoria permanente."""
        with self._conn() as c:
            c.execute("""
                INSERT INTO core_memory (key, value, category, updated_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    updated_at=datetime('now')
            """, (key, str(value), category))

    def recall(self, key: str) -> Optional[str]:
        """Recupera algo de memoria permanente."""
        with self._conn() as c:
            row = c.execute("SELECT value FROM core_memory WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    def recall_all(self, category: str = None) -> Dict[str, str]:
        """Recupera toda la memoria, opcionalmente filtrada por categoría."""
        with self._conn() as c:
            if category:
                rows = c.execute(
                    "SELECT key, value FROM core_memory WHERE category=? ORDER BY key",
                    (category,)).fetchall()
            else:
                rows = c.execute(
                    "SELECT key, value, category FROM core_memory ORDER BY category, key"
                ).fetchall()
        return {r["key"]: r["value"] for r in rows}

    def forget(self, key: str):
        """Borra un elemento de memoria permanente (usar con cuidado)."""
        with self._conn() as c:
            c.execute("DELETE FROM core_memory WHERE key=?", (key,))

    def get_core_memory_block(self) -> str:
        """
        Retorna un bloque de texto con la memoria permanente para inyectar al LLM.
        Solo lo más importante — identidad, clínica, aprendizajes clave.
        """
        memories = self.recall_all()
        if not memories:
            return ""
        lines = []
        for key, value in memories.items():
            lines.append(f"  {key}: {value}")
        return "MEMORIA PERMANENTE (nunca olvides esto):\n" + "\n".join(lines)

    def get_recent_patient_chats(self, limit: int = 10) -> List[Dict]:
        """Retorna los últimos N pacientes que han hablado con Firby."""
        with self._conn() as c:
            rows = c.execute("""
                SELECT c.chat_id,
                       p.name,
                       COUNT(c.id) as message_count,
                       MAX(c.ts) as last_message,
                       (SELECT content FROM conversations
                        WHERE chat_id=c.chat_id AND role='user'
                        ORDER BY ts DESC LIMIT 1) as last_user_msg
                FROM conversations c
                LEFT JOIN patients p ON p.chat_id = c.chat_id
                WHERE c.chat_id NOT IN (
                    SELECT chat_id FROM admins WHERE chat_id IS NOT NULL
                )
                AND c.chat_id != 'status@broadcast'
                AND c.chat_id NOT LIKE '%@newsletter'
                AND c.chat_id NOT LIKE 'owner-demo-%'
                AND c.chat_id NOT LIKE 'owner-debug%'
                AND c.chat_id NOT LIKE 'admin_probe%'
                AND c.chat_id NOT LIKE 'admin_control%'
                AND c.chat_id NOT LIKE 'prompt_probe%'
                AND c.chat_id NOT LIKE 'style_probe%'
                AND c.chat_id NOT LIKE 'wa_style_probe_%'
                AND c.chat_id NOT LIKE 'tone_probe_%'
                AND c.chat_id NOT LIKE 'fresh_greeting_fix_%'
                GROUP BY c.chat_id
                ORDER BY last_message DESC
                LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def get_patient_conversation(self, chat_id: str, limit: int = 30) -> List[Dict]:
        """Retorna la conversación completa de un paciente."""
        with self._conn() as c:
            rows = c.execute("""
                SELECT role, content, ts
                FROM conversations
                WHERE chat_id=?
                ORDER BY ts ASC
                LIMIT ?
            """, (chat_id, limit)).fetchall()
        return [dict(r) for r in rows]

    # ─── Feedback y Carpeta de Confianza ────────────────────────────────────────

    def save_feedback(self, patient_chat_id: str, feedback_text: str,
                      feedback_type: str, context: str, admin_chat_id: str) -> int:
        """Guarda feedback del admin sobre una conversación."""
        with self._conn() as c:
            cursor = c.execute("""
                INSERT INTO conversation_feedback
                (chat_id, feedback_text, feedback_type, context, created_by)
                VALUES (?,?,?,?,?)
            """, (patient_chat_id, feedback_text, feedback_type, context, admin_chat_id))
            return cursor.lastrowid

    def save_trust_rule(self, category: str, rule: str,
                        example_bad: str = "", example_good: str = "",
                        weight: float = 1.0) -> int:
        """Agrega una regla a la carpeta de confianza."""
        with self._conn() as c:
            cursor = c.execute("""
                INSERT INTO trust_folder (category, rule, example_bad, example_good, weight)
                VALUES (?,?,?,?,?)
            """, (category, rule, example_bad, example_good, weight))
            return cursor.lastrowid

    def get_trust_rules(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Recupera las reglas de comunicación aprendidas."""
        with self._conn() as c:
            if category:
                rows = c.execute("""
                    SELECT * FROM trust_folder WHERE category=?
                    ORDER BY weight DESC, times_applied DESC LIMIT ?
                """, (category, limit)).fetchall()
            else:
                rows = c.execute("""
                    SELECT * FROM trust_folder
                    ORDER BY weight DESC, times_applied DESC LIMIT ?
                """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def get_all_trust_rules(self) -> List[Dict]:
        """Todas las reglas para inyectar en el system prompt."""
        with self._conn() as c:
            rows = c.execute("""
                SELECT category, rule, example_bad, example_good
                FROM trust_folder
                ORDER BY weight DESC, times_applied DESC
                LIMIT 30
            """).fetchall()
        return [dict(r) for r in rows]

    def increment_rule_usage(self, rule_id: int):
        with self._conn() as c:
            c.execute("UPDATE trust_folder SET times_applied=times_applied+1 WHERE id=?",
                      (rule_id,))

    def save_behavior_playbook(self, trigger_text: str, response_example: str,
                               category: str = "general", instruction: str = "",
                               bubble_count: int = 1, weight: float = 1.0) -> int:
        """Guarda un playbook aprendido del dueño."""
        with self._conn() as c:
            cursor = c.execute("""
                INSERT INTO behavior_playbooks
                (category, trigger_text, instruction, response_example, bubble_count, weight)
                VALUES (?,?,?,?,?,?)
            """, (
                category,
                trigger_text,
                instruction,
                response_example,
                max(1, int(bubble_count or 1)),
                float(weight or 1.0),
            ))
            return cursor.lastrowid

    def get_behavior_playbooks(self, category: str = None, limit: int = 12) -> List[Dict]:
        """Retorna playbooks aprendidos ordenados por prioridad."""
        with self._conn() as c:
            if category:
                rows = c.execute("""
                    SELECT * FROM behavior_playbooks
                    WHERE category=?
                    ORDER BY weight DESC, times_used DESC, id DESC
                    LIMIT ?
                """, (category, limit)).fetchall()
            else:
                rows = c.execute("""
                    SELECT * FROM behavior_playbooks
                    ORDER BY weight DESC, times_used DESC, id DESC
                    LIMIT ?
                """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def delete_trust_rule(self, rule_id: int):
        with self._conn() as c:
            c.execute("DELETE FROM trust_folder WHERE id=?", (rule_id,))

    def get_feedback_list(self, limit: int = 10) -> List[Dict]:
        """Últimos feedbacks del admin."""
        with self._conn() as c:
            rows = c.execute("""
                SELECT cf.*, p.name as patient_name
                FROM conversation_feedback cf
                LEFT JOIN patients p ON p.chat_id = cf.chat_id
                ORDER BY cf.created_at DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]
    
    # ─── Appointment Operations ─────────────────────────────────────────────────
    
    def save_appointment(self, chat_id: str, data: Dict) -> int:
        with self._conn() as c:
            cursor = c.execute("""
                INSERT INTO appointments
                (chat_id, patient_name, patient_phone, patient_email,
                 service, datetime_slot, duration_minutes, notes)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                chat_id,
                data.get("patient_name", ""),
                data.get("patient_phone", ""),
                data.get("patient_email", ""),
                data.get("service", ""),
                data.get("datetime_slot", ""),
                data.get("duration_minutes", 60),
                data.get("notes", "")
            ))
            return cursor.lastrowid
    
    def get_appointments(self, chat_id: str = None, status: str = None, 
                        limit: int = 50) -> List[Dict]:
        query = "SELECT * FROM appointments WHERE 1=1"
        params = []
        
        if chat_id:
            query += " AND chat_id=?"
            params.append(chat_id)
        if status:
            query += " AND status=?"
            params.append(status)
        
        query += " ORDER BY datetime_slot DESC LIMIT ?"
        params.append(limit)
        
        with self._conn() as c:
            rows = c.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    
    def update_appointment(self, apt_id: int, **kwargs):
        if not kwargs:
            return
        kwargs['updated_at'] = datetime.now().isoformat()
        sets = ", ".join(f"{k}=?" for k in kwargs)
        with self._conn() as c:
            c.execute(f"UPDATE appointments SET {sets} WHERE id=?",
                     list(kwargs.values()) + [apt_id])
    
    # ─── Conversation State ─────────────────────────────────────────────────────
    
    def get_conversation_state(self, chat_id: str) -> ConversationState:
        with self._conn() as c:
            row = c.execute(
                "SELECT state FROM conversation_states WHERE chat_id=?",
                (chat_id,)
            ).fetchone()
        
        if row:
            data = json.loads(row["state"])
            return ConversationState(
                chat_id=chat_id,
                phase=data.get("phase", "greeting"),
                collected_data=data.get("collected_data", {}),
                pending_questions=data.get("pending_questions", []),
                last_intent=IntentType[data["last_intent"]] if data.get("last_intent") else None,
                turn_count=data.get("turn_count", 0),
                satisfaction_score=data.get("satisfaction_score", 0.5),
                escalation_needed=data.get("escalation_needed", False),
                notes=data.get("notes", [])
            )
        
        return ConversationState(
            chat_id=chat_id,
            phase="greeting",
            collected_data={},
            pending_questions=[],
            last_intent=None,
            turn_count=0,
            satisfaction_score=0.5,
            escalation_needed=False,
            notes=[]
        )
    
    def save_conversation_state(self, state: ConversationState):
        data = {
            "phase": state.phase,
            "collected_data": state.collected_data,
            "pending_questions": state.pending_questions,
            "last_intent": state.last_intent.name if state.last_intent else None,
            "turn_count": state.turn_count,
            "satisfaction_score": state.satisfaction_score,
            "escalation_needed": state.escalation_needed,
            "notes": state.notes
        }
        
        with self._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO conversation_states (chat_id, state, updated_at)
                VALUES (?, ?, datetime('now'))
            """, (state.chat_id, json.dumps(data, ensure_ascii=False)))
    
    # ─── Memory Operations ──────────────────────────────────────────────────────
    
    def save_memory(self, memory: MemoryItem):
        embedding_blob = None
        if memory.embedding:
            # Serialize embedding as binary
            import struct
            embedding_blob = struct.pack(f'{len(memory.embedding)}f', *memory.embedding)
        
        with self._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO memories
                (id, chat_id, content, embedding, category, importance, 
                 accessed_count, created_at, last_accessed, metadata)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                memory.id,
                memory.chat_id,
                memory.content,
                embedding_blob,
                memory.category,
                memory.importance,
                memory.accessed_count,
                memory.created_at.isoformat(),
                memory.last_accessed.isoformat(),
                json.dumps(memory.metadata, ensure_ascii=False)
            ))
    
    def search_memories(self, chat_id: str, category: str = None, 
                       limit: int = 10) -> List[MemoryItem]:
        query = "SELECT * FROM memories WHERE chat_id=?"
        params = [chat_id]
        
        if category:
            query += " AND category=?"
            params.append(category)
        
        query += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
        params.append(limit)
        
        with self._conn() as c:
            rows = c.execute(query, params).fetchall()
        
        memories = []
        for r in rows:
            embedding = None
            if r["embedding"]:
                import struct
                n = len(r["embedding"]) // 4
                embedding = list(struct.unpack(f'{n}f', r["embedding"]))
            
            memories.append(MemoryItem(
                id=r["id"],
                chat_id=r["chat_id"],
                content=r["content"],
                embedding=embedding,
                category=r["category"],
                importance=r["importance"],
                created_at=datetime.fromisoformat(r["created_at"]),
                accessed_count=r["accessed_count"],
                last_accessed=datetime.fromisoformat(r["last_accessed"]),
                metadata=json.loads(r["metadata"] or "{}")
            ))
        
        return memories
    
    # ─── Task Operations ────────────────────────────────────────────────────────
    
    def create_task(self, task: Task):
        with self._conn() as c:
            c.execute("""
                INSERT INTO tasks
                (id, type, priority, status, data, scheduled_for, created_at)
                VALUES (?,?,?,?,?,?,?)
            """, (
                task.id,
                task.type,
                task.priority,
                task.status,
                json.dumps(task.data, ensure_ascii=False),
                task.scheduled_for.isoformat() if task.scheduled_for else None,
                task.created_at.isoformat()
            ))
    
    def get_pending_tasks(self, limit: int = 20) -> List[Task]:
        with self._conn() as c:
            rows = c.execute("""
                SELECT * FROM tasks 
                WHERE status IN ('pending', 'running')
                AND (scheduled_for IS NULL OR scheduled_for <= datetime('now'))
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            """, (limit,)).fetchall()
        
        return [Task(
            id=r["id"],
            type=r["type"],
            priority=r["priority"],
            status=r["status"],
            data=json.loads(r["data"] or "{}"),
            created_at=datetime.fromisoformat(r["created_at"]),
            scheduled_for=datetime.fromisoformat(r["scheduled_for"]) if r["scheduled_for"] else None,
            completed_at=datetime.fromisoformat(r["completed_at"]) if r["completed_at"] else None,
            result=json.loads(r["result"]) if r["result"] else None,
            retries=r["retries"]
        ) for r in rows]
    
    def update_task(self, task_id: str, **kwargs):
        if not kwargs:
            return
        for k, v in kwargs.items():
            if isinstance(v, (dict, list)):
                kwargs[k] = json.dumps(v, ensure_ascii=False)
            elif isinstance(v, datetime):
                kwargs[k] = v.isoformat()
        
        sets = ", ".join(f"{k}=?" for k in kwargs)
        with self._conn() as c:
            c.execute(f"UPDATE tasks SET {sets} WHERE id=?",
                     list(kwargs.values()) + [task_id])
    
    # ─── MCP Plugin Operations ──────────────────────────────────────────────────
    
    def get_plugins(self, enabled_only: bool = False) -> List[MCPPlugin]:
        query = "SELECT * FROM mcp_plugins"
        if enabled_only:
            query += " WHERE enabled=1"
        
        with self._conn() as c:
            rows = c.execute(query).fetchall()
        
        return [MCPPlugin(
            id=r["id"],
            name=r["name"],
            description=r["description"],
            version=r["version"],
            enabled=bool(r["enabled"]),
            config=json.loads(r["config"] or "{}"),
            capabilities=json.loads(r["capabilities"] or "[]"),
            endpoints=json.loads(r["endpoints"] or "{}"),
            health_status=r["health_status"],
            last_check=datetime.fromisoformat(r["last_check"]) if r["last_check"] else datetime.now()
        ) for r in rows]
    
    def install_plugin(self, plugin: MCPPlugin):
        with self._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO mcp_plugins
                (id, name, description, version, enabled, config, 
                 capabilities, endpoints, health_status, last_check)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                plugin.id,
                plugin.name,
                plugin.description,
                plugin.version,
                int(plugin.enabled),
                json.dumps(plugin.config, ensure_ascii=False),
                json.dumps(plugin.capabilities, ensure_ascii=False),
                json.dumps(plugin.endpoints, ensure_ascii=False),
                plugin.health_status,
                plugin.last_check.isoformat()
            ))
    
    # ─── Linked Channel Operations (V10 Omnicanal) ──────────────────────────────
    
    def get_linked_channels(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        query = "SELECT * FROM linked_channels"
        if enabled_only:
            query += " WHERE is_active=1"
        with self._conn() as c:
            rows = c.execute(query).fetchall()
        
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["config_json"] = json.loads(d["config_json"] or "{}")
            except Exception:
                d["config_json"] = {}
            results.append(d)
        return results

    def add_linked_channel(self, platform: str, channel_identity: str, config_json: Dict[str, Any] = None) -> int:
        config_str = json.dumps(config_json or {}, ensure_ascii=False)
        with self._conn() as c:
            cursor = c.execute("""
                INSERT INTO linked_channels (platform, channel_identity, config_json, is_active)
                VALUES (?, ?, ?, 1)
            """, (platform, channel_identity, config_str))
            return cursor.lastrowid

    def update_linked_channel(self, channel_id: int, is_active: Optional[bool] = None, config_json: Optional[Dict[str, Any]] = None):
        updates = []
        params = []
        if is_active is not None:
            updates.append("is_active=?")
            params.append(int(is_active))
        if config_json is not None:
            updates.append("config_json=?")
            params.append(json.dumps(config_json, ensure_ascii=False))
        
        if not updates:
            return
        
        updates.append("updated_at=datetime('now')")
        query = f"UPDATE linked_channels SET {', '.join(updates)} WHERE id=?"
        params.append(channel_id)
        
        with self._conn() as c:
            c.execute(query, params)

    def remove_linked_channel(self, channel_id: int):
        with self._conn() as c:
            c.execute("DELETE FROM linked_channels WHERE id=?", (channel_id,))
    
    # ─── Metrics Operations ─────────────────────────────────────────────────────
    
    def record_metric(self, metric_type: str, metric_name: str, 
                     value: float, dimensions: Dict = None):
        with self._conn() as c:
            c.execute("""
                INSERT INTO metrics (metric_type, metric_name, metric_value, dimensions)
                VALUES (?,?,?,?)
            """, (metric_type, metric_name, value, 
                  json.dumps(dimensions or {}, ensure_ascii=False)))
    
    def get_metrics(self, metric_type: str = None, since: datetime = None,
                   limit: int = 1000) -> List[Dict]:
        query = "SELECT * FROM metrics WHERE 1=1"
        params = []
        
        if metric_type:
            query += " AND metric_type=?"
            params.append(metric_type)
        if since:
            query += " AND ts >= ?"
            params.append(since.isoformat())
        
        query += " ORDER BY ts DESC LIMIT ?"
        params.append(limit)
        
        with self._conn() as c:
            rows = c.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    
    # ─── Learned Optimizations ──────────────────────────────────────────────────
    
    def save_optimization(self, category: str, trigger: str, 
                         optimization: str, success_rate: float = 0):
        with self._conn() as c:
            c.execute("""
                INSERT INTO learned_optimizations
                (category, trigger_pattern, optimization, success_rate)
                VALUES (?,?,?,?)
            """, (category, trigger, optimization, success_rate))
    
    def get_optimizations(self, category: str = None) -> List[Dict]:
        query = "SELECT * FROM learned_optimizations WHERE success_rate > 0.5"
        params = []
        
        if category:
            query += " AND category=?"
            params.append(category)
        
        query += " ORDER BY success_rate DESC, usage_count DESC"
        
        with self._conn() as c:
            rows = c.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    
    # ─── Self Improvement Log ───────────────────────────────────────────────────
    
    def log_improvement(self, improvement_type: str, description: str,
                       before: Dict, after: Dict, impact: float, applied: bool):
        with self._conn() as c:
            c.execute("""
                INSERT INTO self_improvement_log
                (improvement_type, description, before_state, after_state, 
                 impact_score, applied)
                VALUES (?,?,?,?,?,?)
            """, (
                improvement_type,
                description,
                json.dumps(before, ensure_ascii=False),
                json.dumps(after, ensure_ascii=False),
                impact,
                int(applied)
            ))
    
    # ─── Response Cache ─────────────────────────────────────────────────────────
    
    def cache_response(self, query_hash: str, response: str, ttl: int = 3600):
        with self._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO response_cache
                (hash, response, hit_count, last_hit, ttl_seconds)
                VALUES (?,?,1,datetime('now'),?)
            """, (query_hash, response, ttl))
    
    def get_cached_response(self, query_hash: str) -> Optional[str]:
        with self._conn() as c:
            row = c.execute("""
                SELECT response, created_at, ttl_seconds 
                FROM response_cache 
                WHERE hash=?
            """, (query_hash,)).fetchone()
            
            if row:
                created = datetime.fromisoformat(row["created_at"])
                if datetime.now() - created < timedelta(seconds=row["ttl_seconds"]):
                    c.execute("""
                        UPDATE response_cache 
                        SET hit_count=hit_count+1, last_hit=datetime('now')
                        WHERE hash=?
                    """, (query_hash,))
                    return row["response"]
        return None

    # ─── Auth Operations ─────────────────────────────────────────────────────────

    def create_activation_token(self, token: str, clinic_label: str,
                                 expires_at: str) -> bool:
        """Crea un token de activacion (lo genera Santiago) y lo replica en todas las DBs."""
        local_saved = False
        try:
            with self._conn() as c:
                c.execute("""
                    INSERT INTO activation_tokens
                    (token, clinic_label, expires_at)
                    VALUES (?, ?, ?)
                """, (token, clinic_label, expires_at))
            local_saved = True
        except Exception as e:
            log.error(f"Error local saving token: {e}")

        # Replicar en otras DBs conocidas para que el login central lo encuentre
        db_paths = [
            "/home/ubuntu/firby/firby.db",
            "/home/ubuntu/firby/instances/clinica-de-las-americas/firby.db",
            "/home/ubuntu/firby/agents/ovni/firby.db"
        ]
        for p in db_paths:
            if os.path.exists(p) and os.path.abspath(self.db_path) != os.path.abspath(p):
                try:
                    import sqlite3
                    with sqlite3.connect(p) as conn:
                        conn.execute("""
                            CREATE TABLE IF NOT EXISTS activation_tokens (
                                token TEXT PRIMARY KEY,
                                clinic_label TEXT NOT NULL,
                                expires_at TEXT NOT NULL,
                                used_at TEXT,
                                used_by_chat_id TEXT,
                                is_active INTEGER DEFAULT 1,
                                created_at TEXT DEFAULT (datetime('now'))
                            )
                        """)
                        conn.execute("""
                            INSERT OR REPLACE INTO activation_tokens
                            (token, clinic_label, expires_at)
                            VALUES (?, ?, ?)
                        """, (token, clinic_label, expires_at))
                except Exception as e:
                    log.error(f"Error replicating token to {p}: {e}")
        return local_saved

    def get_activation_token(self, token: str) -> Optional[Dict]:
        """Lee un token de la DB local o realiza fallback en las otras DBs."""
        token_upper = str(token).strip().upper()
        row = None
        # 1. Buscar localmente
        try:
            with self._conn() as c:
                row = c.execute(
                    "SELECT * FROM activation_tokens WHERE UPPER(token)=?", (token_upper,)
                ).fetchone()
        except Exception:
            pass

        # 2. Fallback a otras DBs
        if not row:
            db_paths = [
                "/home/ubuntu/firby/firby.db",
                "/home/ubuntu/firby/instances/clinica-de-las-americas/firby.db",
                "/home/ubuntu/firby/agents/ovni/firby.db"
            ]
            for p in db_paths:
                if os.path.exists(p) and os.path.abspath(self.db_path) != os.path.abspath(p):
                    try:
                        import sqlite3
                        with sqlite3.connect(p) as conn:
                            conn.row_factory = sqlite3.Row
                            row = conn.execute(
                                "SELECT * FROM activation_tokens WHERE UPPER(token)=?", (token_upper,)
                            ).fetchone()
                            if row:
                                break
                    except Exception:
                        pass

        if not row:
            return None
        data = dict(row)
        # Verificar expiracion
        try:
            exp = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > exp:
                return None
        except Exception:
            return None
        # Verificar si ya fue usado
        if data.get("used_at") and data.get("is_active") == 0:
            return None
        return data

    def consume_activation_token(self, token: str, chat_id: str):
        """Marca el token como usado en todas las DBs."""
        # 1. Consumir localmente
        try:
            with self._conn() as c:
                c.execute("""
                    UPDATE activation_tokens
                    SET used_at=datetime('now'), used_by_chat_id=?, is_active=0
                    WHERE token=?
                """, (chat_id, token))
        except Exception as e:
            log.error(f"Error local consuming token: {e}")

        # 2. Consumir en las demás DBs del sistema
        db_paths = [
            "/home/ubuntu/firby/firby.db",
            "/home/ubuntu/firby/instances/clinica-de-las-americas/firby.db",
            "/home/ubuntu/firby/agents/ovni/firby.db"
        ]
        for p in db_paths:
            if os.path.exists(p) and os.path.abspath(self.db_path) != os.path.abspath(p):
                try:
                    import sqlite3
                    with sqlite3.connect(p) as conn:
                        conn.execute("""
                            UPDATE activation_tokens
                            SET used_at=datetime('now'), used_by_chat_id=?, is_active=0
                            WHERE token=?
                        """, (chat_id, token))
                except Exception as e:
                    log.error(f"Error syncing consumed token to {p}: {e}")

    def create_admin(self, chat_id: str, email: str, password_hash: str,
                     name: str, role: str = "admin",
                     token: str = "", invited_by: str = "") -> bool:
        """Registra un nuevo admin."""
        try:
            with self._conn() as c:
                c.execute("""
                    INSERT OR REPLACE INTO admins
                    (chat_id, email, password_hash, name, role,
                     activated_by_token, invited_by_chat_id, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (chat_id, email.lower(), password_hash, name,
                      role, token, invited_by))
            return True
        except Exception as e:
            log.warning(f"create_admin error: {e}")
            return False

    def get_admin(self, chat_id: str) -> Optional[Dict]:
        """Obtiene admin por chat_id."""
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM admins WHERE chat_id=? AND is_active=1",
                (chat_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_admin_by_email(self, email: str) -> Optional[Dict]:
        """Obtiene admin por email."""
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM admins WHERE email=? AND is_active=1",
                (email.lower(),)
            ).fetchone()
        return dict(row) if row else None

    def list_admins(self) -> List[Dict]:
        """Lista todos los admins activos."""
        with self._conn() as c:
            rows = c.execute(
                "SELECT id,chat_id,email,name,role,created_at FROM admins WHERE is_active=1"
            ).fetchall()
        return [dict(r) for r in rows]

    def update_admin_login(self, chat_id: str):
        """Actualiza ultimo login y resetea intentos fallidos."""
        with self._conn() as c:
            c.execute("""
                UPDATE admins SET last_login=datetime('now'), login_attempts=0
                WHERE chat_id=?
            """, (chat_id,))

    def increment_login_attempts(self, chat_id: str):
        with self._conn() as c:
            c.execute("""
                UPDATE admins SET login_attempts=login_attempts+1 WHERE chat_id=?
            """, (chat_id,))

    def deactivate_admin(self, chat_id: str):
        with self._conn() as c:
            c.execute("UPDATE admins SET is_active=0 WHERE chat_id=?", (chat_id,))

    def get_owner(self) -> Optional[Dict]:
        """Obtiene el owner (primer admin con role=owner)."""
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM admins WHERE role='owner' AND is_active=1 LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    # ─── Auth Session (flujo pendiente) ─────────────────────────────────────────

    def get_auth_session(self, chat_id: str) -> Optional[Dict]:
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM auth_sessions WHERE chat_id=?", (chat_id,)
            ).fetchone()
        if not row:
            return None
        data = dict(row)
        try:
            data["temp_data"] = json.loads(data.get("temp_data") or "{}")
        except Exception:
            data["temp_data"] = {}
        return data

    def set_auth_session(self, chat_id: str, flow: str, step: str,
                         temp_data: Dict = None, attempts: int = 0):
        with self._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO auth_sessions
                (chat_id, flow, step, temp_data, attempts, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (chat_id, flow, step,
                  json.dumps(temp_data or {}, ensure_ascii=False), attempts))

    def clear_auth_session(self, chat_id: str):
        with self._conn() as c:
            c.execute("DELETE FROM auth_sessions WHERE chat_id=?", (chat_id,))

    def log_auth_event(
        self,
        email: str,
        provider: str,
        action: str,
        status: str = "success",
        name: str = "",
        ip_address: str = "",
        user_agent: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Registra un evento de autenticacion (Google, email/pass, token, etc.)."""
        try:
            with self._conn() as c:
                cur = c.execute("""
                    INSERT INTO auth_logs (email, provider, action, status, name, ip_address, user_agent, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (
                    (email or "").strip().lower(),
                    (provider or "unknown").strip().lower(),
                    (action or "login").strip().lower(),
                    (status or "success").strip().lower(),
                    (name or "").strip(),
                    (ip_address or "").strip(),
                    (user_agent or "").strip(),
                    json.dumps(details or {}, ensure_ascii=False)
                ))
                return cur.lastrowid or 1
        except Exception as e:
            log.warning(f"[log_auth_event] Error registrando auditoria de auth: {e}")
            return 0

    def get_auth_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        email: Optional[str] = None,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de autenticacion con filtros opcionales."""
        try:
            query = "SELECT * FROM auth_logs WHERE 1=1"
            params = []
            if email:
                query += " AND LOWER(email) = ?"
                params.append(email.strip().lower())
            if provider:
                query += " AND LOWER(provider) = ?"
                params.append(provider.strip().lower())
            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            with self._conn() as c:
                rows = c.execute(query, params).fetchall()
                result = []
                for r in rows:
                    d = dict(r)
                    try:
                        d["details"] = json.loads(d.get("details", "{}") or "{}")
                    except Exception:
                        d["details"] = {}
                    result.append(d)
                return result
        except Exception as e:
            log.warning(f"[get_auth_logs] Error consultando logs de auth: {e}")
            return []

    def store_verification_code(
        self,
        email: str,
        code_hash: str,
        salt: str,
        purpose: str,
        expires_at: str,
        ip_address: str = "",
        user_agent: str = ""
    ) -> int:
        """Almacena un nuevo código OTP con hash, salt y expiración."""
        try:
            with self._conn() as c:
                cur = c.execute("""
                    INSERT INTO email_verification_codes (email, code_hash, salt, purpose, expires_at, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    email.strip().lower(),
                    code_hash,
                    salt,
                    purpose.strip().lower(),
                    expires_at,
                    ip_address.strip(),
                    user_agent.strip()
                ))
                return cur.lastrowid or 1
        except Exception as e:
            log.warning(f"[store_verification_code] Error guardando código OTP: {e}")
            return 0

    def get_latest_verification_code(
        self,
        email: str,
        purpose: str = "verification"
    ) -> Optional[Dict[str, Any]]:
        """Obtiene el último código de verificación emitido no utilizado para un correo."""
        try:
            with self._conn() as c:
                row = c.execute("""
                    SELECT * FROM email_verification_codes
                    WHERE email = ? AND purpose = ? AND verified = 0
                    ORDER BY id DESC LIMIT 1
                """, (email.strip().lower(), purpose.strip().lower())).fetchone()
                return dict(row) if row else None
        except Exception as e:
            log.warning(f"[get_latest_verification_code] Error buscando código: {e}")
            return None

    def increment_verification_attempts(self, code_id: int) -> int:
        """Incrementa el contador de intentos fallidos de validación."""
        try:
            with self._conn() as c:
                c.execute("""
                    UPDATE email_verification_codes
                    SET attempts = attempts + 1
                    WHERE id = ?
                """, (code_id,))
                row = c.execute("SELECT attempts FROM email_verification_codes WHERE id = ?", (code_id,)).fetchone()
                return row["attempts"] if row else 1
        except Exception as e:
            log.warning(f"[increment_verification_attempts] Error: {e}")
            return 1

    def mark_verification_code_used(self, code_id: int) -> bool:
        """Marca un código como verificado/consumido para evitar reuso."""
        try:
            with self._conn() as c:
                c.execute("""
                    UPDATE email_verification_codes
                    SET verified = 1
                    WHERE id = ?
                """, (code_id,))
                return True
        except Exception as e:
            log.warning(f"[mark_verification_code_used] Error: {e}")
            return False

    def count_recent_verification_requests(self, email: str, minutes: int = 60) -> int:
        """Cuenta cuántas solicitudes de código ha hecho un email en una ventana de minutos."""
        try:
            with self._conn() as c:
                row = c.execute("""
                    SELECT COUNT(*) as count FROM email_verification_codes
                    WHERE email = ? AND created_at >= datetime('now', 'localtime', '-' || ? || ' minutes')
                """, (email.strip().lower(), minutes)).fetchone()
                return row["count"] if row else 0
        except Exception as e:
            log.warning(f"[count_recent_verification_requests] Error: {e}")
            return 0

    def count_recent_ip_verification_requests(self, ip_address: str, minutes: int = 10) -> int:
        """Cuenta solicitudes de código desde una misma IP en una ventana de minutos."""
        if not ip_address:
            return 0
        try:
            with self._conn() as c:
                row = c.execute("""
                    SELECT COUNT(*) as count FROM email_verification_codes
                    WHERE ip_address = ? AND created_at >= datetime('now', 'localtime', '-' || ? || ' minutes')
                """, (ip_address.strip(), minutes)).fetchone()
                return row["count"] if row else 0
        except Exception as e:
            log.warning(f"[count_recent_ip_verification_requests] Error: {e}")
            return 0


# Instancia global
db: DatabaseManager = None
kb: "KnowledgeBase" = None

def init_database():
    import src.core.globals as g
    global db, kb
    db = DatabaseManager(Config.DB_PATH, Config.VECTOR_DB_PATH)
    g.db = db
    if _KB_AVAILABLE:
        kb = KnowledgeBase(Config.DB_PATH)
        g.kb = kb
        log.info("[kb] KnowledgeBase inicializada")

