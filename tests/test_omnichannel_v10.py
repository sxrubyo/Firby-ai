# -*- coding: utf-8 -*-
"""Pruebas unitarias para la Fase 1 del Omnicanal V10 (adaptadores y DB)."""
import pytest
import json
from unittest.mock import AsyncMock, patch
from src.firby.channels.telegram import TelegramAdapter
from src.firby.channels.slack import SlackAdapter
from src.firby.channels.base import NormalizedMessage
from src.firby.brain.database import DatabaseManager

# ─── Mocks para Webhooks ──────────────────────────────────────────────────────

TELEGRAM_WEBHOOK_TEXT = {
    "update_id": 10000,
    "message": {
        "message_id": 123,
        "from": {
            "id": 987654321,
            "is_bot": False,
            "first_name": "Test",
            "username": "tester"
        },
        "chat": {
            "id": 987654321,
            "type": "private"
        },
        "date": 1620000000,
        "text": "Hola, necesito información"
    }
}

TELEGRAM_WEBHOOK_PHOTO = {
    "update_id": 10001,
    "message": {
        "message_id": 124,
        "from": {"id": 987654321, "is_bot": False},
        "chat": {"id": 987654321, "type": "private"},
        "date": 1620000000,
        "photo": [
            {"file_id": "small_id", "file_unique_id": "u1", "width": 90, "height": 90},
            {"file_id": "big_id", "file_unique_id": "u2", "width": 320, "height": 320}
        ]
    }
}

SLACK_CHALLENGE = {
    "token": "token123",
    "challenge": "challenge_token_abc",
    "type": "url_verification"
}

SLACK_EVENT_MESSAGE = {
    "token": "token123",
    "team_id": "T123",
    "api_app_id": "A123",
    "event": {
        "type": "message",
        "user": "U12345678",
        "text": "Hello bot on Slack!",
        "ts": "1620000000.000100",
        "channel": "C98765432"
    },
    "type": "event_callback"
}

SLACK_EVENT_BOT_MESSAGE = {
    "token": "token123",
    "event": {
        "type": "message",
        "user": "U123",
        "bot_id": "B123",
        "text": "I am a bot reply",
        "channel": "C98765432"
    },
    "type": "event_callback"
}

# ─── Pruebas del Adaptador de Telegram ────────────────────────────────────────

@pytest.mark.anyio
async def test_telegram_adapter_handle_webhook_text():
    adapter = TelegramAdapter({"token": "123456:ABC-DEF"})
    normalized = await adapter.handle_webhook(TELEGRAM_WEBHOOK_TEXT)
    
    assert normalized is not None
    assert normalized.platform == "telegram"
    assert normalized.sender_id == "987654321"
    assert normalized.channel_id == "987654321"
    assert normalized.text == "Hola, necesito información"
    assert len(normalized.attachments) == 0

@pytest.mark.anyio
async def test_telegram_adapter_handle_webhook_photo():
    adapter = TelegramAdapter({"token": "123456:ABC-DEF"})
    normalized = await adapter.handle_webhook(TELEGRAM_WEBHOOK_PHOTO)
    
    assert normalized is not None
    assert normalized.platform == "telegram"
    assert len(normalized.attachments) == 1
    assert normalized.attachments[0]["type"] == "image"
    assert normalized.attachments[0]["file_id"] == "big_id"

@pytest.mark.anyio
async def test_telegram_adapter_ignores_bots():
    bot_payload = {
        "update_id": 10002,
        "message": {
            "message_id": 125,
            "from": {"id": 9999, "is_bot": True},
            "chat": {"id": 987654321, "type": "private"},
            "date": 1620000000,
            "text": "Ignórame"
        }
    }
    adapter = TelegramAdapter({"token": "123456:ABC-DEF"})
    normalized = await adapter.handle_webhook(bot_payload)
    assert normalized is None

@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_telegram_adapter_send_message(mock_post):
    mock_post.return_value = mock_response = AsyncMock()
    mock_response.status_code = 200
    
    adapter = TelegramAdapter({"token": "123456:ABC-DEF"})
    success = await adapter.send_message("987654321", "Test outgoing message")
    
    assert success is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.telegram.org/bot123456:ABC-DEF/sendMessage"
    assert kwargs["json"]["chat_id"] == "987654321"
    assert kwargs["json"]["text"] == "Test outgoing message"

