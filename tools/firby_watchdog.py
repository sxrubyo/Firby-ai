#!/usr/bin/env python3
"""Watchdog que monitorea el bridge y lo reinicia si está desconectado."""
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request

BRIDGE_STATUS_URL = "http://localhost:8002/status"
FIRBY_HEALTH_URL = "http://localhost:8003/health"
LOCK_FILE = Path("/tmp/firby-watchdog.lock")


def check_bridge():
    try:
        req = Request(BRIDGE_STATUS_URL, headers={"Accept": "application/json"})
        with urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        return data.get("status") == "open", data
    except Exception:
        return False, {}


def check_firby():
    try:
        req = Request(FIRBY_HEALTH_URL, headers={"Accept": "application/json"})
        with urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        return data.get("status") == "online", data
    except Exception:
        return False, {}


def restart_bridge():
    subprocess.run(["pm2", "restart", "whatsapp-bridge"], capture_output=True, timeout=30)
    return "whatsapp-bridge reiniciado via watchdog"


def restart_firby():
    subprocess.run(["pm2", "restart", "firby-clinica-de-las-americas", "firby"], capture_output=True, timeout=30)
    return "instancias firby reiniciadas via watchdog"


def main():
    if LOCK_FILE.exists():
        age = time.time() - LOCK_FILE.stat().st_mtime
        if age < 60:
            return
    LOCK_FILE.touch()

    actions = []

    conn_ok, bridge_data = check_bridge()
    if not conn_ok:
        actions.append(restart_bridge())
    else:
        stats = bridge_data.get("stats", {})
        if stats.get("failed", 0) > stats.get("sent", 0) and stats.get("failed", 0) > 3:
            actions.append(restart_bridge())

    firby_ok, _ = check_firby()
    if not firby_ok:
        actions.append(restart_firby())

    if actions:
        with open("/home/ubuntu/firby/logs/watchdog.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {' | '.join(actions)}\n")

    LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
