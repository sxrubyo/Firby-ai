# 🗺️ Mapa de Arquitectura y Funciones del Repositorio
 Total Archivos Python: **640**
 Total Líneas de Código: **207,094**

## 📦 Módulos Principales

### `src/firby/channels/cli.py` (11884 líneas)
- **Clases (6):** FakeI18n, Sector, C, Spinner, Instance, Alert
- **Funciones:** 237
- **Imports:** `sys, os, json, time, subprocess, threading, shutil, hashlib`

### `src/interfaces/web/app.py` (10685 líneas)
- **Clases (25):** FacadeProxy, AvatarUploadRequest, ConversationSimulator, HallucinationGuard, FailurePredictorEngine, SmartContextManager, AppointmentStateMachine, ConversationRecoveryEngine, ResponseVariationEngine, ProactiveCampaignEngine, AdminIntelligentBriefing, SelfTestSuite, MockAnalysis, EventType, AgentEvent, EventBus, AgentTracer, ConversationObserver, AIDiagnostician, SkillEngine, TrainerGateway, OwnerStyleController, PromptEvolver, AdminClientMode, NovaRuleSync
- **Funciones:** 203
- **Imports:** `__future__.annotations, asyncio, hashlib, random, secrets, re, json, os`

### `instances/clinica-de-las-americas/src/interfaces/web/app.py` (10685 líneas)
- **Clases (25):** FacadeProxy, AvatarUploadRequest, ConversationSimulator, HallucinationGuard, FailurePredictorEngine, SmartContextManager, AppointmentStateMachine, ConversationRecoveryEngine, ResponseVariationEngine, ProactiveCampaignEngine, AdminIntelligentBriefing, SelfTestSuite, MockAnalysis, EventType, AgentEvent, EventBus, AgentTracer, ConversationObserver, AIDiagnostician, SkillEngine, TrainerGateway, OwnerStyleController, PromptEvolver, AdminClientMode, NovaRuleSync
- **Funciones:** 203
- **Imports:** `__future__.annotations, asyncio, hashlib, random, secrets, re, json, os`

### `firby_cli_runtime.py` (9379 líneas)
- **Clases (1):** Alert
- **Funciones:** 146
- **Imports:** `__future__.annotations, firby_cli_common.*, firby_cli_instances.*, firby_cli_common, firby_cli_instances, firby_cli_bb.BBContext, firby_cli_bb.bb_apply_persona, firby_cli_bb.bb_load_persona`

### `instances/clinica-de-las-americas/firby_cli_runtime.py` (9379 líneas)
- **Clases (1):** Alert
- **Funciones:** 146
- **Imports:** `__future__.annotations, firby_cli_common.*, firby_cli_instances.*, firby_cli_common, firby_cli_instances, firby_cli_bb.BBContext, firby_cli_bb.bb_apply_persona, firby_cli_bb.bb_load_persona`

### `src/firby/api/routes.py` (8967 líneas)
- **Clases (24):** ConversationSimulator, HallucinationGuard, FailurePredictorEngine, SmartContextManager, AppointmentStateMachine, ConversationRecoveryEngine, ResponseVariationEngine, ProactiveCampaignEngine, AdminIntelligentBriefing, SelfTestSuite, MockAnalysis, EventType, AgentEvent, EventBus, AgentTracer, ConversationObserver, AIDiagnostician, SkillEngine, TrainerGateway, OwnerStyleController, PromptEvolver, AdminClientMode, NovaRuleSync, InstanceCreateRequest
- **Funciones:** 187
- **Imports:** `__future__.annotations, src.domain.prompts.human_writer.STYLE_GUIDELINES, logging, hashlib, fastapi.FastAPI, fastapi.middleware.cors.CORSMiddleware, contextlib.asynccontextmanager, src.interfaces.web.admin_api.router`

### `src/interfaces/web/demo_handler.py` (4259 líneas)
- **Clases (1):** FirbyDemo
- **Funciones:** 33
- **Imports:** `__future__.annotations, logging, asyncio, re, json, time, random, base64`

### `instances/clinica-de-las-americas/src/interfaces/web/demo_handler.py` (4259 líneas)
- **Clases (1):** FirbyDemo
- **Funciones:** 33
- **Imports:** `__future__.annotations, logging, asyncio, re, json, time, random, base64`

### `src/firby/demo/handler.py` (4091 líneas)
- **Clases (1):** FirbyDemo
- **Funciones:** 32
- **Imports:** `__future__.annotations, logging, asyncio, re, json, time, random, base64`

### `tools/firby-omni.py` (3843 líneas)
- **Clases (4):** C, Spinner, Instance, Notification
- **Funciones:** 68
- **Imports:** `__future__.annotations, asyncio, json, os, sys, re, time, threading`

### `firby-omni.py` (3840 líneas)
- **Clases (4):** C, Spinner, Instance, Notification
- **Funciones:** 68
- **Imports:** `__future__.annotations, asyncio, json, os, sys, re, time, threading`

### `instances/clinica-de-las-americas/firby-omni.py` (3840 líneas)
- **Clases (4):** C, Spinner, Instance, Notification
- **Funciones:** 68
- **Imports:** `__future__.annotations, asyncio, json, os, sys, re, time, threading`

### `src/core/runtime.py` (3498 líneas)
- **Clases (1):** FirbyUltra
- **Funciones:** 28
- **Imports:** `__future__.annotations, asyncio, os, json, random, re, time, datetime.datetime`

### `instances/clinica-de-las-americas/src/core/runtime.py` (3498 líneas)
- **Clases (1):** FirbyUltra
- **Funciones:** 28
- **Imports:** `__future__.annotations, asyncio, os, json, random, re, time, datetime.datetime`

### `src/firby/admin/dashboard.py` (3296 líneas)
- **Clases (1):** AdminCommandsMixin
- **Funciones:** 4
- **Imports:** `__future__.annotations, typing.Dict, typing.List, typing.Any, typing.Optional, datetime.datetime, datetime.timedelta, logging`

### `src/core/globals.py` (2856 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 44
- **Imports:** `__future__.annotations, asyncio, hashlib, json, logging, math, os, random`

### `instances/clinica-de-las-americas/src/core/globals.py` (2856 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 44
- **Imports:** `__future__.annotations, asyncio, hashlib, json, logging, math, os, random`

### `src/firby/brain/llm_engine.py` (2718 líneas)
- **Clases (10):** LLMProvider, GroqProvider, GeminiProvider, OpenRouterProvider, OpenAIProvider, LLMServiceError, LLMEngine, MessageAnalyzer, ReasoningEngine, ResponseGenerator
- **Funciones:** 72
- **Imports:** `__future__.annotations, os, re, json, time, random, logging, asyncio`

### `tests/test_demo_patient_entry.py` (1603 líneas)
- **Clases (41):** _DemoDb, _DummyConn, _Search, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Resp, _FakeAsyncClient, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine, _Engine
- **Funciones:** 72
- **Imports:** `pytest, sys, types, uuid, importlib.util, asyncio, pathlib.Path, firby_domino`

### `src/firby/brain/humanity.py` (1602 líneas)
- **Clases (6):** EmotionalMirrorEngine, ClientPersonaDetector, TimeContextualizer, ConversationRhythmAnalyzer, SectorClosingScripts, ResponseQualityPatcher
- **Funciones:** 43
- **Imports:** `__future__.annotations, os, re, json, logging, time, random, datetime.datetime`

### `landing/generate_landing.py` (1595 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `src/firby/brain/database.py` (1569 líneas)
- **Clases (1):** DatabaseManager
- **Funciones:** 71
- **Imports:** `__future__.annotations, os, sqlite3, json, logging, datetime.datetime, datetime.timedelta, typing.List`

### `landing/generate_landing_v3.py` (1448 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `firby_cli_common.py` (1447 líneas)
- **Clases (4):** FakeI18n, Sector, C, Spinner
- **Funciones:** 77
- **Imports:** `sys, os, json, time, subprocess, threading, shutil, hashlib`

### `instances/clinica-de-las-americas/firby_cli_common.py` (1447 líneas)
- **Clases (4):** FakeI18n, Sector, C, Spinner
- **Funciones:** 77
- **Imports:** `sys, os, json, time, subprocess, threading, shutil, hashlib`

### `src/interfaces/web/admin_api.py` (1379 líneas)
- **Clases (3):** PersonaUpdate, ModelUpdate, TeachRequest
- **Funciones:** 5
- **Imports:** `json, os, sqlite3, logging, pathlib.Path, datetime.datetime, typing.List, typing.Optional`

### `landing/generate_landing_v7.py` (1341 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `landing/generate_landing_v5.py` (1320 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `landing/generate_landing_v6.py` (1305 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `landing/generate_landing_v4.py` (1302 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `src/core/admin_engines.py` (1297 líneas)
- **Clases (6):** FirbyAdmin, AuthEngine, AdminLearningEngine, SimulationEngine, SelfImprovementEngine, TaskManager
- **Funciones:** 24
- **Imports:** `__future__.annotations, asyncio, logging, json, re, time, hashlib, secrets`

### `instances/clinica-de-las-americas/src/core/admin_engines.py` (1297 líneas)
- **Clases (6):** FirbyAdmin, AuthEngine, AdminLearningEngine, SimulationEngine, SelfImprovementEngine, TaskManager
- **Funciones:** 24
- **Imports:** `__future__.annotations, asyncio, logging, json, re, time, hashlib, secrets`

### `src/core/production_monitor.py` (1219 líneas)
- **Clases (1):** FirbyProduction
- **Funciones:** 5
- **Imports:** `__future__.annotations, logging, re, time, typing.Any, typing.Dict, typing.List, typing.Optional`

### `instances/clinica-de-las-americas/src/core/production_monitor.py` (1219 líneas)
- **Clases (1):** FirbyProduction
- **Funciones:** 5
- **Imports:** `__future__.annotations, logging, re, time, typing.Any, typing.Dict, typing.List, typing.Optional`

### `src/firby/brain/intelligence.py` (1167 líneas)
- **Clases (7):** ConversationIntelligence, HyperHumanEngine, SmartVariety, ConversionFunnelTracker, MultilingualHandler, PersonaEvolution, ModelManager
- **Funciones:** 37
- **Imports:** `__future__.annotations, asyncio, json, logging, random, re, time, datetime.datetime`

### `src/firby/production/handoff.py` (1150 líneas)
- **Clases (3):** HandoffTicket, HandoffLearning, SmartAdminHandoff
- **Funciones:** 37
- **Imports:** `__future__.annotations, asyncio, json, logging, random, re, sqlite3, time`

