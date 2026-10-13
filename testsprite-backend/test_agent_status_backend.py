# Backend verification test for TestSprite runner
# Verifies /health and /api/operator/config contracts on Firby runtime
import os
import requests

TARGET_URL = os.environ.get("TARGET_URL", "http://127.0.0.1:8001")
__AUTH_HEADERS__ = globals().get("__AUTH_HEADERS__", {})

def test_firby_health_endpoint():
    endpoint = f"{TARGET_URL}/health"
    headers = {"Accept": "application/json", **__AUTH_HEADERS__}
    res = requests.get(endpoint, headers=headers, timeout=10)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data.get("status") in ("healthy", "online") or data.get("ok") is True, f"Unhealthy status: {data}"

def test_firby_operator_config_endpoint():
    endpoint = f"{TARGET_URL}/api/operator/config"
    headers = {"Accept": "application/json", **__AUTH_HEADERS__}
    res = requests.get(endpoint, headers=headers, timeout=10)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data.get("ok") is True, f"Expected ok:True, got: {data}"
    assert "config" in data, f"Missing config in payload: {data}"
    config = data["config"]
    assert config.get("tenant_id") == "firby_landing" or "identity" in config, f"Unexpected config: {config}"

if __name__ == "__main__":
    test_firby_health_endpoint()
    test_firby_operator_config_endpoint()
    print("TestSprite backend assertions passed successfully.")
