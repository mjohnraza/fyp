from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    FORUM = "FORUM"                     # e.g., Reddit, Hacker News, niche communities
    REVIEW = "REVIEW"                   # e.g., G2, Capterra, Trustpilot
    JOB_POSTING = "JOB_POSTING"         # e.g., Upwork, Indeed, LinkedIn job descriptions
    INDUSTRY_REPORT = "INDUSTRY_REPORT" # e.g., Gartner, Forrester, academic case studies


class OutcomeCategory(str, Enum):
    WORKFLOW_AUTOMATION = "WORKFLOW_AUTOMATION"
    DATA_ETL_ANALYTICS = "DATA_ETL_ANALYTICS"
    KNOWLEDGE_ONBOARDING = "KNOWLEDGE_ONBOARDING"
    COMPLIANCE_SECURITY = "COMPLIANCE_SECURITY"
    DEVELOPER_TOOLING = "DEVELOPER_TOOLING"


class EvidenceSnippet(BaseModel):
    snippet_id: str
    category: OutcomeCategory
    source_type: SourceType
    source_title: str
    source_url_or_ref: str
    raw_quote: str
    pain_point_summary: str
    frequency_weight: float = Field(1.0, ge=0.1, le=10.0)
    publication_date: Optional[str] = "2026-Q1"


class TriangulatedEvidence(BaseModel):
    category: OutcomeCategory
    snippets: List[EvidenceSnippet]
    source_types_represented: List[SourceType]
    source_diversity_count: int
    triangulation_passed: bool
    triangulation_ratio: float = Field(..., ge=0.0, le=1.0)