# ─── Pruebas del Adaptador de Slack ───────────────────────────────────────────

@pytest.mark.anyio
async def test_slack_adapter_handle_challenge():
    adapter = SlackAdapter({"token": "xoxb-mock-token"})
    normalized = await adapter.handle_webhook(SLACK_CHALLENGE)
    
    assert normalized is not None
    assert normalized.platform == "slack"
    assert normalized.channel_id == "url_verification"
    assert normalized.sender_id == "slack_system"
    assert normalized.text == "challenge_token_abc"

@pytest.mark.anyio
async def test_slack_adapter_handle_message():
    adapter = SlackAdapter({"token": "xoxb-mock-token"})
    normalized = await adapter.handle_webhook(SLACK_EVENT_MESSAGE)
    
    assert normalized is not None
    assert normalized.platform == "slack"
    assert normalized.sender_id == "U12345678"
    assert normalized.channel_id == "C98765432"
    assert normalized.text == "Hello bot on Slack!"

@pytest.mark.anyio
async def test_slack_adapter_ignores_bots():
    adapter = SlackAdapter({"token": "xoxb-mock-token"})
    normalized = await adapter.handle_webhook(SLACK_EVENT_BOT_MESSAGE)
    assert normalized is None

@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_slack_adapter_send_message(mock_post):
    mock_post.return_value = mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"ok": True}
    
    adapter = SlackAdapter({"token": "xoxb-mock-token"})
    success = await adapter.send_message("C98765432", "Hello Slack channel")
    
    assert success is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://slack.com/api/chat.postMessage"
    assert kwargs["headers"]["Authorization"] == "Bearer xoxb-mock-token"
    assert kwargs["json"]["channel"] == "C98765432"
    assert kwargs["json"]["text"] == "Hello Slack channel"

# ─── Pruebas de Base de Datos para Canales Vinculados ──────────────────────────

def test_database_linked_channels_operations(tmp_path):
    db_file = tmp_path / "test_firby.db"
    db = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    
    # 1. Verificar lista vacía
    channels = db.get_linked_channels()
    assert len(channels) == 0
    
    # 2. Agregar canal
    channel_id = db.add_linked_channel(
        platform="slack",
        channel_identity="xoxb-12345",
        config_json={"signing_secret": "secret_abc"}
    )
    assert channel_id > 0
    
    # 3. Leer canales
    channels = db.get_linked_channels()
    assert len(channels) == 1
    assert channels[0]["platform"] == "slack"
    assert channels[0]["channel_identity"] == "xoxb-12345"
    assert channels[0]["config_json"] == {"signing_secret": "secret_abc"}
    assert channels[0]["is_active"] == 1
    
    # 4. Actualizar canal
    db.update_linked_channel(channel_id, is_active=False, config_json={"signing_secret": "new_secret"})
    channels = db.get_linked_channels()
    assert channels[0]["is_active"] == 0
    assert channels[0]["config_json"] == {"signing_secret": "new_secret"}
    
    # Solo activos
    active_channels = db.get_linked_channels(enabled_only=True)
    assert len(active_channels) == 0
    
    # 5. Borrar canal
    db.remove_linked_channel(channel_id)
    channels = db.get_linked_channels()
    assert len(channels) == 0

# ─── Pruebas de Onboarding Conversacional (Fase 2) ─────────────────────────────

from src.firby.channels.onboarding import (
    detect_tokens,
    validate_telegram_token,
    validate_slack_token,
    handle_omnichannel_setup_flow
)

def test_detect_tokens():
    # Telegram token
    res = detect_tokens("Aquí tienes mi token 123456789:AAH_abc123-def_xyz")
    assert res is not None
    assert res["platform"] == "telegram"
    assert res["token"] == "123456789:AAH_abc123-def_xyz"

    # Slack token
    res = detect_tokens("Conecta esto xoxb-1234567890-abcdef-ghijkl")
    assert res is not None
    assert res["platform"] == "slack"
    assert res["token"] == "xoxb-1234567890-abcdef-ghijkl"

    # Ninguno
    res = detect_tokens("Hola, no hay token aquí")
    assert res is None

@pytest.mark.anyio
@patch("httpx.AsyncClient.get")
async def test_validate_telegram_token_success(mock_get):
    mock_get.return_value = mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {"ok": True, "result": {"username": "my_test_bot"}}
    
    username = await validate_telegram_token("123:AA-Token")
    assert username == "my_test_bot"

