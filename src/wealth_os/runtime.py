from __future__ import annotations

from agents import Runner, SQLiteSession

from .agents import build_agents
from .calendar_google import calendar_digest
from .state import SESSIONS_DB, load_state


def operating_context(include_calendar: bool = True) -> str:
    state = load_state()
    parts = ["CURRENT USER-ENTERED OPERATING STATE:\n" + state.model_dump_json(indent=2)]
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
