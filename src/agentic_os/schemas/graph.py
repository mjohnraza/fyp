from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ReframedAssetType(str, Enum):
    SELF_HOSTED_PLAYBOOK = "SELF_HOSTED_PLAYBOOK"           # Structured guide/system that compiles knowledge
    AUTOMATION_WORKFLOW = "AUTOMATION_WORKFLOW"             # Pre-configured n8n / script pipeline
    PROPRIETARY_DATASET = "PROPRIETARY_DATASET"             # Curated, cleaned, domain-specific data asset
    MICRO_SAAS_ENGINE = "MICRO_SAAS_ENGINE"                 # Lightweight hosted API or dashboard
    COMPLIANCE_AUDIT_PACK = "COMPLIANCE_AUDIT_PACK"         # Automated evaluation checklist and test harness


class GroundedBuyerReliefStatement(BaseModel):
    statement_id: str
    target_persona: str = Field(..., description="E.g., Solo B2B SaaS Founders, Small Marketing Agency Ops Leads")
    obstacle_id: str = Field(..., description="ID of the obstacle being relieved")
    relief_mechanism: str = Field(..., description="Causal mechanism: how technical capability solves the friction")
    evidence_citation: str = Field(..., description="ID or title of corroborating market evidence")
    asset_type: ReframedAssetType
    labor_framing: str = Field(..., description="Additive hourly-service framing (to avoid)")
    asset_reframing: str = Field(..., description="Multiplicative compounding-asset framing (Ownership Mindset)")
    multiplicative_leverage_ratio: float = Field(..., ge=1.0, description="Estimated asset-to-labor efficiency multiplier")


class GraphNode(BaseModel):
    id: str
    label: str
    graph_type: str  # "CAPABILITY" or "BUYER"
    attributes: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str    # "PREREQUISITE", "SYNERGY", "CAUSES", "RELIEVES"
    weight: float = 1.0


class DualGraphData(BaseModel):
    capability_nodes: List[GraphNode]
    buyer_nodes: List[GraphNode]
    edges: List[GraphEdge]
    relief_statements: List[GroundedBuyerReliefStatement]
