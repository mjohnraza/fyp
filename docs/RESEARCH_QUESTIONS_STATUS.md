# Academic Research Questions (RQ1 – RQ5) Status & Verification
## Final Year Project-I (FYP-I) Deliverable Audit
**Institution:** FAST School of Computing, FAST National University Karachi  
**Session:** Fall 2026  
**Project:** Agentic Entrepreneur OS: A Wealth-Formation Opportunity Discovery Pipeline  

---

## Executive Summary: FYP-I Research Question Matrix

| Research Question | Focus Dimension | FYP-I Target Scope | Implementation Artifacts | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **RQ1** | Capability Decomposition & Obstacle-Chain Extraction | Fully Implemented & Tested | `ingestion/profiler.py`, `ingestion/clusterer.py`, `extraction/obstacle_chain.py`, `corpus/` | **COMPLETE** |
| **RQ2** | Grounding & Consistency Confidence Routing vs. LLM Confidence | Fully Implemented & Tested | `orchestrator/confidence.py`, `orchestrator/pipeline.py` | **COMPLETE** |
| **RQ3** | Ten-Dimension Scorecard & Hormozi Value Equation | Fully Implemented & Tested | `agents/scorecard.py`, `agents/offer_diagnosis.py`, `agents/product_suite.py` | **COMPLETE** |
| **RQ4** | Dual-Graph Translation & Labor-to-Asset Reframing | Fully Implemented & Tested | `graph/dual_graph.py`, `graph/reframing.py` | **COMPLETE** |
| **RQ5** | Behavioural Framing (Regret Minimization & Kelly Sizing) | System Architecture & Memo Copy Complete (A/B Human Trial in FYP-II) | `orchestrator/checkpoints.py`, `FounderDecisionMemo`, `frontend/index.html` | **FYP-I COMPLETE** (Trial in FYP-II) |

---

## Detailed Research Question Breakdown

### 🔬 RQ1: Grounded Extraction & Capability Decomposition
> *"Can a retrieval-grounded multi-agent pipeline extract buyer obstacle chains from diverse market evidence with higher fidelity than single-prompt baselines?"*

- **Theoretical Motivation:** Guo et al. (2024) [2] multi-agent decomposition, Renz et al. (2025) [6], Singh et al. (2025) [5] agentic RAG.
- **FYP-I Deliverables Completed:**
  1. **Schema Parsing:** `schemas/profile.py` converts raw text into `CapabilityItem`, `ContextItem`, and `ConstraintItem`.
  2. **Multi-Cluster Decomposition:** `ingestion/clusterer.py` and `ingestion/intersection.py` cluster skills and discover high-leverage intersections.
  3. **Cold-Start Seeding:** `corpus/seed_data.json` populated with 15 verified snippets across 5 outcome categories.
  4. **Multi-Source Triangulation:** `retrieval/triangulation.py` enforces $\ge 2$ distinct source types (`FORUM`, `REVIEW`, `JOB_POSTING`, `INDUSTRY_REPORT`).
  5. **Chronological Obstacle Sequencing:** `extraction/obstacle_chain.py` extracts 3 chronological phases (`BEFORE_ATTEMPT`, `DURING_EXECUTION`, `AFTER_COMPLETION`) with $100\%$ citation coverage.
- **Verification:** `tests/test_ingestion.py`, `tests/test_retrieval.py`, `tests/test_obstacle_chain.py` (All Passed).

---

### 🔬 RQ2: Grounding & Consistency Confidence vs. Self-Reported LLM Confidence
> *"Does confidence routing based on grounding and internal consistency outperform self-reported LLM confidence in triggering necessary loop-backs?"*

- **Theoretical Motivation:** LLM self-reported confidence (`"I am 95% confident"`) is notoriously uncalibrated and hallucinatory in complex planning tasks.
- **FYP-I Deliverables Completed:**
  1. **Grounding Confidence Formula:**
     $$\text{Grounding Score} = 0.5 \times \text{Triangulation Ratio} + 0.5 \times \text{Obstacle Citation Coverage}$$
  2. **Consistency Confidence Formula:**
     $$\text{Consistency Score} = 1.0 - \sum \text{Contradiction Penalties}$$
  3. **Dynamic Routing Engine:** In `orchestrator/confidence.py` and `orchestrator/pipeline.py`:
     - If $\text{Grounding} < 0.65 \implies$ Triggers loop-back to `RETRIEVAL_AGENT` to harvest additional source diversity.
     - If $\text{Consistency} < 0.70 \implies$ Triggers loop-back to `PROFILER_AGENT` to reconcile time/budget constraints.
