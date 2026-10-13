# -*- coding: utf-8 -*-
import pytest
from pathlib import Path
from src.firby.core.tenant import TenantConfig, TenantRegistry, load_env_file

def test_tenant_config_defaults():
    config = TenantConfig(tenant_id="test_clinic", name="Test Clinic", dir_path="/tmp/test")
    assert config.tenant_id == "test_clinic"
    assert config.pm2_name == "firby-test_clinic"
    assert config.platform == "telegram"
    assert config.is_base is False

def test_tenant_registry_discovery(tmp_path):
    # Create fake base env
    base_env = tmp_path / ".env"
    base_env.write_text("PORT=8000\nCLINIC_NAME=Base Clinic\n")

    # Create fake instance
    inst_dir = tmp_path / "instances" / "clinica-demo"
    inst_dir.mkdir(parents=True)
    (inst_dir / ".env").write_text("PORT=8001\nCLINIC_NAME=Clinica Demo\n")

    tenants = TenantRegistry.discover_tenants(root_dir=tmp_path)
    assert len(tenants) == 2

    base = TenantRegistry.get("base")
    assert base is not None
    assert base.port == 8000
    assert base.name == "Base Clinic"

    demo = TenantRegistry.get("clinica-demo")
    assert demo is not None
    assert demo.port == 8001
    assert demo.name == "Clinica Demo"

def test_tenant_header_resolution():
    headers = {"X-Tenant-ID": "base"}
    tenant = TenantRegistry.resolve_from_headers(headers)
    assert tenant is not None
    assert tenant.tenant_id == "base"
