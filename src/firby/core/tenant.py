# -*- coding: utf-8 -*-
"""
Firby Core Tenant Manager
Provides centralized tenant registration, configuration loading, and request resolution.
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_env_file(filepath: str | Path) -> Dict[str, str]:
    """Carga un archivo .env en un diccionario sin modificar os.environ."""
    env = {}
    path = Path(filepath)
    if not path.exists():
        return env

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                val = val.strip().strip("'").strip('"')
                env[key.strip()] = val
    return env


@dataclass
class TenantConfig:
    """Configuración inmutable y aislada de un Tenant (Inquilino / Instancia)."""
    tenant_id: str
    name: str
    port: int = 8000
    dir_path: str = ""
    env: Dict[str, str] = field(default_factory=dict)
    is_base: bool = False
    sector: str = "general"
    created_at: str = ""

    @property
    def pm2_name(self) -> str:
        return "firby" if self.is_base else f"firby-{self.tenant_id}"

    @property
    def db_path(self) -> str:
        return self.env.get("DB_PATH", os.path.join(self.dir_path, "firby.db") if self.dir_path else "firby.db")

    @property
    def master_key(self) -> str:
        return self.env.get("MASTER_API_KEY", "")

    @property
    def platform(self) -> str:
        return self.env.get("PLATFORM", "telegram")

    @property
    def webhook_secret(self) -> str:
        return self.env.get("WEBHOOK_SECRET", "")

    @property
    def is_active(self) -> bool:
        """Verifica en SQLite si la instancia está configurada y lista."""
        try:
            if not os.path.exists(self.db_path):
                return False
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            row = cursor.execute("SELECT setup_done FROM clinic WHERE id=1").fetchone()
            conn.close()
            return bool(row and row[0])
        except Exception:
            return False


class TenantRegistry:
    """Registro global y dinámico de Tenants en la plataforma Firby."""

    _tenants: Dict[str, TenantConfig] = {}
    _base_dir: Path = Path(__file__).resolve().parents[3]

    @classmethod
    def discover_tenants(cls, root_dir: Optional[str | Path] = None) -> List[TenantConfig]:
        """Descubre automáticamente todas las instancias configuradas en el sistema."""
        root = Path(root_dir) if root_dir else cls._base_dir
        cls._tenants.clear()

        # 1. Instancia Base (.env en la raíz)
        base_env_path = root / ".env"
        base_env = load_env_file(base_env_path) if base_env_path.exists() else {}
        base_tenant = TenantConfig(
            tenant_id="base",
            name=base_env.get("CLINIC_NAME", "Instancia Base"),
            port=int(base_env.get("PORT", 8000)),
            dir_path=str(root),
            env=base_env,
            is_base=True,
            sector=base_env.get("SECTOR", "salud"),
        )
        cls._tenants["base"] = base_tenant

        # 2. Instancias en directorio instances/
        instances_dir = root / "instances"
        if instances_dir.exists() and instances_dir.is_dir():
            for item in instances_dir.iterdir():
                if item.is_dir() and (item / ".env").exists():
                    tenant_id = item.name
                    tenant_env = load_env_file(item / ".env")
                    config = TenantConfig(
                        tenant_id=tenant_id,
                        name=tenant_env.get("CLINIC_NAME", tenant_id.replace("-", " ").title()),
                        port=int(tenant_env.get("PORT", 8000)),
                        dir_path=str(item),
                        env=tenant_env,
                        is_base=False,
                        sector=tenant_env.get("SECTOR", "salud"),
                    )
                    cls._tenants[tenant_id] = config

        return list(cls._tenants.values())

    @classmethod
    def get(cls, tenant_id: str) -> Optional[TenantConfig]:
        if not cls._tenants:
            cls.discover_tenants()
        return cls._tenants.get(tenant_id)

    @classmethod
    def resolve_from_headers(cls, headers: Dict[str, str]) -> Optional[TenantConfig]:
        """Resuelve el tenant basado en headers HTTP como X-Tenant-ID o Host."""
        if not cls._tenants:
            cls.discover_tenants()

        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-ID")
        if tenant_id and tenant_id in cls._tenants:
            return cls._tenants[tenant_id]

        return cls._tenants.get("base")


# Singleton / helpers de módulo
tenant_registry = TenantRegistry
