from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel

from src.agentic_os.runtime.mcp_client import MCPStdioClient
from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.ingestion.profiler import ProfilerAgent
from src.agentic_os.ingestion.contradiction import DecompositionPipeline
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.retrieval.triangulation import EvidenceTriangulator
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.graph.dual_graph import DualGraphTranslationLayer
from src.agentic_os.agents.offer_diagnosis import OfferDiagnosisAgent
from src.agentic_os.agents.product_suite import ProductSuiteGenerationAgent
from src.agentic_os.orchestrator.confidence import ConfidenceEvaluator


class RegisteredTool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    source: str = "native"  # "native" or "mcp:<server_name>"


class ToolRegistry:
    """Unified tool registry supporting both native Python tools and live MCP server tools."""

    def __init__(self, attach_mcp: bool = False):
        self._tools: Dict[str, RegisteredTool] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._mcp_client: Optional[MCPStdioClient] = None

        self._register_native_tools()
        if attach_mcp:
            self.attach_mcp_server()

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
        source: str = "native"
    ) -> None:
        self._tools[name] = RegisteredTool(
            name=name,
            description=description,
            input_schema=input_schema,
            source=source
        )
        self._handlers[name] = handler

    def attach_mcp_server(self, server_name: str = "agentic-os-engine") -> int:
        """Discovers tools from a live MCP server over stdio and registers them."""
        self._mcp_client = MCPStdioClient(server_name=server_name)
        mcp_tools = self._mcp_client.list_tools()
        count = 0
        for t in mcp_tools:
            t_name = t["name"]
            self.register_tool(
                name=t_name,
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", {"type": "object", "properties": {}}),
                handler=lambda args, _n=t_name: self._mcp_client.call_tool(_n, args),
                source=f"mcp:{server_name}"
            )
            count += 1
        return count

    def _register_native_tools(self) -> None:
        profiler = ProfilerAgent()
        decomp = DecompositionPipeline()
        retriever = MarketEvidenceRetriever()
        triangulator = EvidenceTriangulator()
        extractor = BuyerObstacleChainExtractor()
        dual_graph = DualGraphTranslationLayer()
        offer_agent = OfferDiagnosisAgent()
        suite_agent = ProductSuiteGenerationAgent()

        self.register_tool(
            name="ingest_profile",
            description="Parse founder raw bio, skills, and constraints into a structured FounderProfile.",
            input_schema={
                "type": "object",
                "properties": {
                    "founder_name": {"type": "string"},
                    "bio": {"type": "string"},
                    "skills_text": {"type": "string"},
                    "available_hours": {"type": "number"},
                    "budget_usd": {"type": "number"}
                },
                "required": ["founder_name", "skills_text"]
            },
            handler=lambda args: profiler.parse_profile(
                founder_name=args.get("founder_name", "Founder"),
                bio=args.get("bio", "Software Engineer"),
                skills_text=args.get("skills_text", "python"),
                available_hours=float(args.get("available_hours", 15.0)),
                budget_usd=float(args.get("budget_usd", 500.0))
            ).model_dump()
        )

        self.register_tool(
            name="decompose_capabilities",
            description="Cluster founder skills, mine cross-cluster intersections, and check feasibility contradictions.",
            input_schema={
                "type": "object",
                "properties": {
                    "founder_name": {"type": "string"},
                    "bio": {"type": "string"},
                    "skills_text": {"type": "string"}
                },
                "required": ["founder_name", "skills_text"]
            },
            handler=lambda args: decomp.process(
                profiler.parse_profile(
                    founder_name=args.get("founder_name", "Founder"),
                    bio=args.get("bio", "Software Engineer"),
                    skills_text=args.get("skills_text", "python")
                )
            ).model_dump()
        )

        self.register_tool(
            name="retrieve_evidence",
            description="Retrieve and triangulate real-world buyer friction evidence across forums, reviews, jobs, and reports.",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [c.value for c in OutcomeCategory]
                    }
                },
                "required": ["category"]
            },
            handler=lambda args: triangulator.triangulate(
                OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION")),
                retriever.retrieve_for_category(OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION")))
            ).model_dump()
        )

        self.register_tool(
            name="extract_obstacle_chain",
            description="Extract chronologically ordered buyer obstacle chain (BEFORE_ATTEMPT, DURING_EXECUTION, AFTER_COMPLETION).",
            input_schema={
                "type": "object",
                "properties": {"category": {"type": "string"}},
                "required": ["category"]
            },
            handler=lambda args: extractor.extract_chain(
                OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION")),
                retriever.retrieve_for_category(OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION")))
            ).model_dump()
        )

        self.register_tool(
            name="translate_dual_graph",
            description="Build bipartite Capability-to-Buyer Dual Graph with Ownership-Mindset labor-to-asset reframing.",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "skills_text": {"type": "string"}
                },
                "required": ["category", "skills_text"]
            },
            handler=lambda args: self._run_dual_graph(args, profiler, decomp, retriever, extractor, dual_graph)
        )

        self.register_tool(
            name="diagnose_offer_value",
            description="Compute Hormozi Value Equation ((Dream * Likelihood) / (Time * Effort)) and identify bottleneck.",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "skills_text": {"type": "string"}
                },
                "required": ["category"]
            },
            handler=lambda args: self._run_offer_diag(args, profiler, decomp, retriever, extractor, offer_agent)
        )

        self.register_tool(
            name="generate_product_suite",
            description="Generate 3-tier compounding asset product suite (Lead Magnet, Core Offer, Recurring Backend).",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "skills_text": {"type": "string"}
                },
                "required": ["category"]
            },
            handler=lambda args: self._run_product_suite(args, profiler, decomp, retriever, extractor, suite_agent)
        )

    def _run_dual_graph(self, args, profiler, decomp, retriever, extractor, dual_graph):
        cat = OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION"))
        prof = profiler.parse_profile("Founder", "Engineer", args.get("skills_text", "python, n8n"))
        d = decomp.process(prof)
        chain = extractor.extract_chain(cat, retriever.retrieve_for_category(cat))
        return dual_graph.construct_dual_graph(d.clusters, d.intersections, chain).model_dump()

    def _run_offer_diag(self, args, profiler, decomp, retriever, extractor, offer_agent):
        cat = OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION"))
        prof = profiler.parse_profile("Founder", "Engineer", args.get("skills_text", "python, n8n"))
        d = decomp.process(prof)
        chain = extractor.extract_chain(cat, retriever.retrieve_for_category(cat))
        inter = d.intersections[0] if d.intersections else None
        if inter is None:
            from src.agentic_os.schemas.profile import CapabilityIntersection
            inter = CapabilityIntersection(
                intersection_id="INT-FALLBACK",
                cluster_names=["Engineering"],
                combined_capabilities=["Python"],
                uniqueness_score=0.80,
                leverage_description="Systems automation",
                defensibility_hypothesis="Custom code"
            )
        return offer_agent.diagnose_offer(cat.value, chain, inter).model_dump()

    def _run_product_suite(self, args, profiler, decomp, retriever, extractor, suite_agent):
        cat = OutcomeCategory(args.get("category", "WORKFLOW_AUTOMATION"))
        prof = profiler.parse_profile("Founder", "Engineer", args.get("skills_text", "python, n8n"))
        d = decomp.process(prof)
        chain = extractor.extract_chain(cat, retriever.retrieve_for_category(cat))
        inter = d.intersections[0] if d.intersections else None
        return suite_agent.generate_suite(cat.value, chain, inter).model_dump()

    def list_tools(self) -> List[RegisteredTool]:
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[RegisteredTool]:
        return self._tools.get(name)

    def get_ollama_tool_schemas(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Formats tools for Ollama's /api/chat tool-calling specification."""
        selected = self._tools.values() if tool_names is None else [self._tools[n] for n in tool_names if n in self._tools]
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema
                }
            }
            for t in selected
        ]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name not in self._handlers:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self._handlers[name](arguments)

    def close(self) -> None:
        if self._mcp_client is not None:
            self._mcp_client.close()
            self._mcp_client = None
