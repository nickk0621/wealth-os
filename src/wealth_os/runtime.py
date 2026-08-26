from __future__ import annotations

from agents import Runner, SQLiteSession

from .agents import build_agents
from .state import SESSIONS_DB, load_state


def operating_context() -> str:
    state = load_state()
    return "CURRENT USER-ENTERED OPERATING STATE:\n" + state.model_dump_json(indent=2)


async def run_chief(prompt: str, session_id: str = "chief-of-staff") -> str:
    SESSIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    session = SQLiteSession(session_id, str(SESSIONS_DB))
    chief = build_agents()["chief"]
    result = await Runner.run(
        chief,
        operating_context() + "\n\nUSER REQUEST:\n" + prompt,
        session=session,
    )
    return str(result.final_output)