### `firby_cli_instances.py` (1087 líneas)
- **Clases (1):** Instance
- **Funciones:** 28
- **Imports:** `__future__.annotations, firby_cli_common.*, firby_cli_common, firby_cli_bb.BBContext, firby_cli_bb.bb_apply_persona, firby_cli_bb.bb_load_persona, firby_cli_bb.bb_persona_defaults, firby_cli_bb.bb_personality_catalog`

### `instances/clinica-de-las-americas/firby_cli_instances.py` (1087 líneas)
- **Clases (1):** Instance
- **Funciones:** 28
- **Imports:** `__future__.annotations, firby_cli_common.*, firby_cli_common, firby_cli_bb.BBContext, firby_cli_bb.bb_apply_persona, firby_cli_bb.bb_load_persona, firby_cli_bb.bb_persona_defaults, firby_cli_bb.bb_personality_catalog`

### `firby_admin.py` (900 líneas)
- **Clases (6):** FirbyAdmin, AuthEngine, AdminLearningEngine, SimulationEngine, SelfImprovementEngine, TaskManager
- **Funciones:** 22
- **Imports:** `__future__.annotations, asyncio, logging, json, re, time, hashlib, secrets`

### `instances/clinica-de-las-americas/firby_admin.py` (900 líneas)
- **Clases (6):** FirbyAdmin, AuthEngine, AdminLearningEngine, SimulationEngine, SelfImprovementEngine, TaskManager
- **Funciones:** 22
- **Imports:** `__future__.annotations, asyncio, logging, json, re, time, hashlib, secrets`

### `firby_brain_v10.py` (821 líneas)
- **Clases (2):** LLMFirstVerdict, LLMResponseValidator
- **Funciones:** 23
- **Imports:** `__future__.annotations, dataclasses.dataclass, re, logging, random, typing.Any, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/firby_brain_v10.py` (821 líneas)
- **Clases (2):** LLMFirstVerdict, LLMResponseValidator
- **Funciones:** 23
- **Imports:** `__future__.annotations, dataclasses.dataclass, re, logging, random, typing.Any, typing.Dict, typing.List`

### `src/firby/brain/engine.py` (804 líneas)
- **Clases (2):** LLMFirstVerdict, LLMResponseValidator
- **Funciones:** 23
- **Imports:** `__future__.annotations, dataclasses.dataclass, re, logging, random, typing.Any, typing.Dict, typing.List`

### `tests/test_patient_greeting_flow.py` (761 líneas)
- **Clases (2):** FakeProductionMgr, FakeAuth
- **Funciones:** 34
- **Imports:** `pytest, asyncio, importlib.util, sys, types, uuid, pathlib.Path, firby_core.conversation_engine.ConversationEngine`

### `firby_init.py` (722 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 20
- **Imports:** `__future__.annotations, os, sys, json, re, time, secrets, shutil`

### `instances/clinica-de-las-americas/firby_init.py` (722 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 20
- **Imports:** `__future__.annotations, os, sys, json, re, time, secrets, shutil`

### `scripts/long_conversation_harness.py` (700 líneas)
- **Clases (3):** ScenarioTurn, Scenario, TurnResult
- **Funciones:** 17
- **Imports:** `__future__.annotations, argparse, json, math, os, re, statistics, sys`

### `firby_domino.py` (696 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 19
- **Imports:** `__future__.annotations, functools.lru_cache, pathlib.Path, re, typing.Any, typing.Dict, typing.List, typing.Optional`

### `src/firby/production/domino.py` (696 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 19
- **Imports:** `__future__.annotations, functools.lru_cache, pathlib.Path, re, typing.Any, typing.Dict, typing.List, typing.Optional`

### `instances/clinica-de-las-americas/firby_domino.py` (696 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 19
- **Imports:** `__future__.annotations, functools.lru_cache, pathlib.Path, re, typing.Any, typing.Dict, typing.List, typing.Optional`

### `firby_i18n.py` (690 líneas)
- **Clases (2):** TranslationSet, I18n
- **Funciones:** 22
- **Imports:** `__future__.annotations, json, os, pathlib.Path, typing.Dict, typing.Optional, dataclasses.dataclass`

### `instances/clinica-de-las-americas/firby_i18n.py` (690 líneas)
- **Clases (2):** TranslationSet, I18n
- **Funciones:** 22
- **Imports:** `__future__.annotations, json, os, pathlib.Path, typing.Dict, typing.Optional, dataclasses.dataclass`

### `firby_core/smart_prompts.py` (670 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `__future__.annotations, typing.Any, typing.Dict, typing.List, typing.Optional`

### `instances/clinica-de-las-americas/firby_core/smart_prompts.py` (670 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `__future__.annotations, typing.Any, typing.Dict, typing.List, typing.Optional`

### `firby_bridge.py` (656 líneas)
- **Clases (8):** BridgeTurn, TransportReply, Transport, BridgeStore, FirbyTransport, LocalFirbyTransport, BridgeLogger, FirbyBridge
- **Funciones:** 40
- **Imports:** `__future__.annotations, argparse, asyncio, json, os, sqlite3, sys, uuid`

### `instances/clinica-de-las-americas/firby_bridge.py` (656 líneas)
- **Clases (8):** BridgeTurn, TransportReply, Transport, BridgeStore, FirbyTransport, LocalFirbyTransport, BridgeLogger, FirbyBridge
- **Funciones:** 40
- **Imports:** `__future__.annotations, argparse, asyncio, json, os, sqlite3, sys, uuid`

### `firby_send_guard.py` (650 líneas)
- **Clases (1):** SendGuard
- **Funciones:** 22
- **Imports:** `__future__.annotations, logging, re, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional`

### `src/domain/send_guard.py` (650 líneas)
- **Clases (1):** SendGuard
- **Funciones:** 22
- **Imports:** `__future__.annotations, logging, re, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional`

### `instances/clinica-de-las-americas/firby_send_guard.py` (650 líneas)
- **Clases (1):** SendGuard
- **Funciones:** 22
- **Imports:** `__future__.annotations, logging, re, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional`

### `src/core/ovni_handler.py` (615 líneas)
- **Clases (1):** OvniHandler
- **Funciones:** 9
- **Imports:** `__future__.annotations, json, logging, os, re, subprocess, time, typing.Any`

### `src/firby/utils/i18n.py` (611 líneas)
- **Clases (2):** TranslationSet, I18n
- **Funciones:** 18
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, dataclasses.dataclass`

### `src/firby/core/messenger.py` (611 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `__future__.annotations, src.firby.admin.commands.get_command_handler, firby_demo_voice.generate_demo_audio, firby_demo_voice.should_send_voice_in_demo, firby_demo_voice.API_KEYS, base64`

### `firby-chat.py` (588 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `asyncio, json, os, re, sys, time, readline, pathlib.Path`

### `instances/clinica-de-las-americas/firby-chat.py` (588 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `asyncio, json, os, re, sys, time, readline, pathlib.Path`

### `demo/firby-chat.py` (579 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `asyncio, json, os, re, sys, time, readline, pathlib.Path`

### `tests/test_omnichannel_v10.py` (578 líneas)
- **Clases (4):** DummyRuntime, Config, MockResponse, DummyRuntime
- **Funciones:** 6
- **Imports:** `pytest, json, unittest.mock.AsyncMock, unittest.mock.patch, src.firby.channels.telegram.TelegramAdapter, src.firby.channels.slack.SlackAdapter, src.firby.channels.base.NormalizedMessage, src.firby.brain.database.DatabaseManager`

### `landing/generate_landing_v9.py` (560 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `firby_core/prompt_ops.py` (559 líneas)
- **Clases (1):** PromptBuilderDeps
- **Funciones:** 6
- **Imports:** `__future__.annotations, re, dataclasses.dataclass, datetime.datetime, typing.Any, typing.Callable, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/firby_core/prompt_ops.py` (559 líneas)
- **Clases (1):** PromptBuilderDeps
- **Funciones:** 6
- **Imports:** `__future__.annotations, re, dataclasses.dataclass, datetime.datetime, typing.Any, typing.Callable, typing.Dict, typing.List`

### `landing/generate_landing_v10.py` (551 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `src/firby/production/guard.py` (550 líneas)
- **Clases (1):** SendGuard
- **Funciones:** 19
- **Imports:** `__future__.annotations, logging, re, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional`

### `firby_session.py` (516 líneas)
- **Clases (3):** Config, DatabaseBackedDict, SessionManager
- **Funciones:** 35
- **Imports:** `__future__.annotations, time, typing.Any, typing.Dict, typing.List, typing.Optional, typing.Tuple, firby_config.Config`

### `instances/clinica-de-las-americas/firby_session.py` (516 líneas)
- **Clases (3):** Config, DatabaseBackedDict, SessionManager
- **Funciones:** 35
- **Imports:** `__future__.annotations, time, typing.Any, typing.Dict, typing.List, typing.Optional, typing.Tuple, firby_config.Config`

### `src/firby/integrations/search.py` (513 líneas)
- **Clases (1):** WebSearchEngine
- **Funciones:** 10
- **Imports:** `__future__.annotations, os, re, json, logging, random, typing.List, typing.Dict`

### `nova_bridge.py` (509 líneas)
- **Clases (2):** NovaClient, FirbyGuard
- **Funciones:** 10
- **Imports:** `__future__.annotations, asyncio, json, logging, os, re, time, typing.Dict`

### `instances/clinica-de-las-americas/nova_bridge.py` (509 líneas)
- **Clases (2):** NovaClient, FirbyGuard
- **Funciones:** 10
- **Imports:** `__future__.annotations, asyncio, json, logging, os, re, time, typing.Dict`

### `firby_tui.py` (502 líneas)
- **Clases (1):** Instance
- **Funciones:** 15
- **Imports:** `curses, os, sys, json, subprocess, time, shutil, pathlib.Path`

### `firby_nuke_robot_phrases.py` (495 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 13
- **Imports:** `__future__.annotations, functools.lru_cache, logging, re, sys, typing.Any, typing.Iterable, typing.Tuple`

### `instances/clinica-de-las-americas/firby_nuke_robot_phrases.py` (495 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 13
- **Imports:** `__future__.annotations, functools.lru_cache, logging, re, sys, typing.Any, typing.Iterable, typing.Tuple`

### `src/infrastructure/llm_providers/engine.py` (487 líneas)
- **Clases (6):** LLMProvider, GroqProvider, GeminiProvider, OpenRouterProvider, OpenAIProvider, LLMEngine
- **Funciones:** 17
- **Imports:** `json, time, httpx, hashlib, re, logging, typing.List, typing.Dict`

### `firby_pitch_upgrade.py` (471 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 10
- **Imports:** `__future__.annotations, logging, re, sys, typing.Any, typing.Dict, typing.List, typing.Optional`

### `instances/clinica-de-las-americas/firby_pitch_upgrade.py` (471 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 10
- **Imports:** `__future__.annotations, logging, re, sys, typing.Any, typing.Dict, typing.List, typing.Optional`

### `search.py` (465 líneas)
- **Clases (1):** SearchEngine
- **Funciones:** 9
- **Imports:** `__future__.annotations, asyncio, hashlib, json, logging, os, re, time`

### `instances/clinica-de-las-americas/search.py` (465 líneas)
- **Clases (1):** SearchEngine
- **Funciones:** 9
- **Imports:** `__future__.annotations, asyncio, hashlib, json, logging, os, re, time`

### `firby_runtime_ops.py` (463 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 21
- **Imports:** `__future__.annotations, json, os, re, shutil, select, shlex, socket`

### `instances/clinica-de-las-americas/firby_runtime_ops.py` (463 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 21
- **Imports:** `__future__.annotations, json, os, re, shutil, select, shlex, socket`

### `firby_generator.py` (460 líneas)
- **Clases (2):** Config, GeneratorManager
- **Funciones:** 4
- **Imports:** `__future__.annotations, time, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `instances/clinica-de-las-americas/firby_generator.py` (460 líneas)
- **Clases (2):** Config, GeneratorManager
- **Funciones:** 4
- **Imports:** `__future__.annotations, time, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `src/firby/personas/generator.py` (447 líneas)
- **Clases (2):** Config, GeneratorManager
- **Funciones:** 4
- **Imports:** `__future__.annotations, time, typing.Any, typing.Callable, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `firby_cli_bb.py` (437 líneas)
- **Clases (1):** BBContext
- **Funciones:** 14
- **Imports:** `__future__.annotations, argparse, ast, json, os, shutil, sqlite3, subprocess`

