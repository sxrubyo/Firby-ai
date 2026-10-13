import firby_app


def test_modern_launcher_forwards_sync_flags(monkeypatch):
    calls = []
    monkeypatch.setattr(firby_app, "_py", lambda *args: calls.append(args))

    firby_app.cmd_sync("--dry-run --no-restart")

    assert calls == [("firby_cli.py", "sync", "--dry-run", "--no-restart")]
