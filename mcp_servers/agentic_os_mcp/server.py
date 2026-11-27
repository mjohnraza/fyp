import sys
import json
import traceback
from typing import Any, Dict, List

from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.ingestion.profiler import ProfilerAgent
from src.agentic_os.ingestion.contradiction import DecompositionPipeline
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.retrieval.triangulation import EvidenceTriangulator
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.graph.dual_graph import DualGraphTranslationLayer
from src.agentic_os.agents.offer_diagnosis import OfferDiagnosisAgent
from src.agentic_os.agents.product_suite import ProductSuiteGenerationAgent
from src.agentic_os.orchestrator.pipeline import MasterOrchestrator

TOOLS = [
    {
        "name": "ingest_profile",
        "description": "Parse founder raw background, skills, and constraints into a standardized profile.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "founder_name": {"type": "string", "description": "Name of founder"},
                "bio": {"type": "string", "description": "Professional background"},
                "skills_text": {"type": "string", "description": "List of technical skills and tools"},
                "available_hours": {"type": "number", "default": 15.0},
                "budget_usd": {"type": "number", "default": 500.0}
            },
            "required": ["founder_name", "skills_text"]
        }
    },
    {
        "name": "decompose_capabilities",
        "description": "Decompose founder capabilities into clusters, cross-cluster intersections, and flag feasibility contradictions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "founder_name": {"type": "string"},
                "skills_text": {"type": "string"},
                "bio": {"type": "string", "default": "Software engineer"}
            },
            "required": ["founder_name", "skills_text"]
        }
    },
    {
        "name": "retrieve_evidence",
        "description": "Retrieve triangulated real-world buyer friction evidence across forums, reviews, jobs, and reports.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "WORKFLOW_AUTOMATION",
                        "DATA_ETL_ANALYTICS",
                        "KNOWLEDGE_ONBOARDING",
                        "COMPLIANCE_SECURITY",
                        "DEVELOPER_TOOLING"
                    ],
                    "default": "WORKFLOW_AUTOMATION"
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "extract_obstacle_chain",
        "description": "Extract chronologically ordered buyer obstacle chain (before attempt, during execution, after completion).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "default": "WORKFLOW_AUTOMATION"}
            },
            "required": ["category"]
        }
    },
    {
        "name": "diagnose_offer_value",
        "description": "Formalize Alex Hormozi's Value Equation ((Dream * Likelihood) / (Time * Effort)) and identify bottleneck.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "default": "WORKFLOW_AUTOMATION"}
            },
            "required": ["category"]
        }
    },
    {
        "name": "generate_founder_decision_memo",
        "description": "Execute complete 13-agent pipeline with confidence scoring, human checkpoints, and generate Founder Decision Memo (requires explicit confirm_checkpoint=True).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "founder_name": {"type": "string"},
                "skills_text": {"type": "string"},
                "category": {"type": "string", "default": "WORKFLOW_AUTOMATION"},
                "available_hours": {"type": "number", "default": 15.0},
                "budget_usd": {"type": "number", "default": 500.0},
                "confirm_checkpoint": {"type": "boolean", "default": False, "description": "Explicit founder approval required to unlock memo"}
            },
            "required": ["founder_name", "skills_text"]
        }
    }
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    profiler = ProfilerAgent()
    decomp_pipeline = DecompositionPipeline()
    retriever = MarketEvidenceRetriever()
    triangulator = EvidenceTriangulator()
    extractor = BuyerObstacleChainExtractor()
    dual_graph = DualGraphTranslationLayer()
    offer_agent = OfferDiagnosisAgent()
    orchestrator = MasterOrchestrator()

    if name == "ingest_profile":
        prof = profiler.parse_profile(
            founder_name=arguments.get("founder_name", "Founder"),
            bio=arguments.get("bio", "Software Engineer"),
            skills_text=arguments.get("skills_text", "Python"),
            available_hours=float(arguments.get("available_hours", 15.0)),
            budget_usd=float(arguments.get("budget_usd", 500.0))
        )
        return prof.model_dump()

    elif name == "decompose_capabilities":
        prof = profiler.parse_profile(
            founder_name=arguments.get("founder_name", "Founder"),
            bio=arguments.get("bio", "Software Engineer"),
            skills_text=arguments.get("skills_text", "Python")
        )
        decomp = decomp_pipeline.process(prof)
        return decomp.model_dump()

    elif name == "retrieve_evidence":
        cat_str = arguments.get("category", "WORKFLOW_AUTOMATION")
        cat = OutcomeCategory(cat_str)
        snippets = retriever.retrieve_for_category(cat)
        triangulated = triangulator.triangulate(cat, snippets)
        return triangulated.model_dump()

    elif name == "extract_obstacle_chain":
        cat_str = arguments.get("category", "WORKFLOW_AUTOMATION")
        cat = OutcomeCategory(cat_str)
        snippets = retriever.retrieve_for_category(cat)
        chain = extractor.extract_chain(cat, snippets)
        return chain.model_dump()

    elif name == "diagnose_offer_value":
        cat_str = arguments.get("category", "WORKFLOW_AUTOMATION")
        cat = OutcomeCategory(cat_str)
        snippets = retriever.retrieve_for_category(cat)
        chain = extractor.extract_chain(cat, snippets)
        skills_text = arguments.get("skills_text", "python, fastapi, n8n")
        prof = profiler.parse_profile("Founder", "Engineer", skills_text)
        decomp = decomp_pipeline.process(prof)
        diag = offer_agent.diagnose_offer(cat.value, chain, decomp.intersections[0] if decomp.intersections else None)
        return diag.model_dump()

    elif name == "generate_founder_decision_memo":
        cat_str = arguments.get("category", "WORKFLOW_AUTOMATION")
        cat = OutcomeCategory(cat_str)
        confirm_cp = bool(arguments.get("confirm_checkpoint", False))
        result = orchestrator.run_pipeline(
            founder_name=arguments.get("founder_name", "Founder"),
            bio=arguments.get("bio", "Software engineer"),
            skills_text=arguments.get("skills_text", "python, fastapi, n8n"),
            category=cat,
            available_hours=float(arguments.get("available_hours", 15.0)),
            budget_usd=float(arguments.get("budget_usd", 500.0)),
            confirm_checkpoint=confirm_cp
        )
        memo_obj = result.get("founder_decision_memo")
        return {
            "status": result["status"],
            "scorecard": result["scorecard"].model_dump() if result.get("scorecard") else None,
            "human_checkpoint": result["human_checkpoint"].model_dump() if result.get("human_checkpoint") else None,
            "founder_decision_memo": memo_obj.model_dump() if memo_obj else None
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


def main():
    """Stdio JSON-RPC MCP server listener."""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line.strip())
            method = req.get("method")
            msg_id = req.get("id")

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "agentic-os-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass

            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                try:
                    tool_output = handle_tool_call(name, args)
                    res = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(tool_output, indent=2)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    res = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                            "isError": True
                        }
                    }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()

            elif method == "ping":
                res = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()

            else:
                if msg_id is not None:
                    res = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32601, "message": f"Method {method} not found"}
                    }
                    sys.stdout.write(json.dumps(res) + "\n")
                    sys.stdout.flush()

        except Exception as e:
            err = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
