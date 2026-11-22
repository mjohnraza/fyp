import re
from typing import Dict, List
from src.agentic_os.schemas.graph import ReframedAssetType, GroundedBuyerReliefStatement
from src.agentic_os.schemas.obstacle import ObstacleNode
from src.agentic_os.schemas.profile import CapabilityIntersection


class OwnershipMindsetReframer:
    """Pass motivated by Power 4 (Ownership Mindset), Bouchaud & Mézard [11], and Penrose [16].
    Converts linear, additive, labor-bound framing into multiplicative, compounding assets.
    """

    LABOR_PATTERNS = [
        (r"I will write scripts", "Deployable self-healing automation template with automated queue recovery"),
        (r"Hourly consultation", "Productized audit framework and compliance playbook with automated checks"),
        (r"Manual data entry", "Deterministic document extraction pipeline with human-in-the-loop review UI"),
        (r"Building custom chatbots", "Localized privacy-first knowledge base engine with continuous Slack/GitHub sync"),
        (r"Freelance development", "Reusable micro-SaaS starter pack with token proxy routing"),
    ]

    ASSET_MAPPING = {
        "WORKFLOW_AUTOMATION": (
            ReframedAssetType.AUTOMATION_WORKFLOW,
            "Sell 1-hour manual fix for $50",
            "Turnkey Dockerized n8n + PostgreSQL workflow engine with pre-configured webhooks sold as a recurring managed asset ($399/mo).",
            8.0
        ),
        "DATA_ETL_ANALYTICS": (
            ReframedAssetType.PROPRIETARY_DATASET,
            "Manually parse invoices into Excel spreadsheets for $20/hr",
            "Multi-format deterministic extraction pipeline with automated schema validation and export connectors, sold as a per-document API license.",
            12.5
        ),
        "KNOWLEDGE_ONBOARDING": (
            ReframedAssetType.SELF_HOSTED_PLAYBOOK,
            "Answer junior developers' questions one-by-one in Slack",
            "Localized engineering onboarding engine indexing Git commits and architecture decision records, eliminating 10+ hours of senior dev interruption weekly.",
            10.0
        ),
        "COMPLIANCE_SECURITY": (
            ReframedAssetType.COMPLIANCE_AUDIT_PACK,
            "Spend 3 weeks manually screenshotting AWS IAM consoles",
            "Audit-ready Infrastructure-as-Code Terraform compliance pack with automated GitHub Actions verification, sold as a flat $2,500 deployment asset.",
            15.0
        ),
        "DEVELOPER_TOOLING": (
            ReframedAssetType.MICRO_SAAS_ENGINE,
            "Manually optimize API prompts and fix timeout errors",
            "Self-hosted LLM gateway proxy with semantic caching and cost alerting, reducing API bills by 60% autonomously.",
            20.0
        ),
    }

    def reframe(
        self,
        category: str,
        obstacle: ObstacleNode,
        intersection: CapabilityIntersection,
        persona: str = "B2B SaaS Founders & Tech Leads"
    ) -> GroundedBuyerReliefStatement:
        cat_key = category.upper()
        if cat_key not in self.ASSET_MAPPING:
            cat_key = "WORKFLOW_AUTOMATION"

        asset_type, default_labor, default_asset, leverage = self.ASSET_MAPPING[cat_key]

        citation = obstacle.citations[0] if obstacle.citations else "CORPUS-GENERAL"

        relief_mechanism = (
            f"Applies {intersection.leverage_description} to permanently eliminate '{obstacle.label}' "
            f"via automated architecture, bypassing manual labor dependency."
        )

        return GroundedBuyerReliefStatement(
            statement_id=f"RELIEF-{obstacle.obstacle_id}",
            target_persona=persona,
            obstacle_id=obstacle.obstacle_id,
            relief_mechanism=relief_mechanism,
            evidence_citation=citation,
            asset_type=asset_type,
            labor_framing=default_labor,
            asset_reframing=default_asset,
            multiplicative_leverage_ratio=leverage
        )
