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

    def _infer_proficiency(self, lower_text: str) -> ProficiencyLevel:
        if any(cue in lower_text for cue in ("principal", "staff", "architect", "world-class")):
            return ProficiencyLevel.EXPERT
        if any(cue in lower_text for cue in ("senior", "lead", "expert", "production")):
            return ProficiencyLevel.ADVANCED
        if any(cue in lower_text for cue in ("beginner", "junior", "learning", "student", "novice")):
            return ProficiencyLevel.NOVICE
        return ProficiencyLevel.INTERMEDIATE

    def _extract_years_experience(self, lower_text: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", lower_text)
        if match:
            return float(match.group(1))
        return 0.0

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

        inferred_proficiency = self._infer_proficiency(lower_text)
        extracted_years = self._extract_years_experience(lower_text)

        # Deterministic keyword mapping without fabricating expertise
        detected_names = set()
        for kw, (skill_name, category) in self.SKILL_KEYWORD_MAP.items():
            if re.search(rf"\b{re.escape(kw)}\b", lower_text) and skill_name not in detected_names:
                detected_names.add(skill_name)
                capabilities.append(
                    CapabilityItem(
                        name=skill_name,
                        category=category,
                        proficiency=inferred_proficiency,
                        proof=f"Keyword mention '{kw}' in profile text (unverified)",
                        years_experience=extracted_years
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
