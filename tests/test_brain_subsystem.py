# -*- coding: utf-8 -*-
import pytest
from src.firby.brain import (
    UncertaintyDetector,
    uncertainty_detector,
    ModelManager,
    LLMProvider,
    v8_process_response,
    AntiRobotFilter,
    EmotionalMirrorEngine,
    ClientPersonaDetector,
    TimeContextualizer,
    SmartVariety,
    ConversationIntelligence,
    PersonaEvolution,
    DatabaseManager,
    init_brain,
)

def test_brain_facade_imports():
    assert UncertaintyDetector is not None
    assert uncertainty_detector is not None
    assert ModelManager is not None
    assert LLMProvider is not None
    assert callable(v8_process_response)
    assert AntiRobotFilter is not None
    assert EmotionalMirrorEngine is not None
    assert ClientPersonaDetector is not None
    assert TimeContextualizer is not None
    assert SmartVariety is not None
    assert ConversationIntelligence is not None
    assert PersonaEvolution is not None
    assert DatabaseManager is not None

def test_uncertainty_detector_basic():
    detector = UncertaintyDetector()
    res = detector.detect_uncertainty_markers("no sé qué responder sobre ese tema")
    assert res is True

def test_anti_robot_filter_basic():
    assert callable(v8_process_response)
    res = v8_process_response("Hola, ¿cómo puedo ayudarte hoy?", chat_id="test_chat")
    assert isinstance(res, str)
    assert len(res) > 0
