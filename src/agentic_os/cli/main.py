import sys
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from src.agentic_os.orchestrator.pipeline import MasterOrchestrator
from src.agentic_os.schemas.corpus import OutcomeCategory

console = Console()


def print_banner():
    banner_text = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                 AGENTIC ENTREPRENEUR OS (FYP-I)                      ║
    ║       A Wealth-Formation Opportunity Discovery Pipeline              ║
    ║        Department of AI/CS - FAST NUCES Karachi (Fall 2026)          ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner_text}[/bold cyan]")


def run_interactive():
    print_banner()
    console.print("[bold yellow]Welcome to the Agentic Entrepreneur OS Core Prototype Pipeline.[/bold yellow]\n")

    founder_name = console.input("[bold green]Enter Founder Name [/bold green][default: Ahmed]: ") or "Ahmed"
    bio = console.input(
        "[bold green]Enter Bio/Background [/bold green][default: Senior Python backend engineer with 3 years building APIs]: "
    ) or "Senior Python backend engineer with 3 years building APIs"
    skills = console.input(
        "[bold green]Enter Skills list [/bold green][default: python, fastapi, n8n, docker, postgresql, rag]: "
    ) or "python, fastapi, n8n, docker, postgresql, rag"

    console.print("\n[bold]Select Target Outcome Domain:[/bold]")
    categories = list(OutcomeCategory)
    for idx, cat in enumerate(categories, 1):
        console.print(f"  {idx}. {cat.value}")
    cat_choice = console.input(f"[bold green]Select domain (1-{len(categories)}) [/bold green][default: 1]: ") or "1"
    try:
        selected_cat = categories[int(cat_choice) - 1]
    except Exception:
        selected_cat = OutcomeCategory.WORKFLOW_AUTOMATION

    hours = float(console.input("[bold green]Available hours per week [/bold green][default: 15.0]: ") or "15.0")
    budget = float(console.input("[bold green]Available budget (USD) [/bold green][default: 500.0]: ") or "500.0")

    console.print("\n[bold cyan]▶ Initiating 13-Agent Opportunity Discovery Pipeline...[/bold cyan]")

    orchestrator = MasterOrchestrator()
    result = orchestrator.run_pipeline(
        founder_name=founder_name,
        bio=bio,
        skills_text=skills,
        category=selected_cat,
        available_hours=hours,
        budget_usd=budget,
        confirm_checkpoint=True
    )

    memo = result["founder_decision_memo"]
    value_diag = result["value_diagnosis"]
    scorecard = result["scorecard"]

    # 1. Pipeline Execution Log
    console.print("\n[bold magenta]=== PIPELINE STAGE AUDIT TRAIL ===[/bold magenta]")
    for log in result["run_log"]:
        console.print(f"  ✓ {log}")

    # 2. Ten-Dimension Opportunity Scorecard Table
    console.print("\n[bold cyan]=== TABLE III: TEN-DIMENSION OPPORTUNITY SCORECARD ===[/bold cyan]")
    score_table = Table(title=f"Scorecard: {scorecard.opportunity_name}")
    score_table.add_column("Dimension", style="cyan", no_wrap=True)
    score_table.add_column("Score (0-10)", style="magenta")
    score_table.add_column("Grounding Source / Theoretical Anchor", style="green")

    score_table.add_row("Buyer Pain", f"{scorecard.buyer_pain}/10", "Agent 4 Obstacle-Chain Severity")
    score_table.add_row("Evidence Strength", f"{scorecard.evidence_strength}/10", "Agent 3 Multi-Source Triangulation")
    score_table.add_row("Capability Fit", f"{scorecard.capability_fit}/10", "Agent 1 Profile Ingestion & Constraints")
    score_table.add_row("Multiplicative Potential", f"{scorecard.multiplicative_potential}/10", "Bouchaud & Mézard [11] (Asset vs Labor)")
    score_table.add_row("Opportunity Surface Area", f"{scorecard.opportunity_surface_area}/10", "Pluchino et al. [12] (Distribution Breadth)")
    score_table.add_row("Defensibility", f"{scorecard.defensibility}/10", "Barney [15] (Resource-Based View)")
    score_table.add_row("AI Leverage", f"{scorecard.ai_leverage}/10", "Maresca [14] (Capital & Model Leverage)")
    score_table.add_row("Recurring Revenue Potential", f"{scorecard.recurring_revenue_potential}/10", "Funnel Recurring Backend Architecture")
    score_table.add_row("Asset Accumulation", f"{scorecard.asset_accumulation_potential}/10", "Penrose [16] (Firm Resource Compounding)")
    score_table.add_row("Risk / Validation Cost", f"{scorecard.risk_validation_cost}/10", "Kelly [13] (Downside Sizing)")
    score_table.add_row("[bold]Composite Score[/bold]", f"[bold]{scorecard.composite_score}/100[/bold]", f"[bold]{scorecard.recommendation}[/bold]")
    console.print(score_table)

    # 3. Value Equation Diagnosis
    console.print("\n[bold yellow]=== HORMOZI VALUE EQUATION DIAGNOSIS ===[/bold yellow]")
    console.print(f"• Formula: Value = (Dream x Likelihood) / (Time Delay x Effort/Sacrifice)")
    console.print(f"• Computed Score: [bold green]{value_diag.computed_score}[/bold green]")
    console.print(f"• Primary Bottleneck: [bold red]{value_diag.bottleneck_dimension}[/bold red]")
    console.print(f"• Recommended Fix: {value_diag.remediation_recommendation}")

    # 4. Founder Decision Memo
    memo_md = f"""
# FOUNDER DECISION MEMO ({memo.memo_id})
**Date:** {memo.date} | **Founder:** {memo.founder_name}
**Primary Opportunity:** {memo.primary_opportunity_title}
**Target Buyer Persona:** {memo.target_persona}

### 1. The Core Capability Leverage
{memo.core_capability_leverage}

### 2. Triangulated Buyer Pain Relieved
{memo.buyer_obstacle_relieved}

### 3. Ownership Mindset Reframing (Labor-to-Asset)
{memo.reframe_from_labor_to_asset}

### 4. 3-Tier Product Suite & Funnel Architecture
* **Lead Magnet:** {memo.product_suite_summary['lead_magnet']['title']} ($0)
* **Core Offer:** {memo.product_suite_summary['core_offer']['title']} (${memo.product_suite_summary['core_offer']['price_point_usd']:,.0f})
* **Recurring Backend:** {memo.product_suite_summary['backend_asset']['title']} (${memo.product_suite_summary['backend_asset']['price_point_usd']:,.0f}/mo)
* **Estimated 12-Month LTV:** ${memo.product_suite_summary['total_ltv']:,.0f}

### 5. First Validation Experiment (Regret-Minimization Framing)
{memo.first_validation_experiment}

> **Regret Minimization Reflection:** {memo.regret_minimization_framing}
> **Kelly-Sizing Guidance:** {memo.human_checkpoint.kelly_sizing_advice}
    """
    console.print(Panel(Markdown(memo_md), title="[bold green]FOUNDER DECISION MEMO[/bold green]", expand=False))


def main():
    try:
        run_interactive()
    except KeyboardInterrupt:
        console.print("\n[red]Execution cancelled by user.[/red]")
        sys.exit(0)


if __name__ == "__main__":
    main()