@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_validate_slack_token_success(mock_post):
    mock_post.return_value = mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "ok": True,
        "team": "My Workspace",
        "team_id": "T123",
        "user": "U456",
        "bot_id": "B789"
    }
    
    info = await validate_slack_token("xoxb-token")
    assert info is not None
    assert info["team_id"] == "T123"
    assert info["team"] == "My Workspace"

class DummyRuntime:
    def __init__(self, db_mgr):
        self.db = db_mgr
        class Config:
            BASE_URL = "https://example.com"
            WEBHOOK_SECRET = "webhook_secret_123"
        self.Config = Config

@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_handle_omnichannel_setup_flow_telegram(mock_post, tmp_path):
    # Setup mocks
    mock_post.return_value = mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {"ok": True, "result": {"username": "my_test_bot"}}
    
    db_file = tmp_path / "test_firby.db"
    db_mgr = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    runtime = DummyRuntime(db_mgr)
    
    clinic = {"setup_buffer": json.dumps({"omni_flow": "telegram_waiting_token"})}
    
    # 1. Enviar texto sin token
    res = await handle_omnichannel_setup_flow(runtime, "admin_1", "Hola", clinic)
    assert "Aún no he detectado" in res[0]
    
    # 2. Cancelar flujo
    res = await handle_omnichannel_setup_flow(runtime, "admin_1", "cancelar", clinic)
    assert "cancelado" in res[0]
    
    # 3. Enviar token correcto
    # Re-setup clinic
    clinic = {"setup_buffer": json.dumps({"omni_flow": "telegram_waiting_token"})}
    
    # Mocking validate_telegram_token internally requires mock_get too
    with patch("src.firby.channels.onboarding.validate_telegram_token", AsyncMock(return_value="my_test_bot")):
        res = await handle_omnichannel_setup_flow(runtime, "admin_1", "Mi token es 123456:AA-Token", clinic)
        
    assert "He verificado tu token de Telegram con éxito" in res[0]
    assert "@my_test_bot" in res[1]
    
    # Verificar guardado en DB
    channels = db_mgr.get_linked_channels()
    assert len(channels) == 1
    assert channels[0]["platform"] == "telegram"
    assert channels[0]["channel_identity"] == "my_test_bot"
    assert channels[0]["config_json"] == {"token": "123456:AA-Token"}


@pytest.mark.anyio
async def test_handle_omnichannel_setup_flow_wa2_full_flow(tmp_path):
    """Prueba el flujo completo wa2: phone_id → token → validación → registro en DB."""
    db_file = tmp_path / "test_firby_wa2.db"
    db_mgr = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    runtime = DummyRuntime(db_mgr)

    # ── Paso 1: el admin envía un Phone Number ID ──────────────────────────
    clinic = {"setup_buffer": json.dumps({"omni_flow": "wa2_waiting_phone_id"})}
    res = await handle_omnichannel_setup_flow(runtime, "admin_1", "123456789012345", clinic)
    assert any("Phone Number ID registrado" in r for r in res), f"Expected phone ID confirmation, got: {res}"

    # ── Paso 2: texto sin ID numérico no avanza ───────────────────────────
    clinic2 = {"setup_buffer": json.dumps({"omni_flow": "wa2_waiting_phone_id"})}
    res2 = await handle_omnichannel_setup_flow(runtime, "admin_1", "no tengo el id", clinic2)
    assert any("No detecté un Phone Number ID" in r for r in res2)

    # ── Paso 3: admin da el Access Token ─────────────────────────────────
    buf_with_phone = {"omni_flow": "wa2_waiting_token", "wa2_phone_id": "123456789012345"}
    clinic3 = {"setup_buffer": json.dumps(buf_with_phone)}

    fake_wa_info = {"phone_number": "+57 300 123 4567", "display_name": "Clínica Test"}
    with patch(
        "src.firby.channels.onboarding.validate_whatsapp_cloud_token",
        AsyncMock(return_value=fake_wa_info),
    ):
        res3 = await handle_omnichannel_setup_flow(
            runtime, "admin_1", "Mi token es EAAabcd1234", clinic3
        )

    assert any("vinculado con éxito" in r for r in res3), f"Expected success, got: {res3}"
    assert any("+57 300 123 4567" in r for r in res3)

    # ── Paso 4: verificar en DB ───────────────────────────────────────────
    channels = db_mgr.get_linked_channels()
    wa_channels = [c for c in channels if c["platform"] == "whatsapp_cloud"]
    assert len(wa_channels) == 1
    assert wa_channels[0]["channel_identity"] == "123456789012345"
    cfg = wa_channels[0]["config_json"]
    assert cfg["phone_number_id"] == "123456789012345"
    assert cfg["phone_number"] == "+57 300 123 4567"


