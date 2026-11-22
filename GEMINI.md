# Agentic Entrepreneur OS - Project Guidelines & Rules

## Project Overview
This repository contains the official codebase and academic deliverables for **Agentic Entrepreneur OS: A Wealth-Formation Opportunity Discovery Pipeline**, a Final Year Project (FYP-I) at **FAST School of Computing, FAST National University (Karachi Campus)**, Session Fall 2026.

## Development Environment
- Python version: `>= 3.12`
- Virtual environment: Managed with `uv` in `.venv/`
- Run CLI: `.venv\Scripts\python.exe -m src.agentic_os.cli.main`
- Run API: `.venv\Scripts\python.exe -m src.agentic_os.api.app`
- Run Tests: `.venv\Scripts\pytest`

## Code Guidelines & Standards
1. **Type Safety**: All modules must utilize Pydantic v2 schemas located in `src/agentic_os/schemas/`.
2. **Deterministic Dual-Graph**: Graph operations must be performed using `networkx` DiGraph structures with explicit bipartite causal links.
3. **Triangulation Rigour**: Any opportunity or obstacle extraction must enforce a minimum of 2 distinct source types (`FORUM`, `REVIEW`, `JOB_POSTING`, `INDUSTRY_REPORT`).
4. **Labor-to-Asset Reframing**: Never output raw hourly billing suggestions. Always transform service concepts into compounding digital assets (Power 4 - Ownership Mindset).
5. **Human-in-the-Loop Safeguards**: High-commitment actions must be gated by the `HumanCheckpointManager` utilizing regret-minimization framing (Power 1) and Kelly-sizing limits.

## Customizations
- Skills: Available under `.agents/skills/`
- MCP Server: Configured in `mcp_config.json` via `agentic-os-engine`
