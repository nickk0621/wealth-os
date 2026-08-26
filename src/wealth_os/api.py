from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .checkins import DailyCEOCheckIn, dashboard_snapshot, get_checkin, list_checkins, save_checkin, score_checkin

app = FastAPI(title="Wealth OS API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("WEALTH_OS_API_TOKEN", "").strip()
    if not expected:
        return
    supplied = ""
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()
    if supplied != expected:
        raise HTTPException(status_code=401, detail="Invalid API token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard", dependencies=[Depends(require_token)])
def dashboard() -> dict[str, Any]:
    return dashboard_snapshot(limit=90)


@app.get("/api/checkins", dependencies=[Depends(require_token)])
def checkins(limit: int = 30) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 365))
    return [item.model_dump() | {"metrics": score_checkin(item).__dict__} for item in list_checkins(limit)]


@app.get("/api/checkins/{checkin_date}", dependencies=[Depends(require_token)])
def checkin(checkin_date: str) -> dict[str, Any]:
    item = get_checkin(checkin_date)
    if not item:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return item.model_dump() | {"metrics": score_checkin(item).__dict__}


@app.post("/api/checkins", dependencies=[Depends(require_token)])
def create_or_update_checkin(payload: DailyCEOCheckIn) -> dict[str, Any]:
    save_checkin(payload)
    return {"saved": True, "checkin": payload.model_dump(), "metrics": score_checkin(payload).__dict__}
