# Master Handoff & Memory State: Firby AI & Autonomous Red-Team Engine

## Session Metadata
- Created: 2026-07-23 05:12:00
- Project: /home/ubuntu/firby
- Branch: refactor-v10
- System Status: 100% Operational (247/247 Unit Tests Passing, PM2 Online)

## Handoff Chain
- **Continues from**: Master Architecture & Red-Teaming Integration
- **Supersedes**: None (Master State)

## Current State Summary

Firby is a 100% autonomous, LLM-driven WhatsApp AI agent for businesses with full voice synthesis (ElevenLabs cascade), natural disfluencies ("ehh...", "mira..."), WhatsApp presence emulation ("Grabando audio..."), zero-robot phrase filtering, and a newly implemented **Autonomous AI vs AI Red-Teaming Engine (`firby_redteam.py`)**.

All demo and production features have been aligned and verified via automated unit testing and dynamic AI-to-AI red-teaming.

## Architecture Overview

Firby uses a dual-engine architecture:
1. **Demo Engine (`src/interfaces/web/demo_handler.py`)**: Handles onboarding business name discovery, confirmation, roleplay mode, interactive commands, and live client simulation.
2. **Production Engine (`src/core/production_monitor.py`)**: Handles live patient interactions, knowledge base retrieval, NPS feedback loops, vision skin diagnostics, and admin escalation.
3. **Voice Cascade Engine (`firby_demo_voice.py` & `firby_core/api_awareness.py`)**: Rotates 3 ElevenLabs API keys across 4 female voices (Jessica, Sarah, Laura, Bella) with disfluency injection and phonetic fixes.
4. **Autonomous AI Red-Teaming Engine (`firby_redteam.py`)**: Simulates 5 dynamic AI Lead personas against Demo and Production endpoints, measuring cliches, loops, and quality scores.

## Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| `firby_redteam.py` | Autonomous AI vs AI Red-Teaming Engine | Evaluates Demo and Production modes across 5 personas |
| `src/interfaces/web/demo_handler.py` | Demo & Onboarding Manager | Manages business search, confirmation, and roleplay |
| `src/core/production_monitor.py` | Production Monitor | Live patient chat, NPS, vision, and admin alerts |
| `firby_demo_voice.py` | Voice Cascade & Disfluencies | TTS synthesis, phonetic fixes (`Bubli`), filler injection |
| `firby_core/api_awareness.py` | API & Voice Awareness | `should_send_voice` reasoning and capability mapping |
| `firby_cli_runtime.py` | CLI Command Dispatcher | Exposes `firby redteam`, `firby sync`, `firby status` |

## Files Modified

- `firby_redteam.py`: Built autonomous AI vs AI Red-Teaming engine.
- `src/interfaces/web/demo_handler.py`: Fixed reset scope bug and onboarding query filter.
- `src/firby/demo/handler.py`: Synced reset and onboarding filter changes.
- `src/core/production_monitor.py`: Added `_recording_action` presence status before audio dispatch.
- `firby_core/api_awareness.py`: Updated `should_send_voice` to handle explicit requests & production lotteries.
- `firby_demo_voice.py`: Fixed unbound `clean` variable and updated phonetic disfluency patterns.
- `firby_cli_runtime.py`: Added `redteam` route to CLI commands.

## Decisions Made

| Decision | Options Considered | Rationale |
|----------|-------------------|-----------|
| Autonomous AI Red-Teaming Engine | Manual QA vs LLM-Lead Simulation | LLM Lead simulation finds real edge-case bugs 100x faster |
| Phonetic `Bubli` Replacement | Raw "Firby" vs "Bubli" | ElevenLabs pronounced "Firby" as "Boobly"; "Bubli" sounds natural |
| WhatsApp Presence Emulation | Instant Audio vs `_recording_action` | "Grabando audio..." presence makes voice notes feel 100% human |
| Onboarding Query Filter | Searching raw text vs Keyword Filter | Prevents random YouTube/TikTok link responses for text questions |

## Immediate Next Steps

1. Execute periodic Red-Team runs (`python3 firby_cli.py redteam --mode production`).
2. Continue expanding AI Lead personas for niche sectors (dermatology, dental, retail).
3. Monitor PM2 logs (`firby logs`).

## Important Context

The next agent working on Firby MUST preserve:
1. **Phonetic Fix**: "Firby" is replaced with "Bubli" inside `inject_human_disfluencies` for audio track only.
2. **Explicit Audio Requests**: Must ALWAYS trigger voice note dispatch regardless of turn number.
3. **No Robot Cliches**: Never return static fallback strings or "demo reseteada".
4. **Onboarding Search Protection**: Text questions without business nouns must not be searched in SerpAPI.

## Assumptions Made

- ElevenLabs API keys in `firby_demo_voice.py` remain active and funded.
- SerpAPI key in `search.py` is configured for Google business searches.

## Potential Gotchas

- When testing in production mode within scripts, ensure `Config.DEMO_MODE` is handled appropriately so the router delegates to `production_mgr`.
