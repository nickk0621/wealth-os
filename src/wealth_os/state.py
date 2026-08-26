from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STATE_PATH = DATA_DIR / "state.json"
HISTORY_PATH = DATA_DIR / "history.jsonl"
REPORTS_DIR = DATA_DIR / "reports"
SESSIONS_DB = DATA_DIR / "sessions.db"


class DailyCheckIn(BaseModel):
    date: str = Field(default_factory=lambda: date.today().isoformat())
    sleep_hours: float | None = None
    exercise: bool | None = None
    deep_work_hours: float | None = None
    energy: int | None = Field(default=None, ge=1, le=10)
    top_outcome: str = ""
    win: str = ""
    friction: str = ""


class OperatingState(BaseModel):
    goals: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    deals: list[dict[str, Any]] = Field(default_factory=list)
    wealth_snapshot: dict[str, Any] = Field(default_factory=dict)
    habits: dict[str, Any] = Field(default_factory=dict)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    daily_checkins: list[DailyCheckIn] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    updated_at: str | None = None


def load_state() -> OperatingState:
    if not STATE_PATH.exists():
        return OperatingState()
    return OperatingState.model_validate_json(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: OperatingState, reason: str = "manual_update") -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state.updated_at = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    append_history(reason, state)


def append_history(reason: str, state: OperatingState) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "state": state.model_dump(mode="json"),
    }
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def upsert_daily_checkin(checkin: DailyCheckIn) -> OperatingState:
    state = load_state()
    state.daily_checkins = [c for c in state.daily_checkins if c.date != checkin.date]
    state.daily_checkins.append(checkin)
    state.daily_checkins.sort(key=lambda c: c.date)
    state.daily_checkins = state.daily_checkins[-120:]
    save_state(state, reason="daily_checkin")
    return state


def write_report(name: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c for c in name if c.isalnum() or c in {"-", "_"}).strip("_-") or "report"
    path = REPORTS_DIR / f"{date.today().isoformat()}-{safe_name}.md"
    path.write_text(content, encoding="utf-8")
    return path
