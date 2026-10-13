# -*- coding: utf-8 -*-
"""
Firby Autonomous Automation Architect (Nova Engine)
Translates natural language business rules into active n8n workflows and webhook pipelines.

Example prompt:
"Cada vez que un paciente agende una cita, envíale un correo de confirmación al doctor y guarda los datos en Google Sheets"
"""
from __future__ import annotations

import os
import json
import uuid
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx

log = logging.getLogger("firby.automation_architect")


class AutomationArchitect:
    """Generates and deploys n8n workflows from natural language descriptions."""

    def __init__(self, db_path: str = "/home/ubuntu/.n8n/database.sqlite"):
        self.db_path = db_path

    async def create_workflow_from_natural_language(
        self, description: str, clinic_name: str = "Clínica"
    ) -> Dict[str, Any]:
        """
        Interprets a business rule description, builds an n8n workflow graph,
        and saves it directly into the active n8n instance.
        """
        workflow_id = str(uuid.uuid4())[:16]
        workflow_name = f"⚡ {clinic_name} - {description[:40]}..."
        
        # Build node graph based on parsed triggers & actions
        nodes, connections = self._build_workflow_nodes(description, workflow_id)

        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            version_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO workflow_entity (
                    id, name, active, nodes, connections, settings, 
                    versionId, createdAt, updatedAt, versionCounter, isArchived
                ) VALUES (?, ?, 1, ?, ?, '{}', ?, ?, ?, 1, 0)
            """, (
                workflow_id,
                workflow_name,
                json.dumps(nodes, ensure_ascii=False),
                json.dumps(connections, ensure_ascii=False),
                version_id,
                now_str,
                now_str
            ))
            conn.commit()
            conn.close()

            log.info(f"[AutomationArchitect] ✅ Workflow '{workflow_name}' ({workflow_id}) creado y activado en n8n")
            
            return {
                "ok": True,
                "workflow_id": workflow_id,
                "name": workflow_name,
                "status": "active",
                "message": f"Automatización '{workflow_name}' creada y activada con éxito en n8n."
            }

        except Exception as e:
            log.error(f"[AutomationArchitect] Error creando workflow en n8n: {e}", exc_info=True)
            return {
                "ok": False,
                "error": str(e),
                "message": "No se pudo registrar la automatización en el motor de n8n."
            }

    def _build_workflow_nodes(self, description: str, workflow_id: str) -> tuple[List[Dict], Dict]:
        """Generates the n8n node structure and wiring based on keywords."""
        desc_lower = description.lower()
        
        nodes = []
        connections = {}

        # 1. Trigger Node (Webhook by default for Firby events)
        webhook_path = f"firby_auto_{workflow_id}"
        nodes.append({
            "parameters": {
                "httpMethod": "POST",
                "path": webhook_path,
                "responseMode": "onReceived",
                "responseData": "allEntries"
            },
            "name": "Webhook Receptor Firby",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300],
            "id": str(uuid.uuid4())
        })

        current_node_name = "Webhook Receptor Firby"
        x_pos = 500

        # 2. Add Google Sheets Node if mentioned
        if "sheet" in desc_lower or "excel" in desc_lower or "tabla" in desc_lower or "fila" in desc_lower:
            sheet_id = str(uuid.uuid4())
            nodes.append({
                "parameters": {
                    "operation": "appendOrUpdate",
                    "sheetName": "Citas y Leads",
                    "options": {}
                },
                "name": "Guardar en Google Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [x_pos, 300],
                "id": sheet_id
            })
            connections[current_node_name] = {
                "main": [[{"node": "Guardar en Google Sheets", "type": "main", "index": 0}]]
            }
            current_node_name = "Guardar en Google Sheets"
            x_pos += 250

        # 3. Add Email / Gmail Node if mentioned
        if "correo" in desc_lower or "email" in desc_lower or "gmail" in desc_lower:
            email_id = str(uuid.uuid4())
            nodes.append({
                "parameters": {
                    "sendTo": "doctor@clinica.com",
                    "subject": "Nueva notificación de paciente - Firby",
                    "message": "Se ha recibido un nuevo evento de paciente en el sistema."
                },
                "name": "Enviar Notificación Gmail",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2.1,
                "position": [x_pos, 300],
                "id": email_id
            })
            if current_node_name in connections:
                connections[current_node_name]["main"][0].append(
                    {"node": "Enviar Notificación Gmail", "type": "main", "index": 0}
                )
            else:
                connections[current_node_name] = {
                    "main": [[{"node": "Enviar Notificación Gmail", "type": "main", "index": 0}]]
                }
            current_node_name = "Enviar Notificación Gmail"
            x_pos += 250

        # 4. Add Telegram / Alert Node if mentioned
        if "telegram" in desc_lower or "alerta" in desc_lower or "avisa" in desc_lower:
            telegram_id = str(uuid.uuid4())
            nodes.append({
                "parameters": {
                    "chatId": "admin",
                    "text": "🚨 *Alerta Firby*: Nueva acción ejecutada por automatización."
                },
                "name": "Alerta Telegram",
                "type": "n8n-nodes-base.telegram",
                "typeVersion": 1.2,
                "position": [x_pos, 300],
                "id": telegram_id
            })
            if current_node_name in connections:
                connections[current_node_name]["main"][0].append(
                    {"node": "Alerta Telegram", "type": "main", "index": 0}
                )
            else:
                connections[current_node_name] = {
                    "main": [[{"node": "Alerta Telegram", "type": "main", "index": 0}]]
                }

        return nodes, connections