### `firby_core/conversation_engine.py` (426 líneas)
- **Clases (2):** ConversationTurnResult, ConversationEngine
- **Funciones:** 18
- **Imports:** `__future__.annotations, dataclasses.dataclass, datetime.datetime, typing.Any, typing.Dict, typing.List, typing.Optional, persona_registry.PersonaProfile`

### `instances/clinica-de-las-americas/firby_core/conversation_engine.py` (426 líneas)
- **Clases (2):** ConversationTurnResult, ConversationEngine
- **Funciones:** 18
- **Imports:** `__future__.annotations, dataclasses.dataclass, datetime.datetime, typing.Any, typing.Dict, typing.List, typing.Optional, persona_registry.PersonaProfile`

### `landing/generate_landing_v11.py` (416 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `firby_redteam.py` (409 líneas)
- **Clases (2):** RedTeamAuditor, RedTeamEngine
- **Funciones:** 2
- **Imports:** `__future__.annotations, asyncio, json, logging, os, re, sys, time`

### `instances/clinica-de-las-americas/firby_redteam.py` (409 líneas)
- **Clases (2):** RedTeamAuditor, RedTeamEngine
- **Funciones:** 2
- **Imports:** `__future__.annotations, asyncio, json, logging, os, re, sys, time`

### `src/firby/brain/filters.py` (370 líneas)
- **Clases (1):** AntiRobotFilter
- **Funciones:** 8
- **Imports:** `__future__.annotations, logging, re, typing.List, src.firby.core.proxy.GlobalProxy`

### `src/firby/channels/onboarding.py` (368 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, re, json, logging, httpx, typing.Dict, typing.Any, typing.Optional`

### `src/firby/integrations/calendar.py` (359 líneas)
- **Clases (1):** CalendarBridge
- **Funciones:** 8
- **Imports:** `__future__.annotations, time, logging, datetime.datetime, datetime.timedelta, typing.List, typing.Dict, typing.Tuple`

### `src/firby/production/monitor.py` (357 líneas)
- **Clases (1):** FirbyProduction
- **Funciones:** 1
- **Imports:** `__future__.annotations, logging, time, typing.Any, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `firby_audio.py` (350 líneas)
- **Clases (2):** Config, AudioHandler
- **Funciones:** 3
- **Imports:** `__future__.annotations, base64, os, tempfile, typing.Optional, typing.Tuple, httpx, firby_config.Config`

### `instances/clinica-de-las-americas/firby_audio.py` (350 líneas)
- **Clases (2):** Config, AudioHandler
- **Funciones:** 3
- **Imports:** `__future__.annotations, base64, os, tempfile, typing.Optional, typing.Tuple, httpx, firby_config.Config`

### `src/firby/core/tasks.py` (341 líneas)
- **Clases (1):** TaskManager
- **Funciones:** 5
- **Imports:** `__future__.annotations, asyncio, logging, uuid, datetime.datetime, typing.Dict, typing.Any, typing.Callable`

### `firby_smart_features.py` (337 líneas)
- **Clases (7):** CrossSessionMemory, FollowUpEngine, SentimentTracker, PredictiveIntent, WeeklyStats, AdminShadowMode, LanguageDetector
- **Funciones:** 24
- **Imports:** `__future__.annotations, json, logging, re, time, datetime.datetime, datetime.timedelta, pathlib.Path`

### `src/firby/brain/smart_features.py` (337 líneas)
- **Clases (7):** CrossSessionMemory, FollowUpEngine, SentimentTracker, PredictiveIntent, WeeklyStats, AdminShadowMode, LanguageDetector
- **Funciones:** 24
- **Imports:** `__future__.annotations, json, logging, re, time, datetime.datetime, datetime.timedelta, pathlib.Path`

### `instances/clinica-de-las-americas/firby_smart_features.py` (337 líneas)
- **Clases (7):** CrossSessionMemory, FollowUpEngine, SentimentTracker, PredictiveIntent, WeeklyStats, AdminShadowMode, LanguageDetector
- **Funciones:** 24
- **Imports:** `__future__.annotations, json, logging, re, time, datetime.datetime, datetime.timedelta, pathlib.Path`

### `src/firby/plugins/mcp.py` (331 líneas)
- **Clases (5):** MCPCapability, MCPPluginBase, CalendarPlugin, NotificationsPlugin, MCPManager
- **Funciones:** 11
- **Imports:** `__future__.annotations, logging, uuid, httpx, abc.ABC, abc.abstractmethod, enum.Enum, datetime.datetime`

### `src/firby/admin/commands.py` (331 líneas)
- **Clases (1):** CommandHandler
- **Funciones:** 4
- **Imports:** `__future__.annotations, json, logging, re, time, pathlib.Path, typing.Any, typing.Dict`

### `knowledge_base.py` (330 líneas)
- **Clases (1):** KnowledgeBase
- **Funciones:** 16
- **Imports:** `__future__.annotations, json, logging, re, sqlite3, datetime.datetime, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/knowledge_base.py` (330 líneas)
- **Clases (1):** KnowledgeBase
- **Funciones:** 16
- **Imports:** `__future__.annotations, json, logging, re, sqlite3, datetime.datetime, typing.Dict, typing.List`

### `tests/test_production_monitor_wiring.py` (328 líneas)
- **Clases (12):** FakeDB, FakeLLM, FakeAnalyzer, FakeReasoning, FakeGenerator, FakeRuntime, FakeMemory, FakeSentiment, FakeLanguage, FakeLearning, FakeUncertainty, MockLearning
- **Funciones:** 25
- **Imports:** `asyncio, sys, types, pathlib.Path, src.core.globals, src.core.globals, src.core.production_monitor.FirbyProduction, src.core.production_monitor.FirbyProduction`

### `src/firby/brain/memory.py` (324 líneas)
- **Clases (2):** AgentDB, FirbyMemoryEngine
- **Funciones:** 7
- **Imports:** `__future__.annotations, hashlib, json, logging, re, time, datetime.datetime, datetime.timedelta`

### `brand_assets.py` (323 líneas)
- **Clases (2):** SavedBrandAsset, BrandAssetStore
- **Funciones:** 18
- **Imports:** `__future__.annotations, hashlib, io, json, mimetypes, re, zipfile, dataclasses.dataclass`

### `instances/clinica-de-las-americas/brand_assets.py` (323 líneas)
- **Clases (2):** SavedBrandAsset, BrandAssetStore
- **Funciones:** 18
- **Imports:** `__future__.annotations, hashlib, io, json, mimetypes, re, zipfile, dataclasses.dataclass`

### `scripts/patches/rewrite_settings_page.py` (317 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/channels/audio.py` (316 líneas)
- **Clases (1):** AudioHandler
- **Funciones:** 3
- **Imports:** `__future__.annotations, base64, logging, os, tempfile, typing.Optional, typing.Tuple, httpx`

