# Akcero AI Product Builder — Streamlit Edition

Akcero accelerates founders from raw idea to actionable product blueprint. This Streamlit-based prototype orchestrates a team of specialized AI agents to synthesize product, business, and go-to-market insights in minutes—complete with a polished PDF export and persistent run history.

## Quickstart
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env`  # add `OPENAI_API_KEY` and `MONGO_URI` if available
4. `streamlit run app.py`

OpenAI and MongoDB keys are optional; the app falls back to deterministic templates and local JSON storage when they are absent.

## Architecture Overview
- **Streamlit UI (`app.py`)** – Beautiful hero layout, agent status indicators, history sidebar, and CTA experiences (PDF export, library save, pitch mode).
- **Agents (`/agents`)** – Modular, deterministic classes inheriting from `BaseAgent`. Each agent focuses on a specific slice of the blueprint.
- **Umbrella Orchestration (`/core/umbrella_agent.py`)** – Hybrid `asyncio` workflow: sequential discovery → parallel execution → sequential synthesis, producing a unified `ProductBlueprint` schema.
- **Schemas & Dependencies (`/core`)** – Typed `TypedDict` schematics and LLM dependency helpers with a deterministic fallback.
- **Utilities (`/utils`)** –
  - `storage.py`: MongoDB persistence with graceful JSON fallback.
  - `report_generator.py`: ReportLab-driven PDF builder styled with Akcero branding.
  - `theming.py`: Centralized Streamlit theming and reusable card components.
- **Assets (`/assets`)** – Lightweight Akcero wordmark used across UI and PDFs.

## Data & Storage Strategy
- Saves every run (`idea_text`, agent outputs, blueprint, pitch, timestamp) to MongoDB collection `ideas` when `MONGO_URI` is set.
- Falls back to timestamped JSON files in `/storage` with identical structure.
- Sidebar history selector repopulates the interface for quick review or PDF regeneration.

## LLM Plug-and-Play
`core/deps.get_llm()` dynamically selects the best available provider:
- **OpenAI** – When `OPENAI_API_KEY` exists; uses chat completions for richer outputs.
- **Deterministic templates** – Offline-friendly fallback ensuring the demo always runs.

## PDF Blueprint Export
`utils/report_generator.build_pdf()` renders the complete blueprint into a brand-aligned PDF featuring:
- Logo header & tagline
- Sectioned content matching agent cards
- Executive summary & roadmap
- Footer with generation timestamp

## Screenshots (placeholders)
- `docs/screenshot-hero.png`
- `docs/screenshot-blueprint.png`

Replace the placeholders with actual screenshots after running the app.

## Development Notes
- Codebase is fully typed with docstrings and inline commentary where clarity helps.
- Designed for extensibility—swap agents, LLMs, or UI components without touching the core orchestration.
- Graceful error handling surfaces actionable feedback directly in the Streamlit UI.

Enjoy building the future with Akcero. 🚀
