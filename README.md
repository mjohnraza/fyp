# Agentic Entrepreneur OS: A Wealth-Formation Opportunity Discovery Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Tests Passing](https://img.shields.io/badge/tests-12%2F12%20passed-brightgreen.svg)](tests/)

**Final Year Project (FYP-I Deliverable)**  
**Department of AI & Computer Science**  
**FAST School of Computing, FAST National University of Computer & Emerging Sciences (Karachi Campus)**  
**Session:** Fall 2026  

---

## 📖 Overview
**Agentic Entrepreneur OS** is a multi-agent system built on Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) that systematically reframes entrepreneurial opportunity discovery around **compounding asset formation** rather than one-off idea generation.

Unlike conventional chatbot ideation tools that output unvalidated product claims, Agentic Entrepreneur OS:
1. Decomposes individual skills into **capability clusters** and **cross-cluster intersections**.
2. Retrieves and triangulates **real buyer friction** across 4 source types (Forums, Reviews, Job Postings, and Industry Reports).
3. Sequences pain points into chronologically ordered **buyer obstacle chains** (`BEFORE_ATTEMPT`, `DURING_EXECUTION`, `AFTER_COMPLETION`).
4. Constructs a **bipartite dual graph** and applies an explicit **Ownership-Mindset Labour-to-Asset Reframing Pass** (motivated by Power 4, Bouchaud & Mézard [11], and Penrose [16]).
5. Formalizes Alex Hormozi's **Value Equation** ($V = \frac{\text{Dream} \times \text{Likelihood}}{\text{Time} \times \text{Effort}}$) to diagnose offer bottlenecks.
6. Synthesizes a 3-tier **funnel architecture** (Lead Magnet, Core Offer, Recurring Backend).
7. Gating via a **Human Checkpoint** with regret-minimization framing (Power 1) and Kelly-sizing capital constraints before generating the **Founder Decision Memo**.

---

## 🛠️ Environment Setup (using `uv`)

This project uses modern Python packaging managed with [`uv`](https://github.com/astral-sh/uv).

### 1. Initialize Virtual Environment
```powershell
# Navigate to the workspace
cd C:\Users\exam.DESKTOP-LNCC6CA\Desktop\fyp

# Create virtual environment
uv venv --python 3.12

# Activate virtual environment
.venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
uv pip install -e .
```

---

## 🚀 Usage Guide

### 1. Interactive Terminal CLI
Launch the interactive Rich terminal pipeline:
```powershell
.venv\Scripts\python.exe -m src.agentic_os.cli.main
```

### 2. FastAPI REST Server
Start the high-performance REST API:
```powershell
.venv\Scripts\python.exe -m src.agentic_os.api.app
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 3. Model Context Protocol (MCP) Server for Antigravity
The system provides a native stdio JSON-RPC MCP server configured in `mcp_config.json`:
```powershell
.venv\Scripts\python.exe -m mcp_servers.agentic_os_mcp.server
```
Exposed tools include:
- `ingest_profile`
- `decompose_capabilities`
- `retrieve_evidence`
- `extract_obstacle_chain`
- `diagnose_offer_value`
- `generate_founder_decision_memo`

---

## 🧪 Running Automated Tests
Run the test suite covering all Stage 1-4 functional modules:
```powershell
.venv\Scripts\pytest -v
```

---

## 📂 Repository Structure
```
fyp/
├── .agents/                        # Antigravity agent configuration
│   ├── skills/                     # Workspace skills
│   │   ├── agentic-entrepreneur-os/SKILL.md
│   │   ├── obstacle-chain-extractor/SKILL.md
│   │   └── offer-diagnostician/SKILL.md
│   └── mcp_config.json             # MCP server registration
├── GEMINI.md                       # Antigravity project conventions
├── mcp_config.json                 # Global MCP configuration
├── pyproject.toml                  # uv / hatchling package configuration
├── README.md                       # Master project overview
├── src/
│   └── agentic_os/
│       ├── schemas/                # Strongly-typed Pydantic schemas
│       ├── ingestion/              # Profiler, Clusterer, Intersection & Contradiction agents
│       ├── corpus/                 # Cold-start seeded market evidence
│       ├── retrieval/              # RAG & Multi-Source Triangulator
│       ├── extraction/             # Buyer Obstacle-Chain Extractor
│       ├── graph/                  # Dual-Graph Translation & Ownership Mindset Reframer
│       ├── agents/                 # Value Equation, Product Suite & 10-Dimension Scorecard
│       ├── orchestrator/           # Confidence routing, Loop-backs & Human Checkpoints
│       ├── api/                    # FastAPI application
│       └── cli/                    # Rich interactive terminal interface
├── mcp_servers/
│   └── agentic_os_mcp/             # MCP server implementation
├── tests/                          # 12 Pytest test suites (100% pass)
└── docs/                           # Academic & Software Engineering Documentation
    ├── FYP_1_INTERIM_REPORT.md     # Official FAST NUCES FYP-1 Report
    ├── SRS_DOCUMENT.md             # IEEE 830 Software Requirements Specification
    ├── SYSTEM_ARCHITECTURE.md      # Architectural design & diagrams
    └── DATA_COLLECTION_AND_CORPUS.md # Triangulated corpus documentation
```

---

## 📚 Academic Deliverables
- **[FYP-I Interim Report](docs/FYP_1_INTERIM_REPORT.md)**: Executive abstract, research questions, theoretical foundations (Bouchaud & Mézard, Pluchino et al., Kelly, Maresca, Barney, Penrose), verification results, and FYP-II roadmap.
- **[SRS Document](docs/SRS_DOCUMENT.md)**: IEEE Std 830-1998 Software Requirements Specification.
- **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)**: High-level architectural flowchart, bipartite dual-graph models, and component responsibilities.
- **[Corpus Audit](docs/DATA_COLLECTION_AND_CORPUS.md)**: Multi-source triangulation matrix and obstacle citation coverage.