### `src/firby/core/session.py` (312 líneas)
- **Clases (2):** _DefaultConfig, SessionManager
- **Funciones:** 19
- **Imports:** `__future__.annotations, time, typing.Any, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `src/firby/integrations/knowledge.py` (312 líneas)
- **Clases (1):** KnowledgeBase
- **Funciones:** 16
- **Imports:** `__future__.annotations, json, logging, re, sqlite3, typing.Dict, typing.List, typing.Tuple`

### `firby_app.py` (309 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 30
- **Imports:** `__future__.annotations, os, sys, time, json, subprocess, signal, random`

### `instances/clinica-de-las-americas/firby_app.py` (309 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 30
- **Imports:** `__future__.annotations, os, sys, time, json, subprocess, signal, random`

### `firby_patch.py` (297 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `sys, shutil, pathlib.Path, datetime.datetime`

### `src/firby/core/router.py` (297 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `__future__.annotations, logging, typing.Any, typing.Dict, typing.List, typing.Optional, firby_config.Config, firby_config.DEMO_CMD_ALIASES`

### `src/domain/prompts/prospect_pitch.py` (296 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `__future__.annotations, src.domain.prompts.human_writer.STYLE_GUIDELINES, logging, re, typing.Any, typing.Dict, typing.List, typing.Optional`

### `firby_memory_engine.py` (292 líneas)
- **Clases (1):** FirbyMemoryEngine
- **Funciones:** 3
- **Imports:** `__future__.annotations, hashlib, json, logging, re, time, datetime.datetime, datetime.timedelta`

### `instances/clinica-de-las-americas/firby_memory_engine.py` (292 líneas)
- **Clases (1):** FirbyMemoryEngine
- **Funciones:** 3
- **Imports:** `__future__.annotations, hashlib, json, logging, re, time, datetime.datetime, datetime.timedelta`

### `firby_core/first_turn_ops.py` (288 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 14
- **Imports:** `__future__.annotations, re, typing.Any, typing.Callable, typing.Dict, typing.Optional`

### `instances/clinica-de-las-americas/firby_core/first_turn_ops.py` (288 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 14
- **Imports:** `__future__.annotations, re, typing.Any, typing.Callable, typing.Dict, typing.Optional`

### `tests/test_sync_runtime.py` (280 líneas)
- **Clases (1):** DummySpinner
- **Funciones:** 13
- **Imports:** `pathlib.Path, types.SimpleNamespace, json, sqlite3, sys, firby_cli, firby_cli_runtime`

### `src/firby/channels/whatsapp.py` (278 líneas)
- **Clases (1):** WhatsAppConnector
- **Funciones:** 2
- **Imports:** `__future__.annotations, logging, os, re, typing.Dict, typing.Any, typing.Optional, httpx`

### `v7/orchestrator.py` (275 líneas)
- **Clases (1):** FirbyOrchestrator
- **Funciones:** 4
- **Imports:** `__future__.annotations, asyncio, logging, time, typing.Dict, typing.List, typing.Optional, typing.Any`

### `instances/clinica-de-las-americas/v7/orchestrator.py` (275 líneas)
- **Clases (1):** FirbyOrchestrator
- **Funciones:** 4
- **Imports:** `__future__.annotations, asyncio, logging, time, typing.Dict, typing.List, typing.Optional, typing.Any`

### `src/core/orchestrator.py` (273 líneas)
- **Clases (1):** FirbyOrchestrator
- **Funciones:** 4
- **Imports:** `__future__.annotations, asyncio, logging, time, typing.Dict, typing.List, typing.Optional, typing.Any`

### `src/firby/utils/helpers.py` (268 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 15
- **Imports:** `__future__.annotations, hashlib, json, logging, secrets, re, typing.Any, typing.Dict`

### `firby_memory.py` (267 líneas)
- **Clases (1):** FirbyMemory
- **Funciones:** 16
- **Imports:** `__future__.annotations, json, logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/firby_memory.py` (267 líneas)
- **Clases (1):** FirbyMemory
- **Funciones:** 16
- **Imports:** `__future__.annotations, json, logging, datetime.datetime, pathlib.Path, typing.Any, typing.Dict, typing.List`

### `tests/test_search_and_llm_runtime.py` (263 líneas)
- **Clases (9):** _Response, _Client, _Response, _Client, _Response, _Client, _Provider, _Error, _Error
- **Funciones:** 20
- **Imports:** `asyncio, importlib.util, sys, time, types, uuid, pathlib.Path`

### `firby_pairing.py` (253 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 14
- **Imports:** `os, json, time, secrets, re, typing.List, typing.Dict, typing.Optional`

### `src/domain/onboarding_flow.py` (253 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `__future__.annotations, json, logging, re, typing.Any, typing.Dict, typing.List, typing.Optional`

### `firby_demo_voice.py` (249 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 6
- **Imports:** `__future__.annotations, asyncio, logging, os, tempfile, typing.List, typing.Optional, typing.Tuple`

### `instances/clinica-de-las-americas/firby_demo_voice.py` (249 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 6
- **Imports:** `__future__.annotations, asyncio, logging, os, tempfile, typing.List, typing.Optional, typing.Tuple`

### `src/firby/core/config.py` (248 líneas)
- **Clases (1):** Config
- **Funciones:** 3
- **Imports:** `__future__.annotations, json, os, re, pathlib.Path, typing.Dict, typing.List, typing.Any`

### `scripts/patches/rewrite_sidebar2.py` (244 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/router.py` (239 líneas)
- **Clases (3):** AgentID, RouterResult, IntentRouter
- **Funciones:** 4
- **Imports:** `__future__.annotations, re, time, logging, dataclasses.dataclass, dataclasses.field, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/v7/router.py` (239 líneas)
- **Clases (3):** AgentID, RouterResult, IntentRouter
- **Funciones:** 4
- **Imports:** `__future__.annotations, re, time, logging, dataclasses.dataclass, dataclasses.field, typing.Dict, typing.List`

### `scripts/patches/patch_beta_flow.py` (238 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `firby_config.py` (237 líneas)
- **Clases (1):** Config
- **Funciones:** 1
- **Imports:** `__future__.annotations, os, pathlib.Path, typing.Dict, typing.List, typing.Set, typing.Tuple, dotenv.load_dotenv`

### `instances/clinica-de-las-americas/firby_config.py` (237 líneas)
- **Clases (1):** Config
- **Funciones:** 1
- **Imports:** `__future__.annotations, os, pathlib.Path, typing.Dict, typing.List, typing.Set, typing.Tuple, dotenv.load_dotenv`

### `src/firby/admin/api.py` (234 líneas)
- **Clases (3):** PersonaUpdate, ModelUpdate, TeachRequest
- **Funciones:** 3
- **Imports:** `json, os, logging, pathlib.Path, datetime.datetime, typing.List, typing.Optional, fastapi.APIRouter`

### `firby_doctor.py` (227 líneas)
- **Clases (2):** HealthCheck, FirbyDoctor
- **Funciones:** 12
- **Imports:** `asyncio, json, os, subprocess, sys, time, pathlib.Path, datetime.datetime`

### `instances/clinica-de-las-americas/firby_doctor.py` (227 líneas)
- **Clases (2):** HealthCheck, FirbyDoctor
- **Funciones:** 12
- **Imports:** `asyncio, json, os, subprocess, sys, time, pathlib.Path, datetime.datetime`

### `scripts/build_settings_page.py` (224 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/rewrite_sidebar.py` (222 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/agents/base.py` (216 líneas)
- **Clases (3):** AgentContext, AgentResponse, AgentBase
- **Funciones:** 16
- **Imports:** `__future__.annotations, logging, time, abc.ABC, abc.abstractmethod, dataclasses.dataclass, dataclasses.field, typing.Dict`

### `instances/clinica-de-las-americas/v7/agents/base.py` (216 líneas)
- **Clases (3):** AgentContext, AgentResponse, AgentBase
- **Funciones:** 16
- **Imports:** `__future__.annotations, logging, time, abc.ABC, abc.abstractmethod, dataclasses.dataclass, dataclasses.field, typing.Dict`

### `firby_demo_v2.py` (209 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `__future__.annotations, asyncio, json, os, random, sys, time, pathlib.Path`

### `demo/firby_demo_v2.py` (209 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `__future__.annotations, asyncio, json, os, random, sys, time, pathlib.Path`

### `src/core/vision_handler.py` (209 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `base64, logging, httpx, typing.Dict, typing.Optional, src.core.globals.Config`

### `instances/clinica-de-las-americas/firby_demo_v2.py` (209 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `__future__.annotations, asyncio, json, os, random, sys, time, pathlib.Path`

### `tests/test_vision_diagnosis.py` (205 líneas)
- **Clases (1):** TestVisionDiagnosis
- **Funciones:** 0
- **Imports:** `sys, unittest, base64, json, unittest.mock.AsyncMock, unittest.mock.MagicMock, unittest.mock.patch, pathlib.Path`

### `tests/test_demo_greeting_loop.py` (205 líneas)
- **Clases (1):** TestDemoGreetingLoop
- **Funciones:** 0
- **Imports:** `asyncio, sys, unittest, unittest.mock.AsyncMock, unittest.mock.MagicMock, unittest.mock.patch, pathlib.Path, firby`

### `tests/test_smart_handoff.py` (203 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `asyncio, json, sqlite3, sys, time, pathlib.Path, src.firby.production.handoff`

### `src/firby/admin/clone_manager.py` (203 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, os, re, json, shutil, secrets, sqlite3, logging`

### `v7/memory/patient_profile.py` (200 líneas)
- **Clases (3):** FunnelStage, PatientProfile, ProfileStore
- **Funciones:** 11
- **Imports:** `__future__.annotations, json, time, logging, dataclasses.dataclass, dataclasses.field, dataclasses.asdict, typing.Dict`

### `instances/clinica-de-las-americas/v7/memory/patient_profile.py` (200 líneas)
- **Clases (3):** FunnelStage, PatientProfile, ProfileStore
- **Funciones:** 11
- **Imports:** `__future__.annotations, json, time, logging, dataclasses.dataclass, dataclasses.field, dataclasses.asdict, typing.Dict`

### `firby_learner.py` (196 líneas)
- **Clases (1):** FirbyLearner
- **Funciones:** 7
- **Imports:** `__future__.annotations, json, os, logging, datetime.datetime, pathlib.Path, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/firby_learner.py` (196 líneas)
- **Clases (1):** FirbyLearner
- **Funciones:** 7
- **Imports:** `__future__.annotations, json, os, logging, datetime.datetime, pathlib.Path, typing.Dict, typing.List`

### `tests/test_payment_integration.py` (184 líneas)
- **Clases (1):** TestPaymentIntegration
- **Funciones:** 1
- **Imports:** `asyncio, sys, json, unittest, unittest.mock.AsyncMock, unittest.mock.MagicMock, unittest.mock.patch, pathlib.Path`

### `firby_tui_select.py` (180 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 8
- **Imports:** `__future__.annotations, os, sys, shutil, select, typing.List, typing.Optional, termios`

### `instances/clinica-de-las-americas/firby_tui_select.py` (180 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 8
- **Imports:** `__future__.annotations, os, sys, shutil, select, typing.List, typing.Optional, termios`

### `src/firby/core/models.py` (175 líneas)
- **Clases (9):** IntentType, SentimentType, UrgencyLevel, MessageAnalysis, ConversationState, MemoryItem, Task, MCPPlugin, PersonalityProfile
- **Funciones:** 0
- **Imports:** `__future__.annotations, dataclasses.dataclass, dataclasses.field, datetime.datetime, enum.Enum, enum.auto, typing.Any, typing.Dict`

### `firby_uncertainty.py` (174 líneas)
- **Clases (1):** UncertaintyDetector
- **Funciones:** 3
- **Imports:** `re, json, logging, asyncio, time, pathlib.Path, typing.Optional, datetime.datetime`

### `instances/clinica-de-las-americas/firby_uncertainty.py` (174 líneas)
- **Clases (1):** UncertaintyDetector
- **Funciones:** 3
- **Imports:** `re, json, logging, asyncio, time, pathlib.Path, typing.Optional, datetime.datetime`

