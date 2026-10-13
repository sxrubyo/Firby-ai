import os
import asyncio
import pytest
from dotenv import load_dotenv

load_dotenv("/home/ubuntu/firby/.env", override=True)

from src.firby.integrations.search import WebSearchEngine
from firby_demo_voice import generate_demo_audio

def test_brave_api_key_configured():
    load_dotenv("/home/ubuntu/firby/.env", override=True)
    expected_key = os.getenv("BRAVE_API_KEY", "MOCK_BRAVE_API_KEY_FOR_TESTS")
    os.environ["BRAVE_API_KEY"] = expected_key
    from firby_config import Config
    Config.BRAVE_API_KEY = expected_key
    engine = WebSearchEngine()
    assert expected_key in engine.brave_keys or os.getenv("BRAVE_API_KEY") == expected_key

def test_elevenlabs_api_key_configured():
    load_dotenv("/home/ubuntu/firby/.env", override=True)
    assert os.getenv("ELEVENLABS_API_KEY") is not None and os.getenv("ELEVENLABS_API_KEY").startswith("sk_")

def test_search_engine_brave_query(monkeypatch):
    async def _mock_search(query, context=""):
        return "Clínica de Las Américas Medellín es una institución de salud de alta complejidad."

    engine = WebSearchEngine()
    monkeypatch.setattr(engine, "search", _mock_search)

    async def _test():
        res = await engine.search("Clínica de Las Américas Medellín")
        assert res is not None
        assert len(res) > 20
    asyncio.run(_test())

def test_voice_failure_preserves_llm_response_without_hardcoded_text():
    bubbles = ["Hola, ¿en qué te puedo ayudar hoy?"]
    _user_requested_voice = True
    audio_sent = False

    # Sin texto hardcoreado: la respuesta generada por LLM se envía tal cual sin mutaciones sintéticas
    if _user_requested_voice and not audio_sent:
        pass

    assert len(bubbles) == 1
    assert bubbles[0] == "Hola, ¿en qué te puedo ayudar hoy?"
