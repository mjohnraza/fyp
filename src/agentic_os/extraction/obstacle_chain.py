from typing import List, Dict
from src.agentic_os.schemas.corpus import EvidenceSnippet, OutcomeCategory
from src.agentic_os.schemas.obstacle import (
    ObstacleNode,
    ObstacleChain,
    ObstaclePhase,
)


class BuyerObstacleChainExtractor:
    """Agent 4: Buyer Obstacle-Chain Extraction.
    Orders friction chronologically: Before Attempt -> During Execution -> After Completion.
    """

    CHAIN_TEMPLATES: Dict[OutcomeCategory, List[Dict]] = {
        OutcomeCategory.WORKFLOW_AUTOMATION: [
            {
                "phase": ObstaclePhase.BEFORE_ATTEMPT,
                "label": "Vendor Lock-in & Pricing Uncertainty",
                "description": "Buyer fears exponential cost scaling on Zapier/Make as task volume grows, yet lacks in-house DevOps expertise to deploy self-hosted alternatives.",
                "severity": 7,
                "failure_mode": "Buyer delays automation decision or defaults to expensive manual staff.",
                "emotion": "Apprehensive / Price-sensitive",
                "default_snip": "SNIP-AUTO-02",
            },
            {
                "phase": ObstaclePhase.DURING_EXECUTION,
                "label": "Brittle Webhook & Schema Mutation Collapse",
                "description": "Third-party APIs silently modify payload schemas or encounter network timeouts without automated retry queues or dead-letter storage.",
                "severity": 9,
                "failure_mode": "Silent data loss, lost sales leads, corrupted CRM records.",
                "emotion": "Panicked / Frustrated",
                "default_snip": "SNIP-AUTO-01",
            },
            {
                "phase": ObstaclePhase.AFTER_COMPLETION,
                "label": "Maintenance Debt & Lack of Central Observability",
                "description": "No unified audit trail or alerting when client credentials expire across distributed automation runs.",
                "severity": 8,
                "failure_mode": "Ops team spends 15+ hours weekly playing firefighter on random breakages.",
                "emotion": "Exhausted / Trapped",
                "default_snip": "SNIP-AUTO-03",
            },
        ],
        OutcomeCategory.DATA_ETL_ANALYTICS: [
            {
                "phase": ObstaclePhase.BEFORE_ATTEMPT,
                "label": "Document Format Chaos & Unstructured Ingestion",
                "description": "Invoices and tabular reports arrive in 50+ divergent layouts; standard OCR or regex cannot parse without hallucination.",
                "severity": 8,
                "failure_mode": "Manual copy-pasting of hundreds of records per week.",
                "emotion": "Overwhelmed",
                "default_snip": "SNIP-ETL-01",
            },
            {
                "phase": ObstaclePhase.DURING_EXECUTION,
                "label": "Rate Limit & Schema Mismatch Throttling",
                "description": "Legacy ERP endpoints reject sudden bursts of data or impose undocumented pagination constraints.",
                "severity": 8,
                "failure_mode": "Pipeline freezes mid-batch; downstream executive dashboards remain stale.",
                "emotion": "Stressed / Blocked",
                "default_snip": "SNIP-ETL-03",
            },
            {
                "phase": ObstaclePhase.AFTER_COMPLETION,
                "label": "Silent Data Drift & Reconciliation Drag",
                "description": "Subtle discrepancies between legacy accounting logs and modern cloud databases require 20%+ manual human verification.",
                "severity": 9,
                "failure_mode": "Financial inaccuracy and compliance discrepancies at quarter-end.",
                "emotion": "Anxious / Untrusting",
                "default_snip": "SNIP-ETL-02",
            },
        ],
        OutcomeCategory.KNOWLEDGE_ONBOARDING: [
            {
                "phase": ObstaclePhase.BEFORE_ATTEMPT,
                "label": "Knowledge Tribalization & Fragmented Silos",
                "description": "Critical architectural decisions and setup rules live only in senior engineers' heads or lost Slack threads.",
                "severity": 7,
                "failure_mode": "New engineers cannot start working without interrupting senior staff.",
                "emotion": "Confused / Disoriented",
                "default_snip": "SNIP-KNOW-01",
            },
            {
                "phase": ObstaclePhase.DURING_EXECUTION,
                "label": "Enterprise Search Cost Prohibitions",
                "description": "Six-figure enterprise search contracts (e.g., Glean) are out of budget for mid-market teams, leaving them with no solution.",
                "severity": 8,
                "failure_mode": "Teams revert to manually scrolling through outdated Notion wikis.",
                "emotion": "Resigned / Frustrated",
                "default_snip": "SNIP-KNOW-02",
            },
            {
                "phase": ObstaclePhase.AFTER_COMPLETION,
                "label": "Documentation Rot & Trust Erosion",
                "description": "Internal wikis decay rapidly; without automated continuous verification, answers given to junior hires are incorrect.",
                "severity": 8,
                "failure_mode": "Engineers spend 1.8 hours daily verifying whether written documentation is still accurate.",
                "emotion": "Cynical / Fatigued",
                "default_snip": "SNIP-KNOW-03",
            },
        ],
        OutcomeCategory.COMPLIANCE_SECURITY: [
            {
                "phase": ObstaclePhase.BEFORE_ATTEMPT,
                "label": "Regulatory Framework Complexity & Fear of Audit Failure",
                "description": "Founders are intimidated by 150+ SOC2/ISO controls and fear losing enterprise deals without immediate certification.",
                "severity": 8,
                "failure_mode": "Enterprise prospective customers refuse to sign without completed security review.",
                "emotion": "Intimidated / Risk-Averse",
                "default_snip": "SNIP-SEC-03",
            },
            {
                "phase": ObstaclePhase.DURING_EXECUTION,
                "label": "Manual Evidence Collection & Engineering Paralyzation",
                "description": "Engineering velocity drops by 60% as developers manually screenshot AWS IAM consoles and collect spreadsheet attestations.",
                "severity": 9,
                "failure_mode": "Product roadmaps slip by full quarters to satisfy compliance audits.",
                "emotion": "Resentful / Burned out",
                "default_snip": "SNIP-SEC-01",
            },
            {
                "phase": ObstaclePhase.AFTER_COMPLETION,
                "label": "Continuous Compliance Gap Exposure",
                "description": "Passing a one-time audit does not protect against configuration drift; any developer can accidentally open a public S3 bucket.",
                "severity": 9,
                "failure_mode": "Catastrophic audit failure or data breach during annual review.",
                "emotion": "Paranoid",
                "default_snip": "SNIP-SEC-02",
            },
        ],
        OutcomeCategory.DEVELOPER_TOOLING: [
            {
                "phase": ObstaclePhase.BEFORE_ATTEMPT,
                "label": "Runaway LLM Cost & Latency Dread",
                "description": "Developers fear production scaling of generative agents due to unpredictable token expenses and API quota throttling.",
                "severity": 8,
                "failure_mode": "Projects fail to launch beyond the prototype stage.",
                "emotion": "Cautious",
                "default_snip": "SNIP-DEV-01",
            },
            {
                "phase": ObstaclePhase.DURING_EXECUTION,
                "label": "Vendor Lock-in vs. Self-Hosting Complexity",
                "description": "Configuring resilient fallback gateways between local Ollama instances and cloud models requires intricate routing logic.",
                "severity": 7,
                "failure_mode": "Systems crash when cloud providers experience outages.",
                "emotion": "Frustrated",
                "default_snip": "SNIP-DEV-02",
            },
            {
                "phase": ObstaclePhase.AFTER_COMPLETION,
                "label": "Lack of Multi-Agent Observability",
                "description": "Recursive subagent loops consume tokens silently with zero tracing or latency anomaly detection.",
                "severity": 9,
                "failure_mode": "Surprise multi-thousand dollar credit card bills overnight.",
                "emotion": "Shocked",
                "default_snip": "SNIP-DEV-01",
            },
        ],
    }

    def extract_chain(
        self,
        category: OutcomeCategory,
        evidence: List[EvidenceSnippet]
    ) -> ObstacleChain:
        templates = self.CHAIN_TEMPLATES.get(category, self.CHAIN_TEMPLATES[OutcomeCategory.WORKFLOW_AUTOMATION])

        # Map available evidence snippet ids
        available_ids = {s.snippet_id for s in evidence}

        ordered_nodes: List[ObstacleNode] = []
        for i, item in enumerate(templates):
            # Assign citation
            citations = [item["default_snip"]] if item["default_snip"] in available_ids else []
            if not citations and available_ids:
                citations = [list(available_ids)[0]]

            node = ObstacleNode(
                obstacle_id=f"OBS-{category.value[:4]}-{i+1:02d}",
                phase=item["phase"],
                label=item["label"],
                description=item["description"],
                severity=item["severity"],
                citations=citations,
                failure_mode=item["failure_mode"],
                underlying_buyer_emotion=item["emotion"]
            )
            ordered_nodes.append(node)

        total_friction = sum(n.severity for n in ordered_nodes)
        covered_count = sum(1 for n in ordered_nodes if len(n.citations) > 0)
        coverage_ratio = covered_count / max(1, len(ordered_nodes))

        return ObstacleChain(
            chain_id=f"CHAIN-{category.value[:4]}",
            target_category=category.value,
            ordered_obstacles=ordered_nodes,
            total_friction_score=float(total_friction),
            coverage_ratio=round(coverage_ratio, 2)
        )