### `scripts/patches/patch_onboarding.py` (173 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `src/firby/integrations/notion.py` (172 líneas)
- **Clases (1):** NotionClient
- **Funciones:** 1
- **Imports:** `__future__.annotations, logging, httpx, typing.Dict, typing.Any, typing.List, typing.Optional, src.core.globals`

### `firby_nova_proxy.py` (170 líneas)
- **Clases (1):** NovaLLMProxy
- **Funciones:** 3
- **Imports:** `__future__.annotations, logging, time, typing.Any, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `instances/clinica-de-las-americas/firby_nova_proxy.py` (170 líneas)
- **Clases (1):** NovaLLMProxy
- **Funciones:** 3
- **Imports:** `__future__.annotations, logging, time, typing.Any, typing.Dict, typing.List, typing.Optional, typing.Tuple`

### `firby_core/api_awareness.py` (169 líneas)
- **Clases (1):** APICapabilityMap
- **Funciones:** 10
- **Imports:** `__future__.annotations, os, logging, typing.Dict, typing.List, typing.Tuple, typing.Optional, random`

### `instances/clinica-de-las-americas/firby_core/api_awareness.py` (169 líneas)
- **Clases (1):** APICapabilityMap
- **Funciones:** 10
- **Imports:** `__future__.annotations, os, logging, typing.Dict, typing.List, typing.Tuple, typing.Optional, random`

### `src/interfaces/web/demo_admin_commands.py` (168 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `__future__.annotations, logging, re, json, typing.Any, typing.Dict, typing.List, typing.Optional`

### `src/firby/brain/uncertainty.py` (167 líneas)
- **Clases (1):** UncertaintyDetector
- **Funciones:** 3
- **Imports:** `re, json, logging, pathlib.Path, datetime.datetime, typing.Optional`

### `scripts/add_backend_endpoints.py` (165 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scratch/audit_migration.py` (165 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `os, ast`

### `firby.py` (163 líneas)
- **Clases (1):** FacadeProxy
- **Funciones:** 2
- **Imports:** `__future__.annotations, sys, os, logging, src.core.globals, src.core.runtime, src.interfaces.web.app, src.core.globals`

### `instances/clinica-de-las-americas/firby.py` (163 líneas)
- **Clases (1):** FacadeProxy
- **Funciones:** 2
- **Imports:** `__future__.annotations, sys, os, logging, src.core.globals, src.core.runtime, src.interfaces.web.app, src.core.globals`

### `firby_direct.py` (162 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `asyncio, httpx, sys, time`

### `instances/clinica-de-las-americas/firby_direct.py` (162 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `asyncio, httpx, sys, time`

### `firby_studio.py` (161 líneas)
- **Clases (1):** FirbyStudio
- **Funciones:** 5
- **Imports:** `asyncio, json, os, sys, time, uuid, pathlib.Path, datetime.datetime`

### `instances/clinica-de-las-americas/firby_studio.py` (161 líneas)
- **Clases (1):** FirbyStudio
- **Funciones:** 5
- **Imports:** `asyncio, json, os, sys, time, uuid, pathlib.Path, datetime.datetime`

### `scripts/patches/rewrite_instances.py` (160 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `firby_google_auth.py` (159 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `__future__.annotations, json, logging, os, pathlib.Path, typing.Dict, typing.Optional, urllib.parse.urlencode`

### `scripts/patches/fix_caddy.py` (159 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `instances/clinica-de-las-americas/firby_google_auth.py` (159 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `__future__.annotations, json, logging, os, pathlib.Path, typing.Dict, typing.Optional, urllib.parse.urlencode`

### `firby_core/persona_registry.py` (157 líneas)
- **Clases (2):** PersonaProfile, PersonaRegistry
- **Funciones:** 11
- **Imports:** `__future__.annotations, dataclasses.dataclass, dataclasses.field, pathlib.Path, typing.Any, typing.Dict, typing.Iterable, typing.List`

### `instances/clinica-de-las-americas/firby_core/persona_registry.py` (157 líneas)
- **Clases (2):** PersonaProfile, PersonaRegistry
- **Funciones:** 11
- **Imports:** `__future__.annotations, dataclasses.dataclass, dataclasses.field, pathlib.Path, typing.Any, typing.Dict, typing.Iterable, typing.List`

### `firby_voice.py` (156 líneas)
- **Clases (1):** FirbyVoice
- **Funciones:** 6
- **Imports:** `__future__.annotations, re, random, logging, typing.Optional, typing.Dict, typing.List`

### `src/firby/channels/voice.py` (156 líneas)
- **Clases (1):** FirbyVoice
- **Funciones:** 6
- **Imports:** `__future__.annotations, re, random, logging, typing.Optional, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/firby_voice.py` (156 líneas)
- **Clases (1):** FirbyVoice
- **Funciones:** 6
- **Imports:** `__future__.annotations, re, random, logging, typing.Optional, typing.Dict, typing.List`

### `firby_learning.py` (154 líneas)
- **Clases (1):** RealTimeLearningEngine
- **Funciones:** 4
- **Imports:** `__future__.annotations, hashlib, json, logging, time, datetime.datetime, pathlib.Path, typing.Any`

### `src/firby/brain/learning.py` (154 líneas)
- **Clases (1):** RealTimeLearningEngine
- **Funciones:** 4
- **Imports:** `__future__.annotations, hashlib, json, logging, time, datetime.datetime, pathlib.Path, typing.Any`

### `instances/clinica-de-las-americas/firby_learning.py` (154 líneas)
- **Clases (1):** RealTimeLearningEngine
- **Funciones:** 4
- **Imports:** `__future__.annotations, hashlib, json, logging, time, datetime.datetime, pathlib.Path, typing.Any`

### `firby_persona_cli.py` (150 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 10
- **Imports:** `argparse, json, os, sys, pathlib.Path, datetime.datetime, httpx`

### `tests/test_admin_natural_triggers.py` (150 líneas)
- **Clases (1):** DummyRuntime
- **Funciones:** 1
- **Imports:** `pytest, json, unittest.mock.MagicMock, unittest.mock.AsyncMock, unittest.mock.patch, src.firby.admin.dashboard.AdminCommandsMixin`

### `instances/clinica-de-las-americas/firby_persona_cli.py` (150 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 10
- **Imports:** `argparse, json, os, sys, pathlib.Path, datetime.datetime, httpx`

### `src/domain/swarm/queen.py` (149 líneas)
- **Clases (2):** Agent, QueenCoordinator
- **Funciones:** 3
- **Imports:** `asyncio, logging, typing.Dict, typing.Any, typing.List, typing.Optional, src.core.globals.llm_engine, json`

### `firby_code_graph.py` (146 líneas)
- **Clases (1):** CodebaseAnalyzer
- **Funciones:** 8
- **Imports:** `ast, json, os, sys, pathlib.Path, typing.Dict, typing.List, typing.Set`

### `tests/test_nps_flow.py` (145 líneas)
- **Clases (1):** TestNPSFlow
- **Funciones:** 0
- **Imports:** `asyncio, sys, unittest, unittest.mock.AsyncMock, unittest.mock.MagicMock, unittest.mock.patch, datetime.datetime, datetime.timedelta`

### `src/firby/core/tenant.py` (145 líneas)
- **Clases (2):** TenantConfig, TenantRegistry
- **Funciones:** 10
- **Imports:** `__future__.annotations, os, sqlite3, dataclasses.dataclass, dataclasses.field, pathlib.Path, typing.Any, typing.Dict`

### `firby_cron.py` (140 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, logging, asyncio, apscheduler.schedulers.asyncio.AsyncIOScheduler, apscheduler.triggers.cron.CronTrigger, firby_weekly_report.generate_weekly_report, datetime.datetime, datetime.timedelta`

### `instances/clinica-de-las-americas/firby_cron.py` (140 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, logging, asyncio, apscheduler.schedulers.asyncio.AsyncIOScheduler, apscheduler.triggers.cron.CronTrigger, firby_weekly_report.generate_weekly_report, datetime.datetime, datetime.timedelta`

### `scripts/patches/patch_dev_ai_chat.py` (139 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/replace_dev_chat.py` (137 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_firby_bridge.py` (135 líneas)
- **Clases (1):** FakeTransport
- **Funciones:** 7
- **Imports:** `pathlib.Path, json, sqlite3, sys, firby_bridge`

### `demo/firby_demo_voice.py` (134 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `__future__.annotations, asyncio, logging, os, tempfile, typing.List, typing.Optional, typing.Tuple`

### `tests/test_activation_gate.py` (133 líneas)
- **Clases (2):** FakeDB, FakeDB
- **Funciones:** 17
- **Imports:** `asyncio, importlib.util, sys, types, uuid, pathlib.Path, src.firby.utils.helpers.generate_admin_activation_token, src.core.admin_engines.AuthEngine`

### `scripts/build_analytics_page.py` (131 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `v7/postprocess.py` (127 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `__future__.annotations, re, unicodedata, typing.List`

### `instances/clinica-de-las-americas/v7/postprocess.py` (127 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `__future__.annotations, re, unicodedata, typing.List`

### `firby_voice_engine.py` (124 líneas)
- **Clases (1):** FirbyVoiceEngine
- **Funciones:** 3
- **Imports:** `__future__.annotations, asyncio, logging, os, tempfile, typing.Dict, typing.List, typing.Optional`

### `src/firby/core/proxy.py` (124 líneas)
- **Clases (2):** GlobalProxy, DynamicGlobalProxy
- **Funciones:** 22
- **Imports:** `__future__.annotations, src.core.globals, src.core.globals, sys`

### `instances/clinica-de-las-americas/firby_voice_engine.py` (124 líneas)
- **Clases (1):** FirbyVoiceEngine
- **Funciones:** 3
- **Imports:** `__future__.annotations, asyncio, logging, os, tempfile, typing.Dict, typing.List, typing.Optional`

### `src/firby/brain/infinite_memory.py` (123 líneas)
- **Clases (2):** AdminTeachingRule, InfiniteMemoryEngine
- **Funciones:** 11
- **Imports:** `time, json, logging, typing.Dict, typing.List, typing.Any, typing.Optional, pathlib.Path`

### `scripts/audit_agents.py` (117 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `__future__.annotations, json, sys, pathlib.Path`

### `src/firby/integrations/payments.py` (115 líneas)
- **Clases (1):** PaymentBridge
- **Funciones:** 3
- **Imports:** `__future__.annotations, logging, os, json, httpx, src.firby.core.proxy.GlobalProxy`

### `firby_core/evolution.py` (112 líneas)
- **Clases (1):** EvolutionManager
- **Funciones:** 1
- **Imports:** `__future__.annotations, os, re, json, logging, datetime.datetime, pathlib.Path, typing.Any`

### `instances/clinica-de-las-americas/firby_core/evolution.py` (112 líneas)
- **Clases (1):** EvolutionManager
- **Funciones:** 1
- **Imports:** `__future__.annotations, os, re, json, logging, datetime.datetime, pathlib.Path, typing.Any`

### `scripts/patches/update_instances_settings.py` (109 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/agents/objeciones.py` (109 líneas)
- **Clases (1):** AgenteObjeciones
- **Funciones:** 3
- **Imports:** `__future__.annotations, re, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `instances/clinica-de-las-americas/v7/agents/objeciones.py` (109 líneas)
- **Clases (1):** AgenteObjeciones
- **Funciones:** 3
- **Imports:** `__future__.annotations, re, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `scripts/patches/rewrite_documents.py` (108 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/update_sidebar.py` (107 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `landing/update_buttons_and_gsap.py` (106 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_app.py` (106 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_greetings.py` (105 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_login_css.py` (103 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_google_calendar_booking.py` (100 líneas)
- **Clases (1):** TestGoogleCalendarBooking
- **Funciones:** 0
- **Imports:** `asyncio, sys, unittest, unittest.mock.AsyncMock, unittest.mock.MagicMock, unittest.mock.patch, pathlib.Path, datetime.datetime`

### `tests/test_runtime_ops.py` (98 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `pathlib.Path, os, sys, firby_runtime_ops`

### `src/domain/prompts/human_writer.py` (98 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/brain/psychology.py` (98 líneas)
- **Clases (1):** LatAmPsychologyEngine
- **Funciones:** 5
- **Imports:** `re, logging, typing.Dict, typing.Any`

### `tests/test_terminal_capabilities.py` (96 líneas)
- **Clases (1):** DummyRuntime
- **Funciones:** 1
- **Imports:** `pytest, unittest.mock.MagicMock, unittest.mock.AsyncMock, unittest.mock.patch, src.firby.admin.dashboard.AdminCommandsMixin, src.core.ovni_handler._detect_quick_command, src.firby.core.tasks.task_manager, src.firby.core.models.Task`

### `scripts/audit_runtime_cleanliness.py` (93 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, json, re, sys, pathlib.Path`

### `firby_web_search.py` (91 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations, logging, os, typing.List, typing.Dict, typing.Optional, httpx, search.apify_search`

### `instances/clinica-de-las-americas/firby_web_search.py` (91 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations, logging, os, typing.List, typing.Dict, typing.Optional, httpx, search.apify_search`

### `tests/test_nova_proxy.py` (90 líneas)
- **Clases (3):** MockLLM, MockGuard, MockBlockingGuard
- **Funciones:** 6
- **Imports:** `sys, asyncio, firby_nova_proxy.NovaLLMProxy`

### `scripts/patches/refactor.py` (89 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `firby_worm.py` (88 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, math, sys, time`

### `tools/firby_worm.py` (88 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, math, sys, time`

### `scripts/patches/patch_dashboard_greeting.py` (88 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `instances/clinica-de-las-americas/firby_worm.py` (88 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, math, sys, time`

### `src/firby/channels/telegram.py` (87 líneas)
- **Clases (1):** TelegramAdapter
- **Funciones:** 1
- **Imports:** `__future__.annotations, logging, httpx, typing.Dict, typing.Any, typing.Optional, typing.List, src.firby.channels.base.ChannelAdapterBase`

### `tests/test_admin_api.py` (86 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 6
- **Imports:** `sys, os, fastapi.testclient.TestClient, src.interfaces.web.admin_api.router, fastapi.FastAPI`

### `scripts/patches/fix_sdk_favicon.py` (86 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_sdk_final.py` (86 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_routes_instances.py` (86 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `firby_weekly_report.py` (85 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations, json, logging, sqlite3, datetime.datetime, datetime.timedelta, pathlib.Path, typing.Dict`

### `tools/firby_weekly_report.py` (85 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations, json, logging, sqlite3, datetime.datetime, datetime.timedelta, pathlib.Path, typing.Dict`

### `instances/clinica-de-las-americas/firby_weekly_report.py` (85 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations, json, logging, sqlite3, datetime.datetime, datetime.timedelta, pathlib.Path, typing.Dict`

### `tests/test_memory.py` (84 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `sys, asyncio, tempfile, shutil, firby_memory_engine.FirbyMemoryEngine, json, pathlib.Path`

### `v7/agents/escalacion.py` (83 líneas)
- **Clases (1):** AgenteEscalacion
- **Funciones:** 2
- **Imports:** `__future__.annotations, re, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `instances/clinica-de-las-americas/v7/agents/escalacion.py` (83 líneas)
- **Clases (1):** AgenteEscalacion
- **Funciones:** 2
- **Imports:** `__future__.annotations, re, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `scripts/patches/restore_onboarding.py` (82 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/add_dashboard_api.py` (81 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sqlite3`

### `tests/test_robot_phrase_boundaries.py` (81 líneas)
- **Clases (2):** DummyGenerator, DummyAntiRobot
- **Funciones:** 6
- **Imports:** `sys, types, uuid, pathlib.Path, pytest, firby_nuke_robot_phrases.apply_patch, firby_nuke_robot_phrases.strip_robot_phrases, src.domain.send_guard.guard_response`

### `src/domain/demo_prompts.py` (81 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/admin/ovni_god_engine.py` (81 líneas)
- **Clases (2):** OvniSecuritySandboxError, OvniGodEngine
- **Funciones:** 4
- **Imports:** `os, sys, logging, pathlib.Path, typing.Dict, typing.Any, typing.List`

### `src/firby/channels/slack.py` (81 líneas)
- **Clases (1):** SlackAdapter
- **Funciones:** 1
- **Imports:** `__future__.annotations, logging, httpx, typing.Dict, typing.Any, typing.Optional, typing.List, src.firby.channels.base.ChannelAdapterBase`

### `scripts/patches/patch_js_opacity.py` (80 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `src/firby/admin/dev_chat.py` (79 líneas)
- **Clases (1):** ChatRequest
- **Funciones:** 0
- **Imports:** `subprocess, fastapi.APIRouter, fastapi.Request, fastapi.HTTPException, pydantic.BaseModel, src.core.globals.db, src.core.globals.llm_engine`

### `firby_integrations/vault.py` (77 líneas)
- **Clases (1):** IntegrationVault
- **Funciones:** 7
- **Imports:** `__future__.annotations, json, logging, os, pathlib.Path, typing.Any, typing.Dict, typing.Optional`

### `scripts/patches/patch_v12.py` (77 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/agents/agenda.py` (77 líneas)
- **Clases (1):** AgenteAgenda
- **Funciones:** 2
- **Imports:** `__future__.annotations, re, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `dev/react/fix_signin_react.py` (77 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `instances/clinica-de-las-americas/firby_integrations/vault.py` (77 líneas)
- **Clases (1):** IntegrationVault
- **Funciones:** 7
- **Imports:** `__future__.annotations, json, logging, os, pathlib.Path, typing.Any, typing.Dict, typing.Optional`

### `instances/clinica-de-las-americas/v7/agents/agenda.py` (77 líneas)
- **Clases (1):** AgenteAgenda
- **Funciones:** 2
- **Imports:** `__future__.annotations, re, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `chat_melissa.py` (76 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `requests, json, sys`

### `chat_firby.py` (76 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `requests, json, sys`

### `demo/chat_firby.py` (76 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `requests, json, sys`

### `instances/clinica-de-las-americas/chat_melissa.py` (76 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `requests, json, sys`

### `instances/clinica-de-las-americas/chat_firby.py` (76 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `requests, json, sys`

### `scratch/analyze_imports.py` (75 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `ast, sys, pathlib.Path`

### `src/firby/admin_memory.py` (75 líneas)
- **Clases (1):** AdminSoulMemory
- **Funciones:** 4
- **Imports:** `__future__.annotations, json, datetime.datetime, typing.Any, typing.Dict, typing.List, src.core.globals.db`

### `tools/firby_watchdog.py` (74 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `json, subprocess, sys, time, pathlib.Path, urllib.request.urlopen, urllib.request.Request`

### `scripts/patches/patch_hero_typography.py` (74 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_humanization.py` (73 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 8
- **Imports:** `sys, firby_voice.FirbyVoice, firby_voice.ROBOT_PATTERNS`

### `tests/test_demo_notion_auto_token.py` (73 líneas)
- **Clases (1):** TestDemoNotionAutoToken
- **Funciones:** 1
- **Imports:** `sys, unittest, unittest.mock.AsyncMock, unittest.mock.MagicMock, unittest.mock.patch, pathlib.Path, firby, src.firby.demo.handler.handle_demo_message`

### `src/interfaces/mcp_server.py` (73 líneas)
- **Clases (1):** MCPServer
- **Funciones:** 6
- **Imports:** `json, sys, logging, typing.Dict, typing.Any, src.interfaces.nova_bridge.nova_bridge`

### `tools/firby_cron.py` (72 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, logging, asyncio, apscheduler.schedulers.asyncio.AsyncIOScheduler, apscheduler.triggers.cron.CronTrigger, firby_weekly_report.generate_weekly_report`

### `scripts/patches/patch_prompts.py` (72 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `os`

### `src/firby/core/cron.py` (72 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, logging, asyncio, apscheduler.schedulers.asyncio.AsyncIOScheduler, apscheduler.triggers.cron.CronTrigger, firby_weekly_report.generate_weekly_report`

### `v7/agents/seguimiento.py` (71 líneas)
- **Clases (1):** AgenteSeguimiento
- **Funciones:** 2
- **Imports:** `__future__.annotations, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `instances/clinica-de-las-americas/v7/agents/seguimiento.py` (71 líneas)
- **Clases (1):** AgenteSeguimiento
- **Funciones:** 2
- **Imports:** `__future__.annotations, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `tests/test_infinite_memory_and_psychology.py` (70 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `pytest, src.firby.brain.InfiniteMemoryEngine, src.firby.brain.AdminTeachingRule, src.firby.brain.LatAmPsychologyEngine, src.firby.admin.ovni_god_engine.OvniGodEngine, src.firby.admin.ovni_god_engine.OvniSecuritySandboxError`

### `dev/react/fix_modern_sidebar.py` (70 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `firby_intelligence.py` (69 líneas)
- **Clases (8):** IntentType, SentimentType, UrgencyLevel, EmotionalMirrorEngine, ClientPersonaDetector, ResponseQualityPatcher, AntiRobotFilter, HyperHumanEngine
- **Funciones:** 5
- **Imports:** `__future__.annotations, logging, re, json, time, typing.Any, typing.Dict, typing.List`

### `tests/test_learning.py` (69 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `sys, asyncio, tempfile, shutil, firby_learning.RealTimeLearningEngine, firby_learning.RealTimeLearningEngine, firby_learning.RealTimeLearningEngine, firby_learning.RealTimeLearningEngine`

### `v7/agents/conocimiento.py` (69 líneas)
- **Clases (1):** AgenteConocimiento
- **Funciones:** 2
- **Imports:** `__future__.annotations, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `src/firby/admin/outreach.py` (69 líneas)
- **Clases (1):** AdminOutreachEngine
- **Funciones:** 5
- **Imports:** `re, time, logging, typing.Dict, typing.Any, typing.Optional`

### `instances/clinica-de-las-americas/firby_intelligence.py` (69 líneas)
- **Clases (8):** IntentType, SentimentType, UrgencyLevel, EmotionalMirrorEngine, ClientPersonaDetector, ResponseQualityPatcher, AntiRobotFilter, HyperHumanEngine
- **Funciones:** 5
- **Imports:** `__future__.annotations, logging, re, json, time, typing.Any, typing.Dict, typing.List`

### `instances/clinica-de-las-americas/v7/agents/conocimiento.py` (69 líneas)
- **Clases (1):** AgenteConocimiento
- **Funciones:** 2
- **Imports:** `__future__.annotations, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `scripts/patches/fix_sidebar_profile.py` (68 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_demo_sidebar_resize.py` (68 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_carbon.py` (67 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/add_documents_api.py` (66 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/setup_app.py` (66 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_snap.py` (66 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_section2.py` (66 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_sidebar_clean.py` (65 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_page_cards.py` (64 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_sidebar_profile2.py` (63 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_intro.py` (63 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `re`

### `tests/test_admin_outreach_system.py` (62 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `pytest, asyncio, src.firby.admin.outreach.AdminOutreachEngine, src.firby.channels.outreach_router.OmnichannelOutreachRouter, asyncio`

### `scripts/patches/fix_sidebar_logic.py` (62 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_nav_infinite.py` (62 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_sidebar_router.py` (61 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/agents/captacion.py` (61 líneas)
- **Clases (1):** AgenteCaptacion
- **Funciones:** 2
- **Imports:** `__future__.annotations, firby_core.identity_policy.compact_identity_rule, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `src/firby/brain/__init__.py` (61 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `uncertainty.UncertaintyDetector, uncertainty.uncertainty_detector, uncertainty.UNCERTAINTY_MARKERS_ES, uncertainty.UNCERTAINTY_MARKERS_EN, engine.init_brain, engine.patch_llm_first, llm_engine.LLMProvider, src.firby.core.proxy.GlobalProxy`

### `instances/clinica-de-las-americas/v7/agents/captacion.py` (61 líneas)
- **Clases (1):** AgenteCaptacion
- **Funciones:** 2
- **Imports:** `__future__.annotations, firby_core.identity_policy.compact_identity_rule, v7.agents.base.AgentBase, v7.agents.base.AgentContext, v7.agents.base.AgentResponse, v7.postprocess.postprocess, v7.postprocess.split_bubbles`

### `scripts/patches/patch_sidebar_final.py` (59 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/precise_fix.py` (59 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_sidebar_theme.py` (59 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_commands.py` (58 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 7
- **Imports:** `sys, asyncio, src.firby.admin.commands.CommandHandler, src.firby.admin.commands.CommandHandler, src.firby.admin.commands.CommandHandler, src.firby.admin.commands.CommandHandler, src.firby.admin.commands.CommandHandler, src.firby.admin.commands.CommandHandler`

### `src/interfaces/nova_bridge.py` (58 líneas)
- **Clases (1):** NovaGovernanceBridge
- **Funciones:** 3
- **Imports:** `json, logging, subprocess, typing.Dict, typing.Any`

### `tests/test_conversation.py` (57 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `asyncio, json, sys, os, firby, firby.Config, traceback`

### `scripts/patches/fix_settings_tokens.py` (57 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_telegram_webhook_mode.py` (56 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `importlib.util, sys, uuid, pathlib.Path`

### `scripts/mock_telegram.py` (55 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `urllib.request, json, logging, sys, uuid, time`

### `dev/react/fix_ai_chat_colors.py` (55 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `src/firby/channels/outreach_router.py` (55 líneas)
- **Clases (1):** OmnichannelOutreachRouter
- **Funciones:** 1
- **Imports:** `logging, typing.Dict, typing.Any, typing.Optional, src.firby.admin.outreach.AdminOutreachEngine, src.firby.brain.psychology.LatAmPsychologyEngine`

### `scripts/patches/fix_app_profile.py` (54 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/clean_panel.py` (53 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_demo_sidebar.py` (53 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_page_sidebar.py` (52 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_app_css.py` (51 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_sdk_editorial.py` (51 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_app_chart.py` (51 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sqlite3, re`

### `src/firby/channels/base.py` (51 líneas)
- **Clases (2):** NormalizedMessage, ChannelAdapterBase
- **Funciones:** 1
- **Imports:** `__future__.annotations, abc.ABC, abc.abstractmethod, dataclasses.dataclass, dataclasses.field, typing.Dict, typing.Any, typing.Optional`

### `scripts/patches/fix_nav.py` (50 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_imports.py` (50 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `scripts/patches/fix_dashboard_page.py` (50 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_mobile.py` (50 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_uncertainty.py` (49 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 5
- **Imports:** `sys, firby_uncertainty.UncertaintyDetector`

### `scripts/patches/fix_index_ui.py` (49 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_elevenlabs_and_brave_demo.py` (48 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `os, asyncio, pytest, dotenv.load_dotenv, src.firby.integrations.search.WebSearchEngine, firby_demo_voice.generate_demo_audio, firby_config.Config`

### `scripts/patches/patch_sidebar.py` (47 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_english.py` (47 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_table_avatars.py` (47 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/__init__.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, typing.TYPE_CHECKING, v7.agents.base.AgentBase, v7.agents.captacion.AgenteCaptacion, v7.agents.objeciones.AgenteObjeciones, v7.agents.agenda.AgenteAgenda`

### `scripts/patches/patch_mobile_and_js.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_translate.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `v7/agents/__init__.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, typing.TYPE_CHECKING, v7.agents.base.AgentBase, v7.agents.captacion.AgenteCaptacion, v7.agents.objeciones.AgenteObjeciones, v7.agents.agenda.AgenteAgenda`

### `v7/memory/__init__.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, typing.TYPE_CHECKING, v7.agents.base.AgentBase, v7.agents.captacion.AgenteCaptacion, v7.agents.objeciones.AgenteObjeciones, v7.agents.agenda.AgenteAgenda`

### `src/interfaces/web/static/generate_avatars.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `os, urllib.request, time`

### `instances/clinica-de-las-americas/v7/__init__.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, typing.TYPE_CHECKING, v7.agents.base.AgentBase, v7.agents.captacion.AgenteCaptacion, v7.agents.objeciones.AgenteObjeciones, v7.agents.agenda.AgenteAgenda`

### `instances/clinica-de-las-americas/v7/agents/__init__.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, typing.TYPE_CHECKING, v7.agents.base.AgentBase, v7.agents.captacion.AgenteCaptacion, v7.agents.objeciones.AgenteObjeciones, v7.agents.agenda.AgenteAgenda`

### `instances/clinica-de-las-americas/v7/memory/__init__.py` (46 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `__future__.annotations, typing.Dict, typing.Optional, typing.TYPE_CHECKING, v7.agents.base.AgentBase, v7.agents.captacion.AgenteCaptacion, v7.agents.objeciones.AgenteObjeciones, v7.agents.agenda.AgenteAgenda`

### `scripts/audit_static_branding.py` (45 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `__future__.annotations, json, pathlib.Path`

### `scripts/patches/patch_typography_final.py` (45 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_landing.py` (45 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `scripts/patches/fix_button.py` (45 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_brain_subsystem.py` (44 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `pytest, src.firby.brain.UncertaintyDetector, src.firby.brain.uncertainty_detector, src.firby.brain.ModelManager, src.firby.brain.LLMProvider, src.firby.brain.v8_process_response, src.firby.brain.AntiRobotFilter, src.firby.brain.EmotionalMirrorEngine`

### `scripts/patches/fix_app_js_clean.py` (44 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_app_logs.py` (44 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re, sqlite3`

### `firby_cli.py` (43 líneas)
- **Clases (1):** _CLIFacadeModule
- **Funciones:** 2
- **Imports:** `__future__.annotations, sys, os, types.ModuleType, firby_cli_common, firby_cli_instances, firby_cli_runtime`

### `firby_design.py` (43 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations`

### `tests/test_demo_admin_priority.py` (43 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 4
- **Imports:** `ast, pathlib.Path`

### `scripts/patches/patch_login_final.py` (43 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `instances/clinica-de-las-americas/firby_design.py` (43 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `__future__.annotations`

### `scripts/patches/patch_head.py` (42 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_instances_topbar.py` (42 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_panel_layout.py` (42 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_redundant_opening_filter.py` (41 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `pathlib.Path, sys, src.core.globals.ResponseGenerator, src.core.globals.ResponseGenerator`

### `scripts/patches/fix_wrapper.py` (41 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_sidebar_bug.py` (41 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `tests/test_tenant_registry.py` (40 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `pytest, pathlib.Path, src.firby.core.tenant.TenantConfig, src.firby.core.tenant.TenantRegistry, src.firby.core.tenant.load_env_file`

### `scripts/patches/fix_kpi_braces.py` (40 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/revert_headers.py` (40 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/update_caddy.py` (40 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_scroll.py` (40 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/test_agents.py` (39 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `urllib.request, json, logging`

### `scripts/add_lang_setting.py` (39 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_logo_v13.py` (39 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_chat_template.py` (39 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/wipe_naked.py` (38 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_heatmap_title.py` (38 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_logo_theme.py` (38 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_page.py` (38 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/rewrite_panel.py` (37 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/mount_patch.py` (37 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_page_wrapper.py` (37 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_chart.py` (37 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_panel_topbar.py` (36 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_all_refs.py` (36 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_melissa.py` (35 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `asyncio, os, sys, firby`

### `firby_skills/demo_mode.py` (35 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `firby_i18n.get_i18n, firby_i18n.SUPPORTED_LANGUAGES`

### `scripts/patches/patch_cursive.py` (35 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/update_borders.py` (35 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/replace_logo.py` (35 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `os, glob`

### `instances/clinica-de-las-americas/firby_skills/demo_mode.py` (35 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `firby_i18n.get_i18n, firby_i18n.SUPPORTED_LANGUAGES`

### `scripts/patches/fix_app_heatmap.py` (34 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_analytics_topbar.py` (34 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_heatmap.py` (34 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/refactor_sidebar.py` (34 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patch_firby_demo.py` (33 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `scripts/patches/fix_heatmap_regex.py` (33 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_sidebar_profile.py` (33 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_redirect.py` (33 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/utils/create_user.py` (33 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `sqlite3, hashlib, secrets`

### `firby_core/identity_policy.py` (32 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `__future__.annotations`

### `scripts/patches/fix_page_sidebar.py` (32 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_fallback_out.py` (32 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_dev_login.py` (32 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `instances/clinica-de-las-americas/firby_core/identity_policy.py` (32 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 3
- **Imports:** `__future__.annotations`

### `landing/fix_animations.py` (31 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_greeting.py` (31 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_final_minimal.py` (31 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_fonts.py` (31 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_page_font.py` (30 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_sidebar_pathname.py` (30 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_carbon_overrides.py` (30 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_aside_modern.py` (30 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_isotype_switch.py` (30 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re, os`

### `scripts/patches/patch_table.py` (29 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_panel_page.py` (29 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_apple_fonts.py` (29 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_page_grid.py` (29 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_page_search_cleanup.py` (29 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patch2.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/hoist_vars.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/protect_listeners.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `re`

### `scripts/patches/fix_api_dashboard.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_auth.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_wide_card.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_layout.py` (28 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_links2.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_kpi_date.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/rewrite_return.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/update_page.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_all.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_module_name.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `scripts/patches/fix_app.py` (27 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_app_eye.py` (26 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_settings_light.py` (26 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_page_search.py` (26 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_prospect.py` (26 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `core/__init__.py` (25 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `firby_memory_engine.memory_engine, firby_memory_engine.FirbyMemoryEngine, firby_uncertainty.uncertainty_detector, firby_uncertainty.UncertaintyDetector, firby_voice.voice, firby_voice.FirbyVoice, firby_nova_proxy.NovaLLMProxy, src.interfaces.web.admin_api.router`

### `scripts/patches/fix_panel_back_link.py` (25 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/utils/check_token.py` (25 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `os`

### `dev/react/fix_mess.py` (25 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `agents/ovni/core/__init__.py` (25 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `firby_memory_engine.memory_engine, firby_memory_engine.FirbyMemoryEngine, firby_uncertainty.uncertainty_detector, firby_uncertainty.UncertaintyDetector, firby_voice.voice, firby_voice.FirbyVoice, firby_nova_proxy.NovaLLMProxy, src.interfaces.web.admin_api.router`

### `instances/clinica-de-las-americas/core/__init__.py` (25 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `firby_memory_engine.memory_engine, firby_memory_engine.FirbyMemoryEngine, firby_uncertainty.uncertainty_detector, firby_uncertainty.UncertaintyDetector, firby_voice.voice, firby_voice.FirbyVoice, firby_nova_proxy.NovaLLMProxy, src.interfaces.web.admin_api.router`

### `scripts/patches/fix_panel_chart.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_theme.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_refs.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_routes.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_settings_tab.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_mounts.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_spacing.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_fastapi_react.py` (24 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scratch/wipe_all_demo_memory.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sqlite3, os, sys`

### `scripts/patches/fix_app_user_avatar.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re, sqlite3`

### `scripts/patches/fix_declarations.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_onboarding_placement.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_panel_date.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_input.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_layout_metadata.py` (23 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_top.py` (22 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_logo.py` (22 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os`

### `scripts/patches/fix_waitlist_placement.py` (22 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_indent.py` (22 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scratch/test_token.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `asyncio, logging, re, sys, os, src.firby.channels.onboarding.validate_telegram_token`

### `scripts/patches/patch_js.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_routes.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_globals.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_fastapi_redirect.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_font_size.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_sidebar_nav.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/tests/test_routes.py` (21 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_headers.py` (20 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_forgot_pwd.py` (20 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/utils/extract_signin2.py` (20 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `json`

### `scripts/utils/check_divs.py` (20 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patch_nav_firby.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_env_writer.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `pathlib.Path, firby_cli_common.load_env, firby_cli_common.update_env_key`

### `scripts/patches/patch_sidebar_links.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_showscreen.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_sidebar_children.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_fallback.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/utils/check_divs2.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/utils/extract_signin.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `json`

### `src/firby/integrations/__init__.py` (19 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `knowledge.KnowledgeBase, knowledge.format_kb_context, knowledge.CHUNK_SIZE, knowledge.CHUNK_OVERLAP, knowledge.MAX_CHUNKS_IN_CONTEXT, knowledge.MIN_RELEVANCE`

### `scripts/translate.py` (18 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patch_nav_firby_ai.py` (18 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_links.py` (18 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_dev_ai_chat_css.py` (18 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `tests/test_admin_wiring.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 2
- **Imports:** `pathlib.Path`

### `tests/test_identity_and_simulation_exit.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `sys, pathlib.Path, pytest, src.firby.utils.helpers.is_negative`

### `scripts/patches/patch_initAdminChat.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_chart_height.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_ui_vars.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_logo.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_revert_maxwidth.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/utils/check_divs3.py` (17 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/extract.py` (16 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `json`

### `scripts/search_exact.py` (16 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `os, re`

### `scripts/patches/patch_password_eye.py` (16 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_missing_vars.py` (16 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_page_button.py` (16 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_init.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/update_caddy_assets.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_panel_back_icon.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_nav.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_layout_auth.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_page_avatar.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_tabs.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_btnSwitchToDev.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/revert_borders.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `re`

### `dev/react/update_transparency.py` (15 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `re`

### `firby_agents/objeciones.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `firby_agents/captacion.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `firby_agents/conocimiento.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `firby_agents/agenda.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `firby_agents/seguimiento.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `firby_agents/escalacion.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `scratch/inspect_cli.py` (14 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `ast`

### `firby_integrations/whatsapp.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `firby_integrations/llm.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `scripts/patches/fix_hola.py` (14 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_word_order.py` (14 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_hero_space.py` (14 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_colors.py` (14 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `agents/ovni/firby_agents/objeciones.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `agents/ovni/firby_agents/captacion.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `agents/ovni/firby_agents/conocimiento.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `agents/ovni/firby_agents/agenda.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `agents/ovni/firby_agents/seguimiento.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `agents/ovni/firby_agents/escalacion.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_agents/objeciones.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_agents/captacion.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_agents/conocimiento.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_agents/agenda.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_agents/seguimiento.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_agents/escalacion.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_integrations/whatsapp.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `instances/clinica-de-las-americas/firby_integrations/llm.py` (14 líneas)
- **Clases (1):** NotImplementedAgent
- **Funciones:** 1

### `scripts/remove_sidebar_theme.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_dashboard.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_register_btn.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_hero_size.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_grid.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_navitems.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_demo_prompt.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/resize_middle_row.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_sidebar_links.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_sidebar.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_panel_arrays.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/tests/check_db.py` (13 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sqlite3, json`

### `scripts/patches/patch_table_size.py` (12 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_panel_sales.py` (12 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_favicon.py` (12 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_app_js_missing.py` (12 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_type.py` (12 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_redirects.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_app_js_final.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_sidebar_shrink.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_symmetry.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_root.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/revert_html.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/update_topbar_children.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_syntax.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_landing_margin.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_resizable_3.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/add_router.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_resizable.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/channels/logo_art.py` (11 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `tests/test_cli_entrypoint.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 1
- **Imports:** `firby_app`

### `scripts/patches/fix_ts_settings.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_mounts_final.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_db_emails.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sqlite3`

### `scripts/patches/fix_sidebar2.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_ts_kpi.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_font_size_2.py` (10 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_aside.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_sidebar_style.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_fallback_again.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_page_imports.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/patch_menu.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_signin2.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/update_signin.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/revert.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_signin.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_ai_chat_bg.py` (9 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_modern_sidebar.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_next.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_settings_avatars.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `scripts/patches/fix_fallback_logic.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_copy_bug.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_import.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_import_force.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/update_logo.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `re`

### `dev/react/fix_lucide.py` (8 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scratch/check_db_globals.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sys, src.core.globals.db`

### `scripts/patches/patch_anchor.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_period.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/patch_cta_link.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/patches/fix_js.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_copy.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_use_client.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_copy_client.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_resizable_2.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_meta.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_sidebar.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_favicon.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `dev/react/fix_layout_meta.py` (7 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `scripts/utils/check_db.py` (6 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `sqlite3`

### `scripts/tests/test_video_route.py` (6 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `urllib.request`

### `scripts/patches/patch_caddy.py` (5 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `firby_integrations/__init__.py` (4 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `firby_integrations.vault.IntegrationVault, firby_integrations.vault.get_vault`

### `scripts/tests/test_login.py` (4 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `requests`

### `scripts/tests/test_config.py` (4 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `requests`

### `instances/clinica-de-las-americas/firby_integrations/__init__.py` (4 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `firby_integrations.vault.IntegrationVault, firby_integrations.vault.get_vault`

### `firby_core/__init__.py` (3 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `conversation_engine.ConversationEngine, conversation_engine.ConversationTurnResult, persona_registry.PersonaProfile, persona_registry.PersonaRegistry`

### `instances/clinica-de-las-americas/firby_core/__init__.py` (3 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `conversation_engine.ConversationEngine, conversation_engine.ConversationTurnResult, persona_registry.PersonaProfile, persona_registry.PersonaRegistry`

### `src/firby/utils/__init__.py` (2 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
- **Imports:** `i18n.get_i18n, i18n.detect_user_language, i18n.SUPPORTED_LANGUAGES`

### `firby_agents/__init__.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `firby_skills/__init__.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `firby_skills/text_processing.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `firby_skills/tone_detection.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `agents/ovni/firby_agents/__init__.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/domain/prompts/__init__.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `instances/clinica-de-las-americas/firby_agents/__init__.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `instances/clinica-de-las-americas/firby_skills/__init__.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `instances/clinica-de-las-americas/firby_skills/text_processing.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `instances/clinica-de-las-americas/firby_skills/tone_detection.py` (1 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/demo/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/personas/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/admin/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/api/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/core/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/channels/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0

### `src/firby/production/__init__.py` (0 líneas)
- **Clases (0):** Ninguna
- **Funciones:** 0
