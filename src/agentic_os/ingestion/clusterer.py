from typing import List, Dict
from src.agentic_os.schemas.profile import FounderProfile, CapabilityCluster


class ClustererAgent:
    """Agent 1b: Clusters capabilities into cohesive functional capability domains."""

    def cluster_capabilities(self, profile: FounderProfile) -> List[CapabilityCluster]:
        category_map: Dict[str, List[str]] = {}
        for cap in profile.capabilities:
            category_map.setdefault(cap.category, []).append(cap.name)

        clusters: List[CapabilityCluster] = []
        cluster_counter = 1

        for cat, cap_list in category_map.items():
            cluster_id = f"CLUS-{cluster_counter:02d}"
            name = f"{cat} Capability Cluster"
            desc = f"Synergistic expertise covering {', '.join(cap_list)}."
            cohesion = 0.80 + (0.04 * min(len(cap_list), 5))
            clusters.append(
                CapabilityCluster(
                    cluster_id=cluster_id,
                    name=name,
                    description=desc,
                    capabilities=cap_list,
                    cohesion_score=min(cohesion, 0.98)
                )
            )
            cluster_counter += 1

        return clusters
