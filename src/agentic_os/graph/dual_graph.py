import networkx as nx
from typing import List, Dict, Tuple
from src.agentic_os.schemas.profile import CapabilityCluster, CapabilityIntersection
from src.agentic_os.schemas.obstacle import ObstacleChain, ObstacleNode
from src.agentic_os.schemas.graph import (
    GraphNode,
    GraphEdge,
    DualGraphData,
    GroundedBuyerReliefStatement,
)
from src.agentic_os.graph.reframing import OwnershipMindsetReframer


class DualGraphTranslationLayer:
    """Agent 5: Dual-Graph Translation Layer.
    Connects technical capabilities to evidence-grounded buyer outcomes via causal mechanisms.
    """

    def __init__(self):
        self.reframer = OwnershipMindsetReframer()

    def construct_dual_graph(
        self,
        clusters: List[CapabilityCluster],
        intersections: List[CapabilityIntersection],
        obstacle_chain: ObstacleChain,
        target_persona: str = "Technical Founders & Operations Leaders"
    ) -> DualGraphData:
        G = nx.DiGraph()

        capability_nodes: List[GraphNode] = []
        buyer_nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        relief_statements: List[GroundedBuyerReliefStatement] = []

        # 1. Populate Capability Subgraph
        for clus in clusters:
            node_id = f"CAP_CLUS_{clus.cluster_id}"
            capability_nodes.append(
                GraphNode(
                    id=node_id,
                    label=clus.name,
                    graph_type="CAPABILITY",
                    attributes={"cohesion": clus.cohesion_score, "skills": clus.capabilities}
                )
            )
            G.add_node(node_id, type="CAPABILITY_CLUSTER")

            for cap in clus.capabilities:
                cap_id = f"CAP_{cap.replace(' ', '_')}"
                capability_nodes.append(
                    GraphNode(
                        id=cap_id,
                        label=cap,
                        graph_type="CAPABILITY",
                        attributes={"cluster": clus.name}
                    )
                )
                G.add_node(cap_id, type="CAPABILITY")
                G.add_edge(node_id, cap_id, relation="CONTAINS")
                edges.append(GraphEdge(source=node_id, target=cap_id, relation="CONTAINS", weight=1.0))

        # 2. Populate Buyer Friction Subgraph
        prev_obs_id = None
        for obs in obstacle_chain.ordered_obstacles:
            node_id = f"BUYER_OBS_{obs.obstacle_id}"
            buyer_nodes.append(
                GraphNode(
                    id=node_id,
                    label=obs.label,
                    graph_type="BUYER",
                    attributes={"phase": obs.phase.value, "severity": obs.severity}
                )
            )
            G.add_node(node_id, type="BUYER_OBSTACLE", severity=obs.severity)

            if prev_obs_id:
                G.add_edge(prev_obs_id, node_id, relation="PROGRESSES_TO")
                edges.append(GraphEdge(source=prev_obs_id, target=node_id, relation="PROGRESSES_TO", weight=1.0))
            prev_obs_id = node_id

        # 3. Cross-Graph Bipartite Translation & Reframing Pass
        primary_intersection = intersections[0] if intersections else CapabilityIntersection(
            intersection_id="INT-GEN",
            cluster_names=["General"],
            combined_capabilities=["Engineering"],
            uniqueness_score=0.75,
            leverage_description="Full-stack system integration",
            defensibility_hypothesis="Execution velocity and custom code"
        )

        for obs in obstacle_chain.ordered_obstacles:
            # Generate grounded relief statement with ownership mindset
            statement = self.reframer.reframe(
                category=obstacle_chain.target_category,
                obstacle=obs,
                intersection=primary_intersection,
                persona=target_persona
            )
            relief_statements.append(statement)

            # Add relief node and cross-graph edges
            relief_node_id = f"BUYER_RELIEF_{obs.obstacle_id}"
            buyer_nodes.append(
                GraphNode(
                    id=relief_node_id,
                    label=f"Relief: {obs.label}",
                    graph_type="BUYER",
                    attributes={"asset_type": statement.asset_type.value, "leverage": statement.multiplicative_leverage_ratio}
                )
            )
            G.add_node(relief_node_id, type="RELIEF_OUTCOME")

            # Link buyer obstacle to relief
            G.add_edge(f"BUYER_OBS_{obs.obstacle_id}", relief_node_id, relation="RELIEVED_BY")
            edges.append(GraphEdge(source=f"BUYER_OBS_{obs.obstacle_id}", target=relief_node_id, relation="RELIEVED_BY", weight=1.5))

            # Cross-graph causal edges from all relevant capability clusters to buyer relief
            linked_any = False
            for clus in clusters:
                # Link cluster if it participates in the active intersection or if no intersection exists
                if not intersections or any(
                    any(cn in clus.name for cn in inter.cluster_names)
                    for inter in intersections
                ):
                    cap_source = f"CAP_CLUS_{clus.cluster_id}"
                    G.add_edge(cap_source, relief_node_id, relation="CAUSAL_MECHANISM")
                    edges.append(GraphEdge(source=cap_source, target=relief_node_id, relation="CAUSAL_MECHANISM", weight=2.0))
                    linked_any = True
            if not linked_any and clusters:
                cap_source = f"CAP_CLUS_{clusters[0].cluster_id}"
                G.add_edge(cap_source, relief_node_id, relation="CAUSAL_MECHANISM")
                edges.append(GraphEdge(source=cap_source, target=relief_node_id, relation="CAUSAL_MECHANISM", weight=2.0))

        return DualGraphData(
            capability_nodes=capability_nodes,
            buyer_nodes=buyer_nodes,
            edges=edges,
            relief_statements=relief_statements
        )
