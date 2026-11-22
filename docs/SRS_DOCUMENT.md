# Software Requirements Specification (SRS)
## Agentic Entrepreneur OS: A Wealth-Formation Opportunity Discovery Pipeline
**Document Version:** 1.0.0  
**Author:** FYP-I Engineering Team  
**Institution:** FAST School of Computing, FAST National University Karachi  
**Standard:** IEEE Std 830-1998  

---

## 1. Introduction
### 1.1 Purpose
This document specifies the software requirements for the **Agentic Entrepreneur OS (FYP-I)**. The system is designed to convert unstructured technical skill profiles into evidence-grounded, defensible, and asset-accumulating entrepreneurial opportunities through a cooperative multi-agent architecture.

### 1.2 Scope
The scope of FYP-I encompasses:
- Profile ingestion, structured parsing, and capability decomposition.
- Triangulated market evidence retrieval across 5 target outcome categories.
- Chronologically sequenced buyer obstacle-chain extraction.
- Dual-graph translation with an explicit ownership-mindset labor-to-asset reframing pass.
- Formalized Alex Hormozi Value Equation offer diagnosis.
- 3-tier product suite generation (Lead Magnet, Core Offer, Recurring Backend).
- Grounding and consistency confidence evaluation with automated loop-backs.
- Human-in-the-loop checkpoint gating and Founder Decision Memo generation.

### 1.3 Definitions and Acronyms
- **LLM:** Large Language Model
- **RAG:** Retrieval-Augmented Generation
- **MCP:** Model Context Protocol
- **RBV:** Resource-Based View (Barney, 1991)
- **LTV:** Lifetime Value
- **MRR:** Monthly Recurring Revenue

---

## 2. Overall Description
### 2.1 Product Perspective
The Agentic Entrepreneur OS acts as an autonomous equity research desk for an individual's skills. Unlike generic chatbots, the system operates deterministically over structured capability and buyer friction graphs, enforcing evidentiary triangulation before suggesting entrepreneurial actions.

### 2.2 User Characteristics
- **Primary Users:** Software engineers, technical consultants, data professionals, and domain specialists seeking to transition from linear billable hours to scalable digital assets.

### 2.3 Operating Environment
- Operating System: Windows / Linux / macOS
- Runtime Environment: Python 3.12+ managed by `uv`
- Inference Environment: Local open-source models via Ollama (`qwen2.5`) with cloud fallback.

---

## 3. Specific Requirements
### 3.1 Functional Requirements (FR)
- **FR-1 (Ingestion):** The system shall parse unstructured bio and skill text into structured Capability, Context, and Constraint schemas.
- **FR-2 (Decomposition):** The system shall cluster related skills and compute cross-cluster intersections with uniqueness scores.
- **FR-3 (Contradiction Audit):** The system shall evaluate feasibility constraints (e.g., hours/week vs sales cycle) and flag contradictions.
- **FR-4 (Corpus Retrieval):** The system shall retrieve real-world buyer friction evidence from a cold-start corpus covering 5 outcome categories.
- **FR-5 (Evidence Triangulation):** The system shall enforce a minimum threshold of 2 distinct source types (`FORUM`, `REVIEW`, `JOB_POSTING`, `INDUSTRY_REPORT`) per outcome category.
- **FR-6 (Obstacle Chaining):** The system shall order buyer obstacles into three sequential phases (`BEFORE_ATTEMPT`, `DURING_EXECUTION`, `AFTER_COMPLETION`).
- **FR-7 (Dual-Graph Translation):** The system shall construct bipartite directed graphs linking capabilities to buyer relief outcomes via causal mechanisms.
- **FR-8 (Labor-to-Asset Reframing):** The system shall convert additive hourly service language into scalable, compounding asset statements.
- **FR-9 (Offer Diagnosis):** The system shall calculate Hormozi's Value Equation score and identify the primary bottleneck parameter.
- **FR-10 (Product Suite Generation):** The system shall design a 3-tier funnel comprising a free lead magnet, core offer, and recurring backend.
- **FR-11 (Confidence Routing):** The system shall route pipeline steps based on computed grounding and consistency signals, triggering loop-backs when thresholds are violated.
- **FR-12 (Human Checkpoint Gate):** The system shall prevent execution past the design stage until the founder confirms key assumptions.
- **FR-13 (Founder Decision Memo):** The system shall compile the final recommendation into an executive decision memo.

### 3.2 Non-Functional Requirements (NFR)
- **NFR-1 (Performance):** The entire Stage 1-4 pipeline must execute in under 3.0 seconds for cached/local retrieval.
- **NFR-2 (Determinism):** Graph compilation and scoring heuristics must produce deterministic outputs for identical inputs.
- **NFR-3 (Modularity):** Model inference and retrieval modules must be decoupled to allow swapping between Ollama, Gemini, and Claude.
- **NFR-4 (Interoperability):** The system must expose standard JSON-RPC MCP server interfaces and RESTful HTTP endpoints.
