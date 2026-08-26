from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "wealth_os.db"


class DailyCEOCheckIn(BaseModel):
    date: str = Field(default_factory=lambda: date.today().isoformat())
    commitments: list[str] = Field(default_factory=list, max_length=3)
    opportunity_creation: str = ""
    deal_decision: str = ""
    ownership_building: str = ""
    capital_allocation: str = ""
    relationship_deposit: str = ""
    health_energy: str = ""
    kill_delegate_avoid: str = ""
    avoidance_or_fear: str = ""
    completed_commitments: list[str] = Field(default_factory=list)
    notes: str = ""


@dataclass
class CEOMetrics:
    execution_rate: float
    opportunity_score: float
    ownership_score: float
    decision_score: float
    leverage_score: float
    relationship_score: float
    energy_score: float
    overall_score: float


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ceo_checkins (
            checkin_date TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return conn


def save_checkin(checkin: DailyCEOCheckIn) -> None:
    now = datetime.now(timezone.utc).isoformat()
    payload = checkin.model_dump_json()
    with _conn() as conn:
        existing = conn.execute(
            "SELECT created_at FROM ceo_checkins WHERE checkin_date = ?",
            (checkin.date,),
        ).fetchone()
        created_at = existing["created_at"] if existing else now
        conn.execute(
            """
            INSERT INTO ceo_checkins(checkin_date, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(checkin_date) DO UPDATE SET
              payload = excluded.payload,
              updated_at = excluded.updated_at
            """,
            (checkin.date, payload, created_at, now),
        )


def get_checkin(checkin_date: str | None = None) -> DailyCEOCheckIn | None:
    checkin_date = checkin_date or date.today().isoformat()
    with _conn() as conn:
        row = conn.execute(
            "SELECT payload FROM ceo_checkins WHERE checkin_date = ?",
            (checkin_date,),
        ).fetchone()
    return DailyCEOCheckIn.model_validate_json(row["payload"]) if row else None


def list_checkins(limit: int = 90) -> list[DailyCEOCheckIn]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT payload FROM ceo_checkins ORDER BY checkin_date DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [DailyCEOCheckIn.model_validate_json(row["payload"]) for row in rows]


def _present(value: str | list[str]) -> float:
    if isinstance(value, list):
        return 1.0 if any(str(x).strip() for x in value) else 0.0
    return 1.0 if value.strip() else 0.0


def score_checkin(checkin: DailyCEOCheckIn) -> CEOMetrics:
    commitments = len([x for x in checkin.commitments if x.strip()])
    completed = len([x for x in checkin.completed_commitments if x.strip()])
    execution_rate = min(completed / commitments, 1.0) if commitments else 0.0

    opportunity = _present(checkin.opportunity_creation)
    ownership = _present(checkin.ownership_building)
    decision = _present(checkin.deal_decision) * 0.7 + _present(checkin.kill_delegate_avoid) * 0.3
    leverage = _present(checkin.capital_allocation) * 0.4 + _present(checkin.kill_delegate_avoid) * 0.6
    relationship = _present(checkin.relationship_deposit)
    energy = _present(checkin.health_energy)

    overall = (
        execution_rate * 30
        + opportunity * 15
        + ownership * 15
        + decision * 15
        + leverage * 10
        + relationship * 10
        + energy * 5
    )
    return CEOMetrics(
        execution_rate=round(execution_rate * 100, 1),
        opportunity_score=round(opportunity * 100, 1),
        ownership_score=round(ownership * 100, 1),
        decision_score=round(decision * 100, 1),
        leverage_score=round(leverage * 100, 1),
        relationship_score=round(relationship * 100, 1),
        energy_score=round(energy * 100, 1),
        overall_score=round(overall, 1),
    )


def dashboard_snapshot(limit: int = 30) -> dict[str, Any]:
    checkins = list_checkins(limit=limit)
    rows = []
    for item in reversed(checkins):
        metrics = score_checkin(item)
        rows.append({
            "date": item.date,
            "overall_score": metrics.overall_score,
            "execution_rate": metrics.execution_rate,
            "commitments": item.commitments,
            "completed_commitments": item.completed_commitments,
            "avoidance_or_fear": item.avoidance_or_fear,
        })
    return {
        "today": get_checkin(),
        "history": rows,
    }