- **Verification:** `tests/test_orchestrator.py` (Passed).

---

### 🔬 RQ3: Multi-Dimensional Opportunity Scoring & Value Equation
> *"Can a multidimensional economic scorecard discriminate between technically viable yet economically stagnant services versus multiplicative assets?"*

- **Theoretical Motivation:** Bouchaud & Mézard (2000) [11], Kelly (1956) [13], Barney (1991) [15], Penrose (1959) [16], Hormozi (2021) [8].
- **FYP-I Deliverables Completed:**
  1. **Table III Ten-Dimension Scorecard (`agents/scorecard.py`):**
     - Buyer Pain (0–10)
     - Evidence Strength (0–10)
     - Capability Fit (0–10)
     - Multiplicative Potential (0–10) [11]
     - Opportunity Surface Area (0–10) [12]
     - Defensibility (0–10) [15]
     - AI Leverage (0–10) [14]
     - Recurring Revenue Potential (0–10) [9]
     - Asset Accumulation Potential (0–10) [16]
     - Risk / Validation Cost (0–10) [13]
  2. **Hormozi's Value Equation Formalization (`agents/offer_diagnosis.py`):**
     $$V = \frac{\text{Dream Outcome} \times \text{Perceived Likelihood}}{\text{Time Delay} \times \text{Effort \& Sacrifice}}$$
     Diagnoses the exact bottleneck dimension and generates automated remediation advice.
  3. **3-Tier Product Suite & Funnel (`agents/product_suite.py`):**
     - Tier 1: Lead Magnet ($0)
     - Tier 2: Core Productized Offer ($1,497+)
     - Tier 3: Compounding Asset Backend ($399+/mo MRR)
- **Verification:** `tests/test_offer_diagnosis.py` (Passed).

---

### 🔬 RQ4: Dual-Graph Translation & Labour-to-Asset Reframing Pass
> *"Does an explicit ownership-mindset reframing pass measurably transform labor-bound services into compounding digital assets?"*

- **Theoretical Motivation:** Power 4 (Ownership Mindset) [18], Bouchaud & Mézard [11] multiplicative wealth dynamics, Penrose [16] firm resource accumulation.
- **FYP-I Deliverables Completed:**
  1. **Dual NetworkX Directed Graph (`graph/dual_graph.py`):**
     - Subgraph 1: Capability nodes, capability clusters, and cross-cluster intersections.
     - Subgraph 2: Chronological buyer obstacles and relief outcomes.
     - Cross-Graph Bipartite Causal Edges: Links capability clusters to buyer relief mechanisms.
  2. **Labour-to-Asset Reframing Engine (`graph/reframing.py`):**
     - Replaces linear hourly billing statements (*"I will write Zapier webhooks for $50/hr"*) with scalable digital asset architectures (*"Deployable Dockerized n8n engine with automated dead-letter queues on a $399/mo managed retainer"*).
     - Computes the multiplicative leverage ratio ($\ge 8\times$ labor efficiency).
- **Verification:** `tests/test_dual_graph.py` (Passed).

---

### 🔬 RQ5: Behavioural Coaching, Regret Minimization, & Human Checkpoint Gating
> *"Does regret-minimization framing and self-permission gating increase a founder's willingness to execute validation experiments?"*

- **Theoretical Motivation:** Power 1 (Regret Minimization) [18], Power 7 (Self-Permission) [18], Kelly (1956) [13] downside capital sizing.
- **FYP-I Deliverables Completed:**
  1. **Human-in-the-Loop Gate (`orchestrator/checkpoints.py`):**
     - Halts execution before high-commitment spending or public outreach.
     - Formulates the test as an invitation rather than high-pressure commitment (Power 7).
  2. **Regret-Minimization Comparison:**
     - Computes prospective 12-month regret: *"Spending 5 hours deploying your free lead magnet and getting 0 replies vs. spending the next 12 months wondering if a recurring asset was within your grasp."*
  3. **Kelly-Sizing Capital Protection:**
     - Explicitly caps validation expenditure to $10\% - 15\%$ of the founder's stated runway.
  4. **Founder Decision Memo:**
     - Consolidates the entire run into an auditable executive briefing memo.
- **FYP-I vs. FYP-II Scope Note:**
  - In **FYP-I**, the entire architecture, gating engine, and memo generation are built and verified.
  - In **FYP-II**, the empirical controlled user study (A/B testing willingness to act with vs. without behavioural framing) will be conducted with cohort participants.
- **Verification:** `tests/test_orchestrator.py` (Passed).
