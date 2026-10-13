import pytest
import asyncio
from src.firby.admin.outreach import AdminOutreachEngine
from src.firby.channels.outreach_router import OmnichannelOutreachRouter


def test_admin_outreach_command_parsing():
    engine = AdminOutreachEngine(tenant_id="clinica-de-las-americas")
    
    parsed = engine.parse_escribir_command("/escribir 3124348669 Hola Santiago, le confirmamos la cita médica.")
    assert parsed is not None
    assert parsed["recipient"] == "3124348669"
    assert "Hola Santiago" in parsed["message"]


def test_admin_outreach_recipient_normalization():
    engine = AdminOutreachEngine()
    
    norm_wa = engine.normalize_recipient("3124348669", preferred_channel="whatsapp")
    assert norm_wa["chat_id"] == "573124348669@s.whatsapp.net"
    assert norm_wa["channel"] == "whatsapp"

    norm_tg = engine.normalize_recipient("123456789", preferred_channel="telegram")
    assert norm_tg["chat_id"] == "123456789"
    assert norm_tg["channel"] == "telegram"


def test_admin_outreach_session_tracking():
    engine = AdminOutreachEngine(tenant_id="clinica-de-las-americas")
    norm = engine.normalize_recipient("573124348669@s.whatsapp.net")
    
    session = engine.register_outreach_session(norm, "Mensaje de prueba", admin_id="santiago")
    assert session["chat_id"] == "573124348669@s.whatsapp.net"
    assert session["status"] == "awaiting_patient_reply"

    retrieved = engine.get_outreach_context("573124348669@s.whatsapp.net")
    assert retrieved is not None
    assert retrieved["outbound_message"] == "Mensaje de prueba"


def test_omnichannel_outreach_router_dispatch():
    router = OmnichannelOutreachRouter(tenant_id="clinica-de-las-americas")
    sent_messages = []

    async def mock_send(chat_id, text):
        sent_messages.append({"chat_id": chat_id, "text": text})

    async def _test():
        result = await router.dispatch_admin_outreach(
            raw_recipient="3124348669",
            message="Hola Santiago, como modelo de lenguaje le recuerdo su cita médica.",
            send_fn=mock_send,
            preferred_channel="whatsapp",
            admin_id="santiago",
        )
        assert result["success"] is True
        assert len(sent_messages) == 1
        assert sent_messages[0]["chat_id"] == "573124348669@s.whatsapp.net"
        assert "como modelo de lenguaje" not in sent_messages[0]["text"]

    import asyncio
    asyncio.run(_test())
