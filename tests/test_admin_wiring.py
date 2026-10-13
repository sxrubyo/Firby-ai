from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_aprendizaje_uses_real_self_improvement_engine():
    source = (ROOT / "src/firby/admin/commands.py").read_text()
    assert "from src.core.admin_engines import SelfImprovementEngine" in source
    assert "from firby_admin import SelfImprovementEngine" not in source


def test_dashboard_confirmations_use_robust_affirmative_helper():
    source = (ROOT / "src/firby/admin/dashboard.py").read_text()
    assert "from src.firby.utils.helpers import is_affirmative" in source
    assert 'text.lower().strip() in ["si", "ok", "claro"]' not in source
    assert 'step == "confirm" and text.lower().strip() == "si"' not in source
