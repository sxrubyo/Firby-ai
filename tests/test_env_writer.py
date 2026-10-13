from pathlib import Path

from firby_cli_common import load_env, update_env_key


def test_update_env_key_quotes_values_that_run_sh_can_source(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("DEMO_MODE=false\n", encoding="utf-8")

    update_env_key(str(env_path), "DEMO_BUSINESS_NAME", "Clínica Las Américas")

    raw = env_path.read_text(encoding="utf-8")
    assert "DEMO_BUSINESS_NAME='Clínica Las Américas'" in raw
    assert load_env(str(env_path))["DEMO_BUSINESS_NAME"] == "Clínica Las Américas"

    shell_check = __import__("subprocess").run(
        ["bash", "-n", str(env_path)], capture_output=True, text=True
    )
    assert shell_check.returncode == 0, shell_check.stderr
