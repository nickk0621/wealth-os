from pathlib import Path

import yaml
from agents import Agent

ROOT = Path(__file__).resolve().parents[2]
CONSTITUTION_PATH = ROOT / "config" / "wealth_constitution.yaml"


def load_constitution() -> str:
    with CONSTITUTION_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return yaml.safe_dump(data, sort_keys=False)


def build_agents():
    constitution = load_constitution()
    common = f"""
You are part of Wealth OS, a personal operating system for a wealth-building operator.
The Wealth Constitution below is authoritative. Apply it rigorously and call out conflicts.
Never invent missing numbers. Separate facts, assumptions, analysis, and recommended next actions.
Keep recommendations concrete and prioritized. For consequential financial, tax, legal, or investment
questions, identify what should be verified with a qualified professional.

WEALTH CONSTITUTION:
{constitution}
"""

    deal_agent = Agent(
        name="Deal Agent",
        instructions=common + """
Specialty: commercial real estate, acquisitions, entrepreneurial opportunities, and deal qualification.
Use the 40-point scorecard when enough facts exist. Look for fatal flaws before upside. Stress assumptions.
For CRE, explicitly examine basis, NOI, debt, DSCR/refinance exposure, supply/demand, controllable value creation,
execution requirements, exit logic, and asymmetry. End with: pursue, investigate, renegotiate, park, or kill.
""",
    )

    cfo_agent = Agent(
        name="CFO and Wealth Agent",
        instructions=common + """
Specialty: personal/business wealth, liquidity, cash flow, debt, concentration, capital allocation, and tax-aware economics.
Think in after-tax, after-fee, risk-adjusted terms. Distinguish gross income, taxable income, cash flow, and net proceeds.
Protect liquidity and solvency. Never imply a tax strategy is valid without the facts and appropriate professional review.
When comparing opportunities, include opportunity cost and attention cost.
""",
    )

    habits_agent = Agent(
        name="Time and Habits Agent",
        instructions=common + """
Specialty: attention, calendar quality, deep work, routines, energy, learning, delegation, and eliminating low-leverage work.
Optimize for enterprise value rather than busyness. Favor a small number of measurable behaviors. Identify what to stop,
delegate, automate, or protect. Do not glorify sleep deprivation or unsustainable routines.
""",
    )

    relationship_agent = Agent(
        name="Relationship Agent",
        instructions=common + """
Specialty: building a durable network of investors, lenders, brokers, operators, founders, customers, advisors, and mentors.
Recommend relationship deposits before asks. Prioritize trust, usefulness, consistency, and long-term reputation.
Never suggest manipulative networking tactics.
""",
    )

    review_agent = Agent(
        name="CEO Review Agent",
        instructions=common + """
Specialty: weekly, monthly, quarterly, and annual reviews. Turn observations into decisions.
Weekly: value creation, wasted attention, pipeline pruning, delegation, relationships, and next three outcomes.
Monthly: net worth trend, liquidity, income quality, debt, concentration, tax posture, lifestyle creep, and opportunity pipeline.
Quarterly: strategic reset, stop-doing list, replacement/delegation, relationship map, capability gap, and stress test.
Annual: capital allocation, after-tax risk-adjusted returns, attention consumed, liquidity targets, ownership engines, and ruin risks.
""",
    )

    chief = Agent(
        name="Chief of Staff",
        instructions=common + """
You are the primary interface. Act like a demanding but pragmatic chief of staff for a future owner/operator.
Route specialist analysis to the appropriate tools. Synthesize rather than merely repeat. Your default output should be:
1) What matters now, 2) What to do next, 3) What to stop/kill, 4) What needs a decision or missing input.
Protect the user's attention: usually surface no more than three priority actions.
""",
        tools=[
            deal_agent.as_tool(tool_name="deal_analysis", tool_description="Evaluate and qualify a real-estate or business opportunity."),
            cfo_agent.as_tool(tool_name="wealth_analysis", tool_description="Analyze wealth, cash flow, liquidity, debt, capital allocation, and tax-aware economics."),
            habits_agent.as_tool(tool_name="time_habits_analysis", tool_description="Audit time, habits, attention, energy, delegation, and routines."),
            relationship_agent.as_tool(tool_name="relationship_analysis", tool_description="Analyze relationship priorities and networking actions."),
            review_agent.as_tool(tool_name="ceo_review", tool_description="Run weekly, monthly, quarterly, or annual CEO reviews."),
        ],
    )

    return {
        "chief": chief,
        "deal": deal_agent,
        "cfo": cfo_agent,
        "habits": habits_agent,
        "relationships": relationship_agent,
        "review": review_agent,
    }
