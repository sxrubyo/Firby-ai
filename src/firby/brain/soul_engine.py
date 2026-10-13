"""
Firby Soul & Identity Engine (Arquitectura OpenClaw / Hermes).
Garantiza que la identidad del dueño, de la clínica y de la recepcionista de IA
queden grabadas permanentemente en SOUL.md, IDENTITY.md, USER.md, MEMORY.md y soul.json
en el disco de la instancia y en el workspace global para que NUNCA se olviden.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

log = logging.getLogger("firby.soul")

class SoulEngine:
    """Gestor maestro de identidad y alma estilo OpenClaw / Hermes."""

    @staticmethod
    def get_instance_dir(instance_id: Optional[str] = None) -> Path:
        if instance_id:
            inst_dir = Path(f"/home/ubuntu/firby/instances/{instance_id}")
            if inst_dir.exists():
                return inst_dir
            if Path(instance_id).is_dir():
                return Path(instance_id)
        env_slug = os.getenv("INSTANCE_ID")
        if env_slug:
            inst_dir = Path(f"/home/ubuntu/firby/instances/{env_slug}")
            if inst_dir.exists():
                return inst_dir
        cwd = Path.cwd()
        if (cwd / "src").exists() or (cwd / ".env").exists() or (cwd / "firby.db").exists():
            return cwd
        return Path("/home/ubuntu/firby")

    @classmethod
    def sync_soul(cls, instance_id: Optional[str] = None,
                  owner_data: Optional[Dict] = None,
                  clinic_data: Optional[Dict] = None,
                  assistant_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Sincroniza y escribe SOUL.md, IDENTITY.md, USER.md, MEMORY.md y soul.json.
        """
        inst_dir = cls.get_instance_dir(instance_id)
        is_americas = "clinica-de-las-americas" in str(inst_dir)

        owner_full = ""
        owner_first = ""
        owner_email = ""
        owner_chat_id = ""
        
        clinic_name = ""
        clinic_phone = ""
        clinic_address = ""
        clinic_website = ""
        clinic_services = []
        clinic_schedule = ""
        receptionist_name = assistant_name or ""

        try:
            from src.core.globals import db
            if db:
                c_row = db.get_clinic() if hasattr(db, "get_clinic") else {}
                if c_row:
                    clinic_name = c_row.get("name", "")
                    clinic_phone = c_row.get("phone", "")
                    clinic_address = c_row.get("address", "")
                    clinic_website = c_row.get("website", "")
                    c_svcs = c_row.get("services", [])
                    if isinstance(c_svcs, str):
                        try: clinic_services = json.loads(c_svcs)
                        except Exception: clinic_services = []
                    elif isinstance(c_svcs, list):
                        clinic_services = c_svcs
                    
                    c_sch = c_row.get("schedule", {})
                    if isinstance(c_sch, str):
                        try: c_sch = json.loads(c_sch)
                        except Exception: c_sch = {}
                    if isinstance(c_sch, dict):
                        clinic_schedule = c_sch.get("texto") or str(c_sch)
                    
                    if not receptionist_name:
                        receptionist_name = c_row.get("assistant_name") or c_row.get("agent_name") or "Firby"

                with db._conn() as conn:
                    admin_row = conn.execute("SELECT * FROM admins WHERE role='owner' OR is_active=1 ORDER BY id ASC LIMIT 1").fetchone()
                    if admin_row:
                        owner_full = admin_row["name"] or ""
                        owner_email = admin_row["email"] or ""
                        owner_chat_id = admin_row["chat_id"] or ""
                        owner_first = owner_full.split()[0].title() if owner_full else ""
        except Exception as e:
            log.warning(f"[soul_engine] error reading DB: {e}")

        if owner_data:
            if owner_data.get("name"):
                owner_full = owner_data["name"]
                owner_first = owner_full.split()[0].title()
            if owner_data.get("email"):
                owner_email = owner_data["email"]
            if owner_data.get("chat_id"):
                owner_chat_id = owner_data["chat_id"]
        
        if clinic_data:
            if clinic_data.get("name"):
                clinic_name = clinic_data["name"]
            if clinic_data.get("phone"):
                clinic_phone = clinic_data["phone"]
            if clinic_data.get("address"):
                clinic_address = clinic_data["address"]
            if clinic_data.get("website"):
                clinic_website = clinic_data["website"]
            if clinic_data.get("services"):
                clinic_services = clinic_data["services"]
            if clinic_data.get("schedule_text"):
                clinic_schedule = clinic_data["schedule_text"]

        if not owner_first and owner_full:
            owner_first = owner_full.split()[0].title()
        if not owner_first:
            owner_first = "Santiago" if is_americas else "Administrador"
        if not owner_full:
            owner_full = "Santiago Rubio Parra" if is_americas else owner_first
        if not owner_email:
            owner_email = ""
        if not clinic_name:
            clinic_name = "Clínica Las Américas Auna" if is_americas else "Tu Negocio"
        if not receptionist_name:
            receptionist_name = "Firby"

        default_addr = "Diagonal 75 B # 2 A 80/140, Belén La Mota, Medellín" if is_americas else ""
        default_tel = "(604) 322 7900" if is_americas else ""
        default_web = "http://clinicalasamericas.lasamericas.com.co/" if is_americas else ""

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        soul_payload = {
            "version": "2.0-openclaw-hermes",
            "last_synced": now_str,
            "owner": {
                "first_name": owner_first,
                "full_name": owner_full,
                "email": owner_email,
                "chat_id": owner_chat_id,
                "role": "Dueño y Administrador Principal"
            },
            "business": {
                "name": clinic_name,
                "city": "Medellín, Colombia",
                "address": clinic_address or default_addr,
                "phone": clinic_phone or default_tel,
                "website": clinic_website or default_web,
                "services": clinic_services,
                "schedule": clinic_schedule or "Horario comercial"
            },
            "assistant": {
                "name": receptionist_name,
                "role": f"Socia de IA y Recepcionista Virtual de {clinic_name}",
                "model_engine": "Firby Ultra 9.6"
            }
        }

        # ── 1. IDENTITY.md (OpenClaw Standard) ──────────────────────────────
        identity_md = f"""# IDENTITY
- Name: {receptionist_name}
- Role: Socia de IA y Recepcionista Ejecutiva
- Business: {clinic_name}
- Owner: {owner_full} ({owner_first})
- Location: {soul_payload['business']['city']}
- Contact: {soul_payload['business']['phone']}
- Website: {soul_payload['business']['website']}
"""

        # ── 2. USER.md (OpenClaw Standard) ──────────────────────────────────
        user_md = f"""# USER PROFILE
- First Name: {owner_first}
- Full Name: {owner_full}
- Email: {owner_email}
- Role: Dueño y Administrador de {clinic_name}
- WhatsApp ID: {owner_chat_id}
- Instructions: Tratar siempre como {owner_first}, con respeto ejecutivo, calidez y memoria perfecta de su identidad y negocio.
"""

        # ── 3. SOUL.md (OpenClaw Standard) ──────────────────────────────────
        soul_md = f"""<!-- AUTO-GENERATED: firby-soul-sync | {now_str} -->
# SOUL
Eres {receptionist_name}, la socia de IA de {owner_first} para {clinic_name} en {soul_payload['business']['city']}.
Tu misión es gestionar la atención en WhatsApp con proactividad, inteligencia y calidez humana.

## LEYES DE MEMORIA INVIOLABLES:
1. Tu dueño es **{owner_first}** ({owner_full}). Si él te pregunta quién es o cómo se llama, dile de inmediato: "Claro que sí, te llamas {owner_first}!".
2. Jamás uses frases de call center pasivas como "cómo te puedo ayudar hoy" ni "en qué puedo servirle".
3. Eres proactiva: cuando {owner_first} te salude, dale un mini reporte del negocio y proponle acciones útiles.
4. Cero signos '¿' ni '¡'. Español latinoamericano natural y cálido.
"""

        # ── 4. MEMORY.md (Hermes Standard) ──────────────────────────────────
        memory_md = f"""# MEMORY & KNOWLEDGE BASE
- Negocio: {clinic_name}
- Dirección: {soul_payload['business']['address']}
- Teléfono: {soul_payload['business']['phone']}
- Web: {soul_payload['business']['website']}
- Horario: {soul_payload['business']['schedule']}
- Servicios: {", ".join(clinic_services) if clinic_services else 'Servicios médicos/especializados'}
"""

        # ── 5. Escribir en las ubicaciones correspondientes ─────────────────
        target_dirs = [
            inst_dir,
            inst_dir / "soul",
            inst_dir / "identity",
        ]

        if inst_dir == Path("/home/ubuntu/firby"):
            target_dirs.extend([
                Path("/home/ubuntu/.openclaw/workspace"),
                Path("/home/ubuntu/firby/soul"),
                Path("/home/ubuntu/firby/identity"),
            ])

        for d in target_dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        files_to_write = [
            # Instancia local
            (inst_dir / "IDENTITY.md", identity_md),
            (inst_dir / "USER.md", user_md),
            (inst_dir / "SOUL.md", soul_md),
            (inst_dir / "MEMORY.md", memory_md),
            (inst_dir / "soul.json", json.dumps(soul_payload, indent=2, ensure_ascii=False)),
            (inst_dir / "soul" / "SOUL.md", soul_md),
            (inst_dir / "identity" / "IDENTITY.md", identity_md),
        ]

        if inst_dir == Path("/home/ubuntu/firby"):
            files_to_write.extend([
                # Workspace OpenClaw
                (Path("/home/ubuntu/.openclaw/workspace/IDENTITY.md"), identity_md),
                (Path("/home/ubuntu/.openclaw/workspace/USER.md"), user_md),
                (Path("/home/ubuntu/.openclaw/workspace/SOUL.md"), soul_md),
                (Path("/home/ubuntu/.openclaw/workspace/MEMORY.md"), memory_md),
                (Path("/home/ubuntu/.openclaw/workspace/soul.json"), json.dumps(soul_payload, indent=2, ensure_ascii=False)),
            ])

        for fpath, content in files_to_write:
            try:
                fpath.parent.mkdir(parents=True, exist_ok=True)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as _fe:
                log.warning(f"[soul_engine] error writing {fpath}: {_fe}")

        log.info(f"[soul_engine] ✓ Identidad Firby grabada en disco ({owner_first} / {clinic_name} / {receptionist_name})")
        return soul_payload

    @classmethod
    def get_soul_prompt_injection(cls, instance_id: Optional[str] = None) -> str:
        """Retorna el bloque de inyección de alma para el prompt de cualquier modelo."""
        inst_dir = cls.get_instance_dir(instance_id)
        is_americas = "clinica-de-las-americas" in str(inst_dir)
        soul_json_path = inst_dir / "soul.json"
        
        data = {}
        if soul_json_path.exists():
            try:
                with open(soul_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        
        if not data:
            data = cls.sync_soul(instance_id)

        owner = data.get("owner", {})
        biz = data.get("business", {})
        asst = data.get("assistant", {})

        def_asst = asst.get('name') or "Firby"
        def_biz = biz.get('name') or "Firby AI"
        def_owner_first = owner.get('first_name') or "Santiago"
        def_owner_full = owner.get('full_name') or "Santiago Rubio Parra"
        def_owner_email = owner.get('email') or "growsantix@gmail.com"
        def_city = biz.get('city') or "Medellín, Colombia"
        def_phone = biz.get('phone') or "+57 324 369 9856"
        def_services = biz.get('services') or ["Operadores Autónomos 24/7", "Agendamiento con Google Calendar", "Línea Ejecutiva por WhatsApp"]
        services_str = ", ".join(def_services) if def_services else "Operadores Digitales de Atención y Citas"
        def_schedule = biz.get('schedule') or "24 horas"

        return f"""MEMORIA MAESTRA DE IDENTIDAD (FIRBY OPENCLAW & HERMES CORE):
- Tu nombre: {def_asst} (Socia de IA y recepcionista oficial)
- Negocio / Clínica: {def_biz}
- Dueño / Administrador: {def_owner_first} (Nombre completo: {def_owner_full})
- Correo del Dueño: {def_owner_email}
- Ciudad: {def_city}
- Teléfono del negocio: {def_phone}
- Servicios: {services_str}
- Horario: {def_schedule}

REGLA INVIOLABLE DE RECONOCIMIENTO:
Tú sabes perfectamente quién es tu dueño ({def_owner_first}). Si te pregunta si recuerdas su nombre o datos personales, responde con total seguridad, naturalidad y exactitud."""
