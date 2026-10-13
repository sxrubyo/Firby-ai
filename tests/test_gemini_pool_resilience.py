# -*- coding: utf-8 -*-
"""
tests/test_gemini_pool_resilience.py
====================================
Suite de Verificación y Resiliencia del Pool de Inferencia Gemini 3.5 Flash:
1. Inicialización y carga segura de 9+ credenciales.
2. Test de concurrencia: 25 requests simultáneos sin colisión ni race conditions.
3. Test de resiliencia: Failover en cascada (429 -> Timeout -> 503 -> 200).
4. Test de truncamiento: MAX_TOKENS y texto mutilado descartados y rotados.
5. Circuit Breaker: Errores no reintentables (401/403) abren circuito por 300s.
6. Fallback determinista: Cuando todas las claves fallan, retorna (None, "") seguro.
7. Observabilidad y Métricas: Cero exposición de secretos en telemetría.
"""

import asyncio
import json
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.inference.gemini_pool import GeminiInferencePool, KeyHealthState


@pytest.fixture
def mock_pool():
    pool = GeminiInferencePool(model_name="gemini-3.5-flash")
    # Forzar claves mock para pruebas deterministas
    pool._keys = [f"AIzaSyMockKeyForTestingNumber{i:02d}XYZ" for i in range(1, 11)]
    pool._key_metadata.clear()
    for idx, k in enumerate(pool._keys, start=1):
        kid = f"KEY_{idx:02d}"
        from src.core.inference.gemini_pool import KeyTelemetry
        pool._key_metadata[k] = KeyTelemetry(key_id=kid, masked_key=f"{k[:6]}...{k[-6:]}")
    return pool


def test_01_pool_initialization():
    real_pool = GeminiInferencePool(model_name="gemini-3.5-flash")
    assert real_pool.total_keys >= 9, f"Se esperaban al menos 9 credenciales, encontradas {real_pool.total_keys}"
    assert real_pool.model_name == "gemini-3.5-flash"

    status = real_pool.get_pool_status()
    assert status["model"] == "gemini-3.5-flash"
    assert status["total_credentials"] >= 9
    assert len(status["credentials"]) >= 9
    for cred in status["credentials"]:
        assert cred["state"] == "HEALTHY"
        assert not cred["masked"].startswith("AIzaSyMock")  # En DEV son reales


def test_02_concurrency_25_requests(mock_pool):
    async def _run():
        call_records = []

        async def mock_post(url, json=None, **kwargs):
            await asyncio.sleep(0.05)  # Simular latencia de red
            key_in_url = url.split("key=")[-1]
            call_records.append(key_in_url)
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "candidates": [{
                    "finishReason": "STOP",
                    "content": {"parts": [{"text": "Respuesta completa de prueba concurrente."}]}
                }],
                "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 20}
            }
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            tasks = [
                mock_pool.generate_turn(
                    system_prompt="Eres Firby",
                    history=[],
                    message=f"Mensaje concurrente {i}"
                )
                for i in range(25)
            ]
            results = await asyncio.gather(*tasks)

        assert len(results) == 25
        for text, model in results:
            assert text == "Respuesta completa de prueba concurrente."
            assert model == "gemini-3.5-flash"

        # Verificar que las solicitudes se distribuyeron entre múltiples claves sin colisión
        unique_keys_used = set(call_records)
        assert len(unique_keys_used) >= 5, f"Solo se usaron {len(unique_keys_used)} claves para 25 requests concurrentes"

    asyncio.run(_run())