@pytest.mark.anyio
async def test_handle_omnichannel_setup_flow_wa2_invalid_token(tmp_path):
    """Prueba que un token de WA inválido produce el mensaje de error correcto."""
    db_file = tmp_path / "test_firby_wa2_fail.db"
    db_mgr = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    runtime = DummyRuntime(db_mgr)

    buf_with_phone = {"omni_flow": "wa2_waiting_token", "wa2_phone_id": "123456789012345"}
    clinic = {"setup_buffer": json.dumps(buf_with_phone)}

    with patch(
        "src.firby.channels.onboarding.validate_whatsapp_cloud_token",
        AsyncMock(return_value=None),  # Simula fallo de validación
    ):
        res = await handle_omnichannel_setup_flow(
            runtime, "admin_1", "Mi token es EAAinvalid0000", clinic
        )

    assert any("No pude validar el token" in r for r in res)


@pytest.mark.anyio
async def test_handle_omnichannel_setup_flow_wa2_cancel(tmp_path):
    """Prueba que el admin puede cancelar el flujo wa2 en cualquier paso."""
    db_file = tmp_path / "test_firby_wa2_cancel.db"
    db_mgr = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    runtime = DummyRuntime(db_mgr)

    clinic = {"setup_buffer": json.dumps({"omni_flow": "wa2_waiting_phone_id"})}
    res = await handle_omnichannel_setup_flow(runtime, "admin_1", "cancelar", clinic)
    assert "cancelado" in res[0]

@pytest.mark.anyio
async def test_handle_omnichannel_setup_flow_gmail(tmp_path):
    """Prueba el flujo completo de conexión de Gmail."""
    db_file = tmp_path / "test_firby_gmail.db"
    db_mgr = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    runtime = DummyRuntime(db_mgr)

    # 1. Enviar formato inválido
    clinic = {"setup_buffer": json.dumps({"omni_flow": "gmail_waiting_credentials"})}
    res = await handle_omnichannel_setup_flow(runtime, "admin_1", "credenciales-cortas", clinic)
    assert any("no parecen tener un formato válido" in r for r in res)

    # 2. Enviar credencial correcta (Google API Key)
    clinic = {"setup_buffer": json.dumps({"omni_flow": "gmail_waiting_credentials"})}
    res = await handle_omnichannel_setup_flow(runtime, "admin_1", "AIzaSyCorrectToken1234567890", clinic)
    assert any("recibidas exitosamente" in r for r in res)
    assert any("Autorizar acceso a Gmail" in r for r in res)

    # Verificar en DB
    channels = db_mgr.get_linked_channels()
    gmail_channels = [c for c in channels if c["platform"] == "gmail"]
    assert len(gmail_channels) == 1
    assert "santiago" in gmail_channels[0]["channel_identity"]
    cfg = gmail_channels[0]["config_json"]
    assert cfg["credentials"] == "AIzaSyCorrectToken1234567890"


