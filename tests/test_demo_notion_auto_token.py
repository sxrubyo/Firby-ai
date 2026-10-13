import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import firby
from src.interfaces.web.demo_handler import handle_demo_message


class TestDemoNotionAutoToken(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.runtime = MagicMock()
        self.runtime.__class__.__module__ = "firby"
        async def _mock_complete(messages, **kwargs):
            txt = str(messages)
            if "sk_" in txt or "elevenlabs" in txt.lower():
                return ("¡Super! Configuré tu token de ElevenLabs para las notas de voz de tu bot.", {})
            if "ntn_" in txt or "notion" in txt.lower():
                if "sincronizar notion" in txt.lower():
                    return ("Notion no está conectado aún. Ingresa tu token ntn_ para vincularlo.", {})
                return ("¡Excelente! Conectado a Notion Espacio Santiago. Ahora puedo sincronizarme con tus bases de datos.", {})
            return ("Entendido perfecto.", {})

        mock_engine = AsyncMock()
        mock_engine.complete = AsyncMock(side_effect=_mock_complete)
        self.runtime.llm_engine = mock_engine
        self.runtime.generator = None
        self.runtime._llm_runtime_available.return_value = True
        self.runtime._generate_llm_response = AsyncMock(return_value="Claro que sí, token procesado con éxito.")
        self.runtime._send_audio = AsyncMock()
        self.runtime._demo_sessions = {}
        self.runtime._session_mgr.touch_and_cleanup.return_value = (False, [])
        self.clinic = {"id": "test_clinic", "name": "Clínica Test"}





        self.runtime._session_mgr.touch_and_cleanup.return_value = (False, [])
        self.clinic = {"id": "test_clinic", "name": "Clínica Test"}


    @patch("src.core.globals.db")
    async def test_notion_token_auto_detection_in_demo(self, mock_db):
        mock_notion_info = {
            "workspace_name": "Espacio Santiago",
            "bot_name": "Firby Bot"
        }

        with patch("src.firby.channels.onboarding.validate_notion_token", AsyncMock(return_value=mock_notion_info)):
            text = "Heyy esta es mi api de Notion, usala: ntn_TEST_TOKEN_DUMMY"
            result = await handle_demo_message(self.runtime, "user_123", text, self.clinic)
            
            assert result is not None
            combined = " ".join(result)
            assert "Notion" in combined
            assert "Espacio Santiago" in combined
            assert "sincronizarme con tus bases de datos" in combined

    @patch("src.core.globals.db")
    async def test_notion_sync_command_when_not_connected(self, mock_db):
        mock_db.get_linked_channels.return_value = []
        text = "sincronizar notion"
        result = await handle_demo_message(self.runtime, "user_123", text, self.clinic)
        
        assert result is not None
        combined = " ".join(result)
        assert "Notion no está conectado" in combined
        assert "ntn_" in combined

    @patch("src.core.globals.db")
    async def test_elevenlabs_token_auto_detection_in_demo(self, mock_db):
        text = "Aqui esta mi token de elevenlabs sk_TEST_TOKEN_DUMMY"
        result = await handle_demo_message(self.runtime, "user_123", text, self.clinic)
        
        assert result is not None
        combined = " ".join(result)
        assert "ElevenLabs" in combined or "voz" in combined
