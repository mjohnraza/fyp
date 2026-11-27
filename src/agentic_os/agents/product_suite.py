from typing import Dict, Any, Optional
from src.agentic_os.schemas.offer import ProductSuite, ProductTier, ProductTierType
from src.agentic_os.schemas.obstacle import ObstacleChain
from src.agentic_os.schemas.profile import CapabilityIntersection


class ProductSuiteGenerationAgent:
    """Agent 9: Generates a 3-tier Funnel Architecture (De Giovanni [9], Hormozi [8]):
    - Tier 1: Lead Magnet / Low-Friction Entry Point
    - Tier 2: Core High-Value Offer
    - Tier 3: Compounding Asset Backend
    """

    SUITE_TEMPLATES: Dict[str, Dict[str, Any]] = {
        "WORKFLOW_AUTOMATION": {
            "niche": "High-Volume B2B SaaS Ops & Agencies",
            "lead": {
                "title": "Webhook Health & Schema Mutation Audit Script",
                "tagline": "Find silent API drops in your Zapier/Make pipeline in 10 minutes",
                "hours": 1.0,
                "price": 0.0,
                "deliverables": ["Automated Python diagnostic script", "Schema drift report checklist"],
                "scalability": "Zero marginal cost distribution via GitHub repo"
            },
            "core": {
                "title": "Turnkey Resilient n8n + Postgres Automation Engine",
                "tagline": "Bulletproof workflow pipeline with dead-letter queueing and retries",
                "hours": 8.0,
                "price": 1497.0,
                "deliverables": [
                    "Dockerized multi-tenant n8n deployment",
                    "Custom retry queue and email/Slack alerting harness",
                    "2 custom production workflow migrations"
                ],
                "scalability": "Pre-built Terraform and Docker templates reduce custom build time by 80%"
            },
            "backend": {
                "title": "Autonomous Pipeline SRE & Managed Workflow Retainer",
                "tagline": "Continuous schema monitoring, zero-downtime updates, and priority fixes",
                "hours": 2.0,
                "price": 399.0,
                "deliverables": ["24/7 uptime monitoring", "Monthly API migration patching", "Incident response SLA"],
                "scalability": "Pooled monitoring alerts handled by automated diagnostic agents"
            }
        },
        "DATA_ETL_ANALYTICS": {
            "niche": "Mid-Market Finance & Logistics Operations",
            "lead": {
                "title": "PDF Invoice Chaos Benchmark & Accuracy Auditor",
                "tagline": "Test your document OCR error rate against deterministic extraction benchmarks",
                "hours": 1.0,
                "price": 0.0,
                "deliverables": ["Sample parser test suite", "Error rate spreadsheet calculator"],
                "scalability": "Self-serve web UI"
            },
            "core": {
                "title": "Deterministic Multi-Layout Invoice & Table Extraction Engine",
                "tagline": "Zero-hallucination invoice to ERP pipeline with human review dashboard",
                "hours": 10.0,
                "price": 2497.0,
                "deliverables": [
                    "Custom document schema parser",
                    "Human-in-the-loop validation UI",
                    "Direct ERP/PostgreSQL connector"
                ],
                "scalability": "Core parsing engine modularly accepts new document templates in < 15 mins"
            },
            "backend": {
                "title": "Enterprise Document Parsing API License & New Template Service",
                "tagline": "Per-document micro-metering and ongoing vendor layout support",
                "hours": 2.5,
                "price": 499.0,
                "deliverables": ["10,000 monthly document API quota", "Up to 3 new vendor layouts added/mo"],
                "scalability": "Serverless containerized pipeline scales on AWS Lambda"
            }
        },
        "COMPLIANCE_SECURITY": {
            "niche": "Seed/Series A Startups Facing Enterprise SOC2/ISO 27001 Audits",
            "lead": {
                "title": "15-Minute AWS Infrastructure Compliance Readiness CLI",
                "tagline": "Instant audit score of your AWS accounts against SOC2 Trust Criteria",
                "hours": 0.5,
                "price": 0.0,
                "deliverables": ["CLI tool executable", "Executive compliance PDF score"],
                "scalability": "Compiled Go/Python CLI"
            },
            "core": {
                "title": "Audit-Ready Terraform & GitHub Actions Compliance Pack",
                "tagline": "Automate 90% of evidence collection and remediate IAM/S3 gaps in 48 hours",
                "hours": 12.0,
                "price": 3500.0,
                "deliverables": [
                    "IaC compliance policies (Terraform / OpenTofu)",
                    "Automated daily screenshot & artifact harvest pipeline",
                    "Auditor-ready evidence directory binder"
                ],
                "scalability": "Reusable policy modules across AWS/GCP"
            },
            "backend": {
                "title": "Continuous Drift Detection & Annual Re-certification Sentinel",
                "tagline": "Alerting when engineers deploy insecure resources before your auditor notices",
                "hours": 1.5,
                "price": 599.0,
                "deliverables": ["Continuous CI/CD policy enforcement", "Annual audit rerun package"],
                "scalability": "Automated webhook checking via GitHub Actions"
            }
        }
    }

    def generate_suite(
        self,
        category: str,
        obstacle_chain: ObstacleChain,
        intersection: Optional[CapabilityIntersection] = None
    ) -> ProductSuite:
        cat_key = category.upper()
        if cat_key not in self.SUITE_TEMPLATES:
            cat_key = "WORKFLOW_AUTOMATION"

        tmpl = self.SUITE_TEMPLATES[cat_key]
        primary_obs_label = (
            obstacle_chain.ordered_obstacles[0].label
            if obstacle_chain.ordered_obstacles
            else "Operational Friction"
        )
        cap_summary = (
            ", ".join(intersection.combined_capabilities[:3])
            if intersection and intersection.combined_capabilities
            else "Core Engineering Stack"
        )

        lead = ProductTier(
            tier=ProductTierType.LEAD_MAGNET,
            title=tmpl["lead"]["title"],
            tagline=f"{tmpl['lead']['tagline']} (Targets: {primary_obs_label})",
            target_delivery_hours=tmpl["lead"]["hours"],
            price_point_usd=tmpl["lead"]["price"],
            is_recurring=False,
            deliverables=list(tmpl["lead"]["deliverables"]),
            scalability_mechanic=tmpl["lead"]["scalability"]
        )

        core_deliverables = list(tmpl["core"]["deliverables"]) + [
            f"Built on founder intersection: {cap_summary}"
        ]
        core = ProductTier(
            tier=ProductTierType.CORE_OFFER,
            title=tmpl["core"]["title"],
            tagline=tmpl["core"]["tagline"],
            target_delivery_hours=tmpl["core"]["hours"],
            price_point_usd=tmpl["core"]["price"],
            is_recurring=False,
            deliverables=core_deliverables,
            scalability_mechanic=tmpl["core"]["scalability"]
        )

        backend = ProductTier(
            tier=ProductTierType.COMPOUNDING_BACKEND,
            title=tmpl["backend"]["title"],
            tagline=tmpl["backend"]["tagline"],
            target_delivery_hours=tmpl["backend"]["hours"],
            price_point_usd=tmpl["backend"]["price"],
            is_recurring=True,
            deliverables=list(tmpl["backend"]["deliverables"]),
            scalability_mechanic=tmpl["backend"]["scalability"]
        )

        # Lifetime Value calculation: Core + 12 months of recurring backend
        ltv = core.price_point_usd + (backend.price_point_usd * 12)

        thesis = (
            f"The free lead magnet removes adoption resistance around '{primary_obs_label}'. "
            f"Delivering the core offer leverages {cap_summary} to solve the immediate fire, "
            f"while the recurring backend converts labor into an accumulating, compounding asset stream."
        )

        return ProductSuite(
            suite_id=f"SUITE-{cat_key[:4]}",
            target_niche=tmpl["niche"],
            lead_magnet=lead,
            core_offer=core,
            backend_asset=backend,
            total_lifetime_value_estimate_usd=round(ltv, 2),
            funnel_conversion_thesis=thesis
        )