@pytest.mark.anyio
async def test_notion_validation_and_sync(tmp_path):
    """Prueba la validación y sincronización de Notion."""
    from src.firby.channels.onboarding import validate_notion_token
    from src.firby.integrations.notion import NotionClient
    import src.core.globals as g

    # 1. Test validate_notion_token
    # Con token inválido
    assert await validate_notion_token("invalid_token") is None

    # Con token válido (simulando llamada exitosa)
    mock_me_response = {
        "object": "user",
        "id": "12345",
        "name": "Test Bot",
        "avatar_url": None,
        "type": "bot",
        "bot": {
            "owner": {
                "type": "workspace",
                "workspace_name": "Mi Espacio Notion"
            }
        }
    }
    
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json_data = json_data
        def json(self):
            return self._json_data

    async def mock_get(url, headers=None, **kwargs):
        if "users/me" in url:
            return MockResponse(200, mock_me_response)
        elif "children" in url:
            return MockResponse(200, {"results": [
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Contenido del párrafo"}]}},
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "Título 1"}]}}
            ]})
        return MockResponse(404, {})

    async def mock_post(url, headers=None, json=None, **kwargs):
        if "search" in url:
            return MockResponse(200, {"results": [
                {"object": "database", "id": "db_123", "title": [{"plain_text": "Base de Datos de Preguntas"}]}
            ]})
        elif "query" in url:
            return MockResponse(200, {"results": [
                {
                    "object": "page",
                    "id": "page_123",
                    "properties": {
                        "Name": {"type": "title", "title": [{"plain_text": "FAQ de Estética"}]},
                        "Detalle": {"type": "rich_text", "rich_text": [{"plain_text": "Detalle FAQ"}]}
                    }
                }
            ]})
        return MockResponse(404, {})

    with patch("httpx.AsyncClient.get", side_effect=mock_get), \
         patch("httpx.AsyncClient.post", side_effect=mock_post):
         
        # Validar token
        info = await validate_notion_token("ntn_1234567890abcdef")
        assert info is not None
        assert info["workspace_name"] == "Mi Espacio Notion"
        assert info["bot_name"] == "Test Bot"

        # Test NotionClient
        client = NotionClient("ntn_1234567890abcdef")
        
        # List databases
        dbs = await client.list_databases()
        assert len(dbs) == 1
        assert dbs[0]["id"] == "db_123"
        assert dbs[0]["title"] == "Base de Datos de Preguntas"

        # Get page content
        text = await client.get_page_text("page_123")
        assert "Contenido del párrafo" in text
        assert "## Título 1" in text

        # Sync database to KB (using mock KB)
        from unittest.mock import MagicMock
        mock_kb = MagicMock()
        with patch("src.core.globals.kb", mock_kb):
            res = await client.sync_database("db_123")
            assert res["ok"] is True
            assert res["pages_synced"] == 1
            assert mock_kb.ingest.called
            ingested_content = mock_kb.ingest.call_args[0][0]
            assert "FAQ de Estética" in ingested_content
            assert "Detalle FAQ" in ingested_content


@pytest.mark.anyio
async def test_elevenlabs_setup_action(tmp_path):
    """Prueba la configuración y el audio de prueba de ElevenLabs."""
    db_file = tmp_path / "test_elevenlabs.db"
    db_mgr = DatabaseManager(str(db_file), str(tmp_path / "vector.db"))
    
    # Mocking Runtime/Mixins
    from src.firby.admin.dashboard import AdminCommandsMixin
    class DummyRuntime(AdminCommandsMixin):
        def __init__(self, db_mgr):
            self.db = db_mgr
            self._send_audio_calls = []
        async def _send_audio(self, chat_id, path):
            self._send_audio_calls.append((chat_id, path))

    runtime = DummyRuntime(db_mgr)
    
    # Simular la llamada a apply_action con configure_channel / elevenlabs
    result_dict = {"reply": "OK"}
    clinic = {}
    
    # Mocking generate_demo_audio y open
    from unittest.mock import MagicMock
    mock_generate = AsyncMock(return_value="/tmp/test_voice.mp3")
    mock_exists = MagicMock(return_value=True)
    mock_unlink = MagicMock()
    
    with patch("src.firby.admin.dashboard.db", db_mgr), \
         patch("firby_demo_voice.generate_demo_audio", mock_generate), \
         patch("os.path.exists", mock_exists), \
         patch("os.unlink", mock_unlink):
         
        mock_el_token = "mock_elevenlabs_token_test_suite_12345"
        success = await runtime._admin_apply_action(
            action="configure_channel",
            data={"platform": "elevenlabs", "token": mock_el_token},
            clinic=clinic,
            chat_id="admin_1",
            result_dict=result_dict
        )
        
        assert success is True
        # Debe haberse registrado en DB
        channels = db_mgr.get_linked_channels()
        el_channels = [c for c in channels if c["platform"] == "elevenlabs"]
        assert len(el_channels) == 1
        assert el_channels[0]["config_json"]["token"] == mock_el_token
        
        # Debe haber intentado generar y enviar audio
        assert mock_generate.called
        assert len(runtime._send_audio_calls) == 1
        assert runtime._send_audio_calls[0] == ("admin_1", "/tmp/test_voice.mp3")
        assert mock_unlink.called
        assert "Conexión de ElevenLabs Configurada" in result_dict["reply"]
