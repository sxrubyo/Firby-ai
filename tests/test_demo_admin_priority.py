import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/interfaces/web/demo_handler.py"


def _find_admin_interceptor_condition(tree: ast.AST) -> str:
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        source = ast.get_source_segment(HANDLER.read_text(encoding="utf-8"), node.test) or ""
        if "is_admin_demo" in source and "_beta_active" in source:
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr in {"handle", "_admin_natural_command"}:
                        return source
    raise AssertionError("No se encontró el interceptor admin del handler de demo")


def test_demo_mode_has_priority_over_admin_interceptor():
    source = HANDLER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    condition = _find_admin_interceptor_condition(tree)

    assert "not Config.DEMO_MODE" in condition


def test_demo_does_not_invent_cold_email_origin():
    source = HANDLER.read_text(encoding="utf-8")

    assert "correo electrónico en frío (cold email)" not in source
    assert "me pasaron tu contacto para hacerte una demostración" not in source
    assert 'BUENO: "hola, soy Firby, una asistente de IA' not in source


def test_demo_onboarding_leads_when_owner_has_no_context():
    source = HANDLER.read_text(encoding="utf-8")

    assert '"dame contexto"' in source
    assert "toma la iniciativa" in source
    assert "ofrece una prueba concreta" in source
