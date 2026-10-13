# -*- coding: utf-8 -*-
import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from src.firby.admin.dashboard import AdminCommandsMixin

class DummyRuntime(AdminCommandsMixin):
    def __init__(self):
        self._admin_pending = {}
        self.admin_learning = MagicMock()
        self.simulator = MagicMock()

@pytest.mark.anyio
async def test_admin_natural_command_triggers():
    runtime = DummyRuntime()
    clinic = {"name": "Mi Negocio", "setup_buffer": "{}"}

    # Mock db and Config in src.firby.admin.dashboard
    mock_db = MagicMock()
    mock_config = MagicMock()
    mock_config.NOVA_ENABLED = False
    mock_config.PLATFORM = "whatsapp"

    with patch("src.firby.admin.dashboard.db", mock_db), \
         patch("src.firby.admin.dashboard.Config", mock_config):
        
        # Test Telegram natural language trigger
        res_tg = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="te doy el token de telegram?",
            clinic=clinic
        )
        assert any("Conexión de Telegram" in r for r in res_tg)
        assert mock_db.update_clinic.called

        # Test Slack natural language trigger
        mock_db.update_clinic.reset_mock()
        res_sl = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="quiero conectar slack a mi workspace",
            clinic=clinic
        )
        assert any("Conexión de Slack" in r for r in res_sl)
        assert mock_db.update_clinic.called

        # Test Gmail natural language trigger
        mock_db.update_clinic.reset_mock()
        res_gm = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="vincular gmail con api key",
            clinic=clinic
        )
        assert any("Conexión de Gmail" in r for r in res_gm)
        assert mock_db.update_clinic.called


@pytest.mark.anyio
async def test_admin_raw_token_auto_detection():
    runtime = DummyRuntime()
    clinic = {"name": "Mi Negocio", "setup_buffer": "{}"}

    mock_db = MagicMock()
    mock_config = MagicMock()
    mock_config.BASE_URL = "https://example.com"
    mock_config.WEBHOOK_SECRET = "secret123"

    with patch("src.firby.admin.dashboard.db", mock_db), \
         patch("src.firby.admin.dashboard.Config", mock_config), \
         patch("src.firby.channels.onboarding.validate_telegram_token", AsyncMock(return_value="my_test_bot")), \
         patch("src.firby.channels.onboarding.validate_slack_token", AsyncMock(return_value={"team": "MyTeam", "team_id": "T123", "bot_id": "B123"})), \
         patch("src.firby.channels.onboarding.validate_gmail_credentials", AsyncMock(return_value={"email": "santiago@gmail.com", "name": "Santiago"})):

        # 1. Test raw Telegram token auto-detection
        res_tg = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="Este es el bot token: 123456789:AAHxBAp_W7nDD4G02M4E70etHciOMDQ_ah0 y lo quiero por allá",
            clinic=clinic
        )
        assert any("He detectado y configurado automáticamente tu bot de Telegram" in r for r in res_tg)
        assert mock_db.add_linked_channel.called
        assert mock_db.add_linked_channel.call_args[1]["platform"] == "telegram"

        # 2. Test raw Slack token auto-detection
        mock_db.add_linked_channel.reset_mock()
        res_sl = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="mira mi token es xoxb-12345-67890-abc123xyz de Slack",
            clinic=clinic
        )
        assert any("He detectado y configurado tu token de Slack" in r for r in res_sl)
        assert mock_db.add_linked_channel.called
        assert mock_db.add_linked_channel.call_args[1]["platform"] == "slack"

        # 3. Test raw Gmail credential auto-detection
        mock_db.add_linked_channel.reset_mock()
        res_gm = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="aquí está la Google api key AIzaSyMockKeyForTestSuite0000000000000 o el secret",
            clinic=clinic
        )
        assert any("He detectado y registrado tus credenciales de Gmail" in r for r in res_gm)
        assert mock_db.add_linked_channel.called
        assert mock_db.add_linked_channel.call_args[1]["platform"] == "gmail"

        # 4. Test WhatsApp Cloud API token auto-detection (EAA...)
        mock_db.add_linked_channel.reset_mock()
        res_wa2 = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="mira mi whatsapp token EAA12345XYZ y no hay phone id en setup_buffer",
            clinic=clinic
        )
        assert any("Token de WhatsApp Cloud API Detectado" in r for r in res_wa2)
        assert any("primero necesito el *Phone Number ID*" in r for r in res_wa2)

        # 4.5. Test Notion token auto-detection (ntn_...)
        mock_db.add_linked_channel.reset_mock()
        with patch("src.firby.channels.onboarding.validate_notion_token", AsyncMock(return_value={"workspace_name": "My Workspace", "bot_name": "My Bot"})):
            res_notion = await runtime._admin_natural_command(
                chat_id="admin_1",
                text="quiero conectar mi notion: ntn_1234567890abcdefghijklmnopqrstuvwxyz",
                clinic=clinic
            )
            assert any("He detectado y registrado tu clave de integración de Notion" in r for r in res_notion)
            assert mock_db.add_linked_channel.called
            assert mock_db.add_linked_channel.call_args[1]["platform"] == "notion"

        # 5. Test generic unrecognized token auto-detection
        res_gen = await runtime._admin_natural_command(
            chat_id="admin_1",
            text="conecta este token raro abcdefghijklmnopqrstuvwxyz1234567890 que no coincide con ninguno",
            clinic=clinic
        )
        assert any("Credencial Detectada" in r for r in res_gen)
        assert any("no puedo determinar a qué servicio pertenece" in r for r in res_gen)
        assert any("`/telegram`" in r for r in res_gen)

        # 6. Test Calendar/Agenda status natural trigger
        mock_calendar = MagicMock()
        mock_calendar.has_google_calendar.return_value = False
        mock_calendar.has_calendly.return_value = False
        with patch("src.firby.admin.dashboard.calendar_bridge", mock_calendar):
            res_cal = await runtime._admin_natural_command(
                chat_id="admin_1",
                text="cómo está mi agenda o calendario?",
                clinic=clinic
            )
            assert any("Sin agenda vinculada todavia." in r for r in res_cal)
            assert any("/vincular-agenda" in r for r in res_cal)


