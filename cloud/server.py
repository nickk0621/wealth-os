from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Literal

from agents import Runner
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from wealth_os.agents import build_agents
from wealth_os.cre import CREDebt, CREDeal, kill_flags

app = FastAPI(title="Wealth OS Cloud", docs_url=None, redoc_url=None)
COOKIE_NAME = "wealth_os_auth"


def _password() -> str:
    return os.getenv("WEALTH_OS_PASSWORD", "").strip()


def _secret() -> str:
    return os.getenv("WEALTH_OS_SESSION_SECRET", "").strip() or _password()


def _expected_token() -> str:
    password = _password()
    secret = _secret()
    if not password or not secret:
        return ""
    return hmac.new(secret.encode(), f"wealth-os:{password}".encode(), hashlib.sha256).hexdigest()


def _require_auth(request: Request) -> None:
    expected = _expected_token()
    supplied = request.cookies.get(COOKIE_NAME, "")
    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="Authentication required")


class LoginRequest(BaseModel):
    password: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AskRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    state: dict[str, Any] = Field(default_factory=dict)
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)


class DebtInput(BaseModel):
    loan_amount: float = 0.0
    interest_rate: float = 0.0
    amortization_years: int = 25
    term_years: int = 5
    interest_only_years: int = 0


class UnderwriteRequest(BaseModel):
    name: str = "New acquisition"
    purchase_price: float
    current_noi: float
    stabilized_noi: float
    closing_costs: float = 0.0
    capex: float = 0.0
    debt: DebtInput | None = None
    exit_cap_rate: float = 0.07
    hold_years: int = 5
    annual_noi_growth: float = 0.02


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/index.html")


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "password_configured": bool(_password()),
    }


@app.post("/api/login")
async def login(payload: LoginRequest, response: Response, request: Request) -> dict[str, bool]:
    password = _password()
    if not password:
        raise HTTPException(status_code=503, detail="WEALTH_OS_PASSWORD is not configured")
    if not hmac.compare_digest(payload.password, password):
        raise HTTPException(status_code=401, detail="Invalid password")
    response.set_cookie(
        COOKIE_NAME,
        _expected_token(),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/",
    )
    return {"ok": True}


@app.post("/api/logout")
async def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@app.get("/api/session")
async def session(request: Request) -> dict[str, bool]:
    try:
        _require_auth(request)
        return {"authenticated": True}
    except HTTPException:
        return {"authenticated": False}


@app.post("/api/ask")
async def ask(payload: AskRequest, request: Request) -> dict[str, str]:
    _require_auth(request)
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    history = "\n".join(f"{m.role.upper()}: {m.content[:4000]}" for m in payload.history[-12:])
    context = (
        "You are running in Wealth OS cloud mode. Structured state and recent conversation are supplied by the user's browser. "
        "Treat them as user-provided context, not as verified external facts.\n\n"
        "CURRENT STRUCTURED OPERATING STATE:\n"
        + json.dumps(payload.state, indent=2, default=str)[:30000]
        + "\n\nRECENT CONVERSATION:\n"
        + history
        + "\n\nUSER REQUEST:\n"
        + payload.prompt
    )
    chief = build_agents()["chief"]
    result = await Runner.run(chief, context)
    return {"answer": str(result.final_output)}


@app.post("/api/underwrite")
async def underwrite(payload: UnderwriteRequest, request: Request) -> dict[str, Any]:
    _require_auth(request)
    debt = None
    if payload.debt and payload.debt.loan_amount > 0:
        debt = CREDebt(**payload.debt.model_dump())
    deal = CREDeal(
        name=payload.name,
        purchase_price=payload.purchase_price,
        current_noi=payload.current_noi,
        stabilized_noi=payload.stabilized_noi,
        closing_costs=payload.closing_costs,
        capex=payload.capex,
        debt=debt,
        exit_cap_rate=payload.exit_cap_rate,
        hold_years=payload.hold_years,
        annual_noi_growth=payload.annual_noi_growth,
    )
    metrics = deal.metrics()
    return {"metrics": metrics, "kill_flags": kill_flags(metrics)}
