# -*- coding: utf-8 -*-
"""
Firby Platform — Technical Codebase & Project Discovery
======================================================
Permite la inspección técnica segura y estructurada de un proyecto/repositorio:
- Detección de frameworks (FastAPI, Flask, Express, Next.js, etc.).
- Identificación de puntos de entrada (Entrypoints) y servicios.
- Detección de motores de bases de datos.
- Requerimientos de entorno con REDACCIÓN ESTRICTA DE SECRETOS.
- Límites de profundidad (max_depth=3) y exclusión de artefactos binarios.
"""

from __future__ import annotations
import os
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Set, Optional


@dataclass
class CodebaseModel:
    root_path: str
    detected_framework: str = "Unknown"
    entrypoints: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    required_env_vars: List[str] = field(default_factory=list)
    api_routes: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    deployment_method: str = "Unknown"
    is_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_path": self.root_path,
            "detected_framework": self.detected_framework,
            "entrypoints": self.entrypoints,
            "databases": self.databases,
            "required_env_vars": self.required_env_vars,
            "api_routes_count": len(self.api_routes),
            "dependencies_count": len(self.dependencies),
            "deployment_method": self.deployment_method
        }


class CodebaseScanner:
    """Escáner técnico seguro de repositorios con política de solo lectura."""

    IGNORE_DIRS = {
        ".git", "node_modules", ".venv", "__pycache__", ".pytest_cache",
        "logs", "dist", "build", ".cache", ".antigravity"
    }

    SECRET_PATTERNS = [
        re.compile(r"(api[_-]?key|secret|password|token|private[_-]?key)", re.IGNORECASE)
    ]

    def __init__(self, root_path: str, max_depth: int = 3):
        self.root_path = os.path.abspath(root_path)
        self.max_depth = max_depth

    @classmethod
    def scan_directory(cls, root_path: str, max_depth: int = 3) -> CodebaseModel:
        """Método de clase utilitario para escanear directamente una ruta."""
        return cls(root_path, max_depth=max_depth).scan()

    def scan(self) -> CodebaseModel:
        model = CodebaseModel(root_path=self.root_path)

        if not os.path.exists(self.root_path) or not os.path.isdir(self.root_path):
            model.is_safe = False
            return model

        all_files: List[str] = []
        root_depth = self.root_path.rstrip(os.sep).count(os.sep)

        for current_root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            current_depth = current_root.count(os.sep) - root_depth
            if current_depth > self.max_depth:
                dirs.clear()
                continue

            for f in files:
                rel = os.path.relpath(os.path.join(current_root, f), self.root_path)
                all_files.append(rel)

        # 1. Detección de Frameworks
        files_set = set(all_files)
        if any("fastapi" in f.lower() for f in files_set) or self._has_content_match("from fastapi import", files_set):
            model.detected_framework = "FastAPI"
        elif any("flask" in f.lower() for f in files_set) or self._has_content_match("from flask import", files_set):
            model.detected_framework = "Flask"
        elif "next.config.js" in files_set or "next.config.mjs" in files_set:
            model.detected_framework = "Next.js"
        elif "package.json" in files_set:
            model.detected_framework = "Node.js"
        elif any(f.endswith(".html") for f in files_set):
            model.detected_framework = "HTML"

        # 2. Detección de Entrypoints
        candidates = [
            "src/interfaces/web/app.py", "app.py", "main.py", "server.py", "firby.py",
            "server.js", "index.js", "index.html", "run.sh"
        ]
        for c in candidates:
            if c in files_set:
                model.entrypoints.append(c)

        # 3. Detección de Bases de Datos
        if any(f.endswith(".db") or f.endswith(".sqlite") or f.endswith(".sqlite3") for f in files_set):
            model.databases.append("SQLite")
        if self._has_content_match("psycopg2", files_set) or self._has_content_match("asyncpg", files_set):
            model.databases.append("PostgreSQL")
        if self._has_content_match("pymongo", files_set) or self._has_content_match("mongoose", files_set):
            model.databases.append("MongoDB")
        if self._has_content_match("redis", files_set):
            model.databases.append("Redis")

        # 4. Inspección Segura de Variables de Entorno (CON REDACCIÓN ABSOLUTA)
        env_files = [f for f in files_set if f in (".env.example", ".env", "env.example")]
        for ef in env_files:
            full_p = os.path.join(self.root_path, ef)
            try:
                with open(full_p, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            var_name = line.split("=", 1)[0].strip()
                            if var_name and var_name not in model.required_env_vars:
                                # Redacción: Solo se registra el nombre de la variable, jamás el valor
                                model.required_env_vars.append(var_name)
            except Exception:
                pass

        # 5. Detección de Deployment
        if "ecosystem.config.js" in files_set or "ecosystem.config.cjs" in files_set:
            model.deployment_method = "PM2 Process Manager"
        elif "docker-compose.yml" in files_set or "Dockerfile" in files_set:
            model.deployment_method = "Docker Container"
        elif "Procfile" in files_set:
            model.deployment_method = "Procfile Runner"

        return model

    def _has_content_match(self, keyword: str, files_set: Set[str]) -> bool:
        """Busca una palabra clave en archivos de código sin cargar binarios."""
        py_js_files = [f for f in files_set if f.endswith((".py", ".js", ".ts", ".json"))]
        for f in py_js_files[:15]:
            full_p = os.path.join(self.root_path, f)
            try:
                with open(full_p, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read(2048)
                    if keyword in content:
                        return True
            except Exception:
                pass
        return False
