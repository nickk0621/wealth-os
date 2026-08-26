import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "data" / "state.json"


class OperatingState(BaseModel):
    goals: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    deals: list[dict[str, Any]] = Field(default_factory=list)
    wealth_snapshot: dict[str, Any] = Field(default_factory=dict)
    habits: dict[str, Any] = Field(default_factory=dict)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


def load_state() -> OperatingState:
    if not STATE_PATH.exists():
        return OperatingState()
    return OperatingState.model_validate_json(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: OperatingState) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(state.model_dump_json(indent=2), encoding="utf-8")
