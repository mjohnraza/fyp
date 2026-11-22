from itertools import combinations
from typing import List
from src.agentic_os.schemas.profile import CapabilityCluster, CapabilityIntersection


class IntersectionMinerAgent:
    """Agent 2: Identifies cross-cluster capability combinations that yield high-leverage assets."""

    INTERSECTION_HEURISTICS = {
        ("Engineering", "AI/NLP"): (
            "Agentic Software Engineering",
            "Combines production API resilience with LLM autonomous tool calling. Unlocks self-healing backends.",
            "High defensibility: pure prompt wrappers break; engineering rigour prevents system collapse."
        ),
        ("Automation", "Data"): (
            "Automated ETL & Pipeline Intelligence",
            "Combines webhook orchestration with structured data transformation. Solves manual data entry bottlenecks.",
            "High defensibility: customized schema mapping creates deep switching costs for client workflows."
        ),
        ("AI/NLP", "Security/Compliance"): (
            "Auditable Agentic Compliance Automation",
            "Combines semantic parsing with deterministic audit frameworks. Replaces 6-week manual SOC2/ISO evidence gathering.",
            "Very high defensibility: regulatory compliance requires high accuracy and audit trails that off-the-shelf bots cannot handle."
        ),
        ("Engineering", "Automation"): (
            "Resilient Multi-Tenant Workflow Systems",
            "Replaces fragile no-code setups with robust Dockerized event runners.",
            "Moderate-to-high defensibility: enterprise buyers distrust brittle Zapier chains but pay retainers for code-backed engines."
        ),
    }

    def mine_intersections(self, clusters: List[CapabilityCluster]) -> List[CapabilityIntersection]:
        intersections: List[CapabilityIntersection] = []
        cluster_names = [c.name.replace(" Capability Cluster", "") for c in clusters]

        counter = 1
        for c1, c2 in combinations(cluster_names, 2):
            key = (c1, c2)
            rev_key = (c2, c1)

            if key in self.INTERSECTION_HEURISTICS:
                title, leverage, defense = self.INTERSECTION_HEURISTICS[key]
            elif rev_key in self.INTERSECTION_HEURISTICS:
                title, leverage, defense = self.INTERSECTION_HEURISTICS[rev_key]
            else:
                title = f"{c1} + {c2} Hybrid Leverage"
                leverage = f"Synthesizes capabilities from {c1} and {c2} to unlock proprietary workflow efficiencies."
                defense = "Cross-domain synthesis raises the barrier to entry compared to single-skill competitors."

            # Collect capabilities from both clusters
            cap1 = next((c.capabilities for c in clusters if c1 in c.name), [])
            cap2 = next((c.capabilities for c in clusters if c2 in c.name), [])

            intersections.append(
                CapabilityIntersection(
                    intersection_id=f"INT-{counter:02d}",
                    cluster_names=[c1, c2],
                    combined_capabilities=list(set(cap1 + cap2)),
                    uniqueness_score=0.88,
                    leverage_description=leverage,
                    defensibility_hypothesis=defense
                )
            )
            counter += 1

        return intersections
