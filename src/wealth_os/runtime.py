from __future__ import annotations

import json

from agents import Runner, SQLiteSession

from .agents import build_agents
from .calendar_google import calendar_digest
from .checkins import list_checkins, score_checkin
from .state import SESSIONS_DB, load_state


def checkin_context(limit: int = 14) -> str:
    rows = []
    for item in reversed(list_checkins(limit=limit)):
        metrics = score_checkin(item)
        rows.append({
            "date": item.date,
            "commitments": item.commitments,
            "completed_commitments": item.completed_commitments,
            "opportunity_creation": item.opportunity_creation,
            "deal_decision": item.deal_decision,
            "ownership_building": item.ownership_building,
            "capital_allocation": item.capital_allocation,
            "relationship_deposit": item.relationship_deposit,
            "kill_delegate_avoid": item.kill_delegate_avoid,
            "avoidance_or_fear": item.avoidance_or_fear,
            "overall_score": metrics.overall_score,
            "execution_rate": metrics.execution_rate,
        })
    return "RECENT CEO CHECK-IN HISTORY:\n" + json.dumps(rows, indent=2)


def operating_context(include_calendar: bool = True) -> str:
    state = load_state()
    parts = [
        "CURRENT USER-ENTERED OPERATING STATE:\n" + state.model_dump_json(indent=2),
        checkin_context(),
    ]
    if include_calendar:
        parts.append(calendar_digest(days_back=7, days_forward=2))
    return "\n\n".join(parts)


async def run_chief(
    prompt: str,
    session_id: str = "chief-of-staff",
    include_calendar: bool = True,
) -> str:
    SESSIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    session = SQLiteSession(session_id, str(SESSIONS_DB))
    chief = build_agents()["chief"]
    result = await Runner.run(
        chief,
        operating_context(include_calendar=include_calendar) + "\n\nUSER REQUEST:\n" + prompt,
        session=session,
    )
    return str(result.final_output)
