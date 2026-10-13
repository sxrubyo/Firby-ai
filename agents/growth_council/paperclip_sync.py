"""Synchronizes the Firby Growth Council with Paperclip.
Registers the 8 specialized agents into Paperclip under company 'Firby AI'.
"""

import json
import urllib.request
import urllib.error
import sys

PAPERCLIP_URL = "http://127.0.0.1:3100"
COMPANY_NAME = "Firby AI"
PYTHON_BIN = "/home/ubuntu/firby/.venv/bin/python"
FIRBY_ROOT = "/home/ubuntu/firby"

AGENTS_SPEC = [
    {
        "name": "IdeaHunter",
        "role": "researcher",
        "title": "Estratega de Ángulos B2B y Fricción de Mercado",
        "icon": "search",
        "capabilities": "Investigación profunda de dolores operativos B2B, detección de horas críticas y formulación de ángulos de adquisición.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "brainstorm"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "CopyChief",
        "role": "cmo",
        "title": "Director de Copywriting de Respuesta Directa",
        "icon": "target",
        "capabilities": "Redacción de anuncios persuasivos de alta conversión en español directo de negocios, cero emojis y oferta de prueba de 7 días.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "campaign"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "VisualDirector",
        "role": "designer",
        "title": "Director Creativo y Formatos de Video Split-Screen",
        "icon": "eye",
        "capabilities": "Dirección de arte, guiones segundo a segundo y storyboards de pantalla dividida (Web vs WhatsApp del dueño).",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "campaign"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "AssetBuilder",
        "role": "designer",
        "title": "Especialista en Piezas Estáticas y Mockups de UI",
        "icon": "puzzle",
        "capabilities": "Diseño de anuncios estáticos de alta densidad, comparativas Antes/Después, tipografía Neue Montreal y acentos neón.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "campaign"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "BrandAuditor",
        "role": "qa",
        "title": "Auditor de Reglas Inquebrantables de Marca",
        "icon": "shield",
        "capabilities": "Auditoría implacable: cero emojis, cero clichés de IA, cero $1.000 COP, respeto estricto al rol de canales.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "audit"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "Skeptic",
        "role": "qa",
        "title": "Comprador B2B Escéptico y Prueba de Estrés",
        "icon": "swords",
        "capabilities": "Simulación de objeciones duras de dueños de negocio desconfiados, detección de promesas débiles antes del gasto en pauta.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "campaign"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "MediaPlanner",
        "role": "cmo",
        "title": "Estratega de Tráfico Pago B2B & Pauta",
        "icon": "rocket",
        "capabilities": "Estructura de campañas en Meta Ads y Google Search, segmentación B2B, distribución de presupuesto y arquitectura UTM.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "campaign"],
            "cwd": FIRBY_ROOT,
        }
    },
    {
        "name": "FunnelOptimizer",
        "role": "engineer",
        "title": "Ingeniero de Conversión y Alineación de Landing Web",
        "icon": "zap",
        "capabilities": "Alineación de mensaje 1:1 entre el anuncio y la landing page firbyai.lat, personalización del widget flotante.",
        "adapterType": "process",
        "adapterConfig": {
            "command": PYTHON_BIN,
            "args": ["-m", "agents.growth_council.cli", "campaign"],
            "cwd": FIRBY_ROOT,
        }
    },
]

def http_get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def http_post(url, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, headers={"Content-Type": "application/json", "Accept": "application/json"}, data=payload)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def sync_growth_council():
    print(f"[*] Conectando a Paperclip en {PAPERCLIP_URL}...")
    try:
        companies = http_get(f"{PAPERCLIP_URL}/api/companies")
    except Exception as e:
        print(f"[!] Error al conectar con Paperclip: {e}")
        return False

    firby_co = next((c for c in companies if c.get("name") == COMPANY_NAME), None)
    if not firby_co:
        print(f"[!] Empresa '{COMPANY_NAME}' no encontrada en Paperclip.")
        return False
    
    co_id = firby_co["id"]
    print(f"[+] Empresa detectada: {firby_co['name']} (ID: {co_id})")

    # List current agents
    existing_agents = http_get(f"{PAPERCLIP_URL}/api/companies/{co_id}/agents")
    existing_map = {a.get("name"): a for a in existing_agents}
    print(f"[*] Agentes actuales registrados: {len(existing_agents)} ({', '.join(existing_map.keys())})")

    created_count = 0
    for spec in AGENTS_SPEC:
        name = spec["name"]
        if name in existing_map:
            print(f"    [-] Agente '{name}' ya existe (ID: {existing_map[name]['id']}). Omitiendo creación.")
            continue
        
        print(f"    [+] Creando agente '{name}' ({spec['title']})...")
        payload = {
            "name": spec["name"],
            "role": spec["role"],
            "title": spec["title"],
            "icon": spec["icon"],
            "capabilities": spec["capabilities"],
            "adapterType": spec["adapterType"],
            "adapterConfig": spec["adapterConfig"],
            "runtimeConfig": {
                "heartbeat": {"enabled": False}
            }
        }
        try:
            res = http_post(f"{PAPERCLIP_URL}/api/companies/{co_id}/agent-hires", payload)
            agent_data = res.get("agent", {})
            print(f"        -> Creado con ID: {agent_data.get('id')}")
            created_count += 1
        except urllib.error.HTTPError as he:
            err_msg = he.read().decode()
            print(f"        [!] Error creando '{name}': {he.code} - {err_msg}")
        except Exception as ex:
            print(f"        [!] Excepcion creando '{name}': {ex}")

    print(f"\n[OK] Sincronizacion completada: {created_count} agentes nuevos incorporados al consejo en Paperclip.")
    return True

if __name__ == "__main__":
    sync_growth_council()
