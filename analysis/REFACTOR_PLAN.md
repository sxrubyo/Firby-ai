# REFACTOR PLAN — firby.py → src/firby/

## STATS
- 28,972 lines | 63 classes | 507 functions
- FirbyUltra god-class: 10,377 lines (36%)
- 16 satellite modules imported
- 2 circular dependency risks (firby_admin, firby_production)
- 7 true duplicates (satellite always wins)
- ~60k total lines ecosystem

## MIGRATION ORDER (independientes primero)

### Wave 1 — Zero coupling (can move immediately)
1. `src/firby/utils/i18n.py` ← firby_i18n.py (standalone)
2. `src/firby/utils/helpers.py` ← firby_utils.py (standalone)
3. `src/firby/brain/uncertainty.py` ← firby_uncertainty.py (standalone)
4. `src/firby/integrations/knowledge.py` ← knowledge_base.py (standalone)

### Wave 2 — Low coupling (import from core only)
5. `src/firby/brain/memory.py` ← firby_memory_engine.py (standalone)
6. `src/firby/channels/voice.py` ← firby_voice.py (standalone)
7. `src/firby/channels/audio.py` ← firby_audio.py (needs Config)
8. `src/firby/core/router.py` ← firby_router.py (standalone)
9. `src/firby/core/session.py` ← firby_session.py (standalone)

### Wave 3 — Medium coupling (import from firby.py globals)
10. `src/firby/brain/engine.py` ← firby_brain_v10.py (imports from __main__)
11. `src/firby/production/guard.py` ← firby_send_guard.py (needs db)
12. `src/firby/production/handoff.py` ← smart_handoff.py (needs db+llm)
13. `src/firby/admin/api.py` ← firby_admin_api.py (needs app)

### Wave 4 — The god-class split (FirbyUltra 10k lines)
14. Extract demo logic → `src/firby/demo/handler.py`
15. Extract buffer/send → `src/firby/core/messenger.py`
16. Extract FastAPI routes → `src/firby/api/routes.py`
17. FirbyUltra remains as thin orchestrator (~500 lines)

### Wave 5 — firby_cli.py (second monolith, 459KB)
18. Separate refactor session

## CIRCULAR DEPS FIX
- firby_admin imports `db, llm_engine` from firby → inject via params
- firby_production imports `db, llm_engine, kb` → inject via params
- Pattern: pass dependencies as constructor args, not global imports

## RISKS
- FirbyUltra has 431 methods — splitting it will break many internal refs
- Demo logic (lines 12507-15000) mixes with core orchestration
- Some functions are 500+ lines with nested closures
- Production DB paths are hardcoded in several places

## FIRST MODULE TO EXTRACT: firby_i18n.py
- 0 dependencies on firby.py
- Already a clean standalone module
- Quick win to validate the pattern
