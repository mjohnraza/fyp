import re
import uuid
from typing import Optional, Dict, Any, List
from src.agentic_os.schemas.profile import (
    FounderProfile,
    CapabilityItem,
    ContextItem,
    ConstraintItem,
    ProficiencyLevel
)


class ProfilerAgent:
    """Agent 1a: Structures raw intake into a standardized FounderProfile."""

    SKILL_KEYWORD_MAP = {
        "python": ("Python Development", "Engineering"),
        "fastapi": ("FastAPI & Microservices", "Engineering"),
        "docker": ("Docker & Containerization", "DevOps"),
        "sql": ("SQL & Relational Databases", "Data"),
        "postgresql": ("PostgreSQL Optimization", "Data"),
        "rag": ("Retrieval-Augmented Generation (RAG)", "AI/NLP"),
        "llm": ("LLM Integration & Prompt Engineering", "AI/NLP"),
        "langchain": ("LangChain / LangGraph Agent Systems", "AI/NLP"),
        "etl": ("ETL Pipelines & Data Ingestion", "Data"),
        "n8n": ("n8n Workflow Automation", "Automation"),
        "zapier": ("Zapier Integration", "Automation"),
        "soc2": ("SOC2 Compliance Standards", "Security/Compliance"),
        "iso": ("ISO 27001 Readiness", "Security/Compliance"),
        "react": ("React Frontend Development", "Engineering"),
        "typescript": ("TypeScript Development", "Engineering"),
    }

    def parse_profile(
        self,
        founder_name: str,
        bio: str,
        skills_text: str,
        available_hours: float = 15.0,
        budget_usd: float = 500.0,
        time_horizon_months: int = 6,
        industry: str = "Software & Technology"
    ) -> FounderProfile:
        capabilities: List[CapabilityItem] = []
        lower_text = (skills_text + " " + bio).lower()

        # Keyword mapping
        detected_names = set()
        for kw, (skill_name, category) in self.SKILL_KEYWORD_MAP.items():
            if kw in lower_text and skill_name not in detected_names:
                detected_names.add(skill_name)
                capabilities.append(
                    CapabilityItem(
                        name=skill_name,
                        category=category,
                        proficiency=ProficiencyLevel.ADVANCED,
                        proof=f"Extracted from profile text: '{kw}' mention",
                        years_experience=2.5
                    )
                )

        # Fallback if no matching keywords found
        if not capabilities:
            capabilities.append(
                CapabilityItem(
                    name="General Python Engineering",
                    category="Engineering",
                    proficiency=ProficiencyLevel.INTERMEDIATE,
                    proof="Self-reported general proficiency",
                    years_experience=1.5
                )
            )

        context = ContextItem(
            current_role="Freelance Developer / Engineer",
            primary_industry=industry,
            available_hours_per_week=available_hours
        )

        constraints = ConstraintItem(
            financial_budget_usd=budget_usd,
            time_horizon_months=time_horizon_months
        )

        return FounderProfile(
            id=f"prof-{uuid.uuid4().hex[:8]}",
            founder_name=founder_name,
            bio=bio,
            capabilities=capabilities,
            context=context,
            constraints=constraints,
            raw_text=f"{bio}\nSkills: {skills_text}"
        )