def test_03_resilience_failover_sequence(mock_pool):
    """
    Simulación exigida en Sección 15:
    KEY 1 -> 429
    KEY 2 -> timeout
    KEY 3 -> 503
    KEY 4 -> success (200)
    Siguiente request:
    KEY 4 -> failure (500)
    KEY 5 -> success
    """
    async def _run():
        key4_called_count = 0

        async def mock_post(url, json=None, **kwargs):
            nonlocal key4_called_count
            key_used = url.split("key=")[-1]
            mock_resp = MagicMock()

            if key_used.endswith("01XYZ"):
                # KEY 1 -> 429
                mock_resp.status_code = 429
                mock_resp.text = "Rate limit exceeded"
                return mock_resp
            elif key_used.endswith("02XYZ"):
                # KEY 2 -> timeout
                import httpx
                raise httpx.TimeoutException("Read timeout on Key 2")
            elif key_used.endswith("03XYZ"):
                # KEY 3 -> 503
                mock_resp.status_code = 503
                mock_resp.text = "Model overloaded"
                return mock_resp
            elif key_used.endswith("04XYZ"):
                key4_called_count += 1
                if key4_called_count == 1:
                    # KEY 4 -> success primera vez
                    mock_resp.status_code = 200
                    mock_resp.json.return_value = {
                        "candidates": [{
                            "finishReason": "STOP",
                            "content": {"parts": [{"text": "Respuesta exitosa de Key 4."}]}
                        }],
                        "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15}
                    }
                    return mock_resp
                else:
                    # KEY 4 -> falla segunda vez
                    mock_resp.status_code = 500
                    mock_resp.text = "Internal error on Key 4"
                    return mock_resp
            elif key_used.endswith("05XYZ"):
                # KEY 5 -> success
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "Respuesta exitosa de Key 5."}]}
                    }],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15}
                }
                return mock_resp
            else:
                # Otras claves retornan 200
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "Respuesta genérica exitosa."}]}
                    }],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15}
                }
                return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Primera solicitud: debe atravesar 429 -> Timeout -> 503 -> Key 4 (200)
            text1, model1 = await mock_pool.generate_turn("Eres Firby", [], "Consulta 1")
            assert text1 == "Respuesta exitosa de Key 4."
            assert model1 == "gemini-3.5-flash"

            # Segunda solicitud: Forzar inicio en Key 4 para probar su falla (500) y failover a Key 5
            mock_pool._current_index = 3
            text2, model2 = await mock_pool.generate_turn("Eres Firby", [], "Consulta 2")
            assert text2 == "Respuesta exitosa de Key 5."
            assert model2 == "gemini-3.5-flash"

        # Verificar estados de salud en el pool
        status = mock_pool.get_pool_status()
        creds = {c["key_id"]: c for c in status["credentials"]}
        assert creds["KEY_01"]["state"] == KeyHealthState.COOLDOWN.value
        assert creds["KEY_02"]["state"] == KeyHealthState.COOLDOWN.value
        assert creds["KEY_03"]["state"] == KeyHealthState.COOLDOWN.value
        assert creds["KEY_04"]["state"] == KeyHealthState.COOLDOWN.value
        assert creds["KEY_05"]["state"] == KeyHealthState.HEALTHY.value

    asyncio.run(_run())


def test_04_truncation_max_tokens_guardrail(mock_pool):
    """
    Simulación exigida en Sección 16:
    Si provider devuelve finishReason = MAX_TOKENS y texto parcial:
    NO entregar al usuario. Debe descartar, registrar, rotar y entregar respuesta completa.
    """
    async def _run():
        attempt = 0

        async def mock_post(url, json=None, **kwargs):
            nonlocal attempt
            attempt += 1
            mock_resp = MagicMock()
            if attempt == 1:
                # KEY 1 devuelve texto cortado con MAX_TOKENS
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "MAX_TOKENS",
                        "content": {"parts": [{"text": "Firby está diseñado para atender a los visitantes y gestionar agend"}]}
                    }],
                    "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 600}
                }
                return mock_resp
            else:
                # KEY 2 devuelve texto completo con STOP
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "Firby es un operador autónomo que agenda citas en tiempo real."}]}
                    }],
                    "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 45}
                }
                return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            text, model = await mock_pool.generate_turn("Eres Firby", [], "¿Qué hace Firby?")
            assert attempt == 2
            # El usuario NUNCA recibe el texto truncado de Key 1
            assert "gestionar agend" not in text
            assert text == "Firby es un operador autónomo que agenda citas en tiempo real."
            assert mock_pool.is_response_complete(text) is True

        # Verificar telemetría de truncamiento
        status = mock_pool.get_pool_status()
        creds = {c["key_id"]: c for c in status["credentials"]}
        assert creds["KEY_01"]["truncation_discards"] == 1

    asyncio.run(_run())


def test_05_non_retryable_circuit_breaker(mock_pool):
    """
    Verifica que un error no reintentable (401 o 403) abra el circuito
    de la credencial por 300s en lugar de reintentar inútilmente con ella.
    """
    async def _run():
        call_count = 0

        async def mock_post(url, json=None, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            if call_count == 1:
                # Clave 1 tiene credencial inválida (401)
                mock_resp.status_code = 401
                mock_resp.text = "API key not valid. Please pass a valid API key."
                return mock_resp
            else:
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "Respuesta correcta tras circuito abierto."}]}
                    }],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 10}
                }
                return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            text, model = await mock_pool.generate_turn("Eres Firby", [], "Consulta")
            assert text == "Respuesta correcta tras circuito abierto."
            assert call_count == 2

        status = mock_pool.get_pool_status()
        creds = {c["key_id"]: c for c in status["credentials"]}
        assert creds["KEY_01"]["state"] == KeyHealthState.CIRCUIT_OPEN.value

    asyncio.run(_run())


def test_06_all_keys_exhausted_fallback(mock_pool):
    """
    Verifica que si todas las claves del pool fallan, se retorne (None, "")
    de forma limpia para que el runtime ejecute la contingencia determinista.
    """
    async def _run():
        async def mock_post(url, json=None, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 503
            mock_resp.text = "All service unavailable"
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            text, model = await mock_pool.generate_turn("Eres Firby", [], "Consulta")
            assert text is None
            assert model == ""

    asyncio.run(_run())


def test_07_metrics_observability_no_secrets(mock_pool):
    """Verifica que la telemetría nunca exponga claves en texto plano."""
    status = mock_pool.get_pool_status()
    serialized = json.dumps(status)
    for raw_k in mock_pool._keys:
        assert raw_k not in serialized, "Fuga de API key en texto plano en la telemetría del pool"
