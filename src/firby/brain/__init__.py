"""Brain subsystem: reasoning, memory, learning, humanity, and uncertainty detection."""

from .uncertainty import (
    UncertaintyDetector,
    uncertainty_detector,
    UNCERTAINTY_MARKERS_ES,
    UNCERTAINTY_MARKERS_EN,
)
from .engine import (
    init_brain,
    patch_llm_first,
)
from .llm_engine import (
    LLMProvider,
)
from src.firby.core.proxy import GlobalProxy
v8_process_response = GlobalProxy("v8_process_response")
from .filters import AntiRobotFilter
from .humanity import (
    EmotionalMirrorEngine,
    ClientPersonaDetector,
    TimeContextualizer,
    ConversationRhythmAnalyzer,
    SectorClosingScripts,
    ResponseQualityPatcher,
)
from .intelligence import (
    ModelManager,
    SmartVariety,
    ConversationIntelligence,
    PersonaEvolution,
)
from .infinite_memory import InfiniteMemoryEngine, AdminTeachingRule
from .psychology import LatAmPsychologyEngine
from .database import DatabaseManager

__all__ = [
    "UncertaintyDetector",
    "uncertainty_detector",
    "UNCERTAINTY_MARKERS_ES",
    "UNCERTAINTY_MARKERS_EN",
    "init_brain",
    "patch_llm_first",
    "LLMProvider",
    "v8_process_response",
    "AntiRobotFilter",
    "EmotionalMirrorEngine",
    "ClientPersonaDetector",
    "TimeContextualizer",
    "ConversationRhythmAnalyzer",
    "SectorClosingScripts",
    "ResponseQualityPatcher",
    "ModelManager",
    "SmartVariety",
    "ConversationIntelligence",
    "PersonaEvolution",
    "InfiniteMemoryEngine",
    "AdminTeachingRule",
    "LatAmPsychologyEngine",
    "DatabaseManager",
]
