import asyncio
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Literal

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from .calendar_google import authorize_calendar, calendar_digest, calendar_is_connected
from .cre import CREDebt, CREDeal, kill_flags
from .runtime import run_chief
from .state import DailyCheckIn, load_state, upsert_daily_checkin, write_report

load_dotenv()
app = typer.Typer(help="Wealth OS — agent-driven personal operating system")
console = Console()
ROOT = Path(__file__).resolve().parents[2]


def render(prompt: str, session_id: str, include_calendar: bool = True) -> str:
    return asyncio.run(run_chief(prompt, session_id=session_id, include_calendar=include_calendar))


def _internet_reachable(host: str = "api.openai.com", port: int = 443, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@app.command()
def doctor():
    """Check whether the local Wealth OS installation is ready to run."""
    checks = []
    py_ok = sys.version_info >= (3, 10)
    checks.append(("Python 3.10+", py_ok, sys.version.split()[0]))

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    checks.append(("OPENAI_API_KEY", bool(api_key), "configured" if api_key else "missing"))

    internet = _internet_reachable()
    checks.append(("Outbound internet", internet, "api.openai.com:443 reachable" if internet else "not reachable"))

    calendar_secret = ROOT / "secrets" / "google_calendar_client_secret.json"
    checks.append(("Google Calendar OAuth client", calendar_secret.exists(), str(calendar_secret) if calendar_secret.exists() else "optional / missing"))
    checks.append(("Google Calendar authorization", calendar_is_connected(), "connected" if calendar_is_connected() else "optional / not connected"))

    try:
        state = load_state()
        state_ok = state is not None
        state_detail = "state loads"
    except Exception as exc:
        state_ok = False
        state_detail = str(exc)
    checks.append(("Local operating state", state_ok, state_detail))

    table = Table(title="Wealth OS doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")
    for name, ok, detail in checks:
        table.add_row(name, "[green]OK[/green]" if ok else "[yellow]ACTION[/yellow]", detail)
    console.print(table)

    required_ok = py_ok and bool(api_key) and internet and state_ok
    if required_ok:
        console.print("[green]Core Wealth OS is ready.[/green]")
    else:
        console.print("[yellow]Fix the ACTION items above before using the AI features.[/yellow]")
        raise typer.Exit(code=1)


@app.command()
def ask(prompt: str):
    """Ask the Chief of Staff a one-off question."""
    console.print(Markdown(render(prompt, "cli-chief")))


@app.command()
def chat():
    """Interactive Chief of Staff session with persistent memory."""
    console.print("[bold]Wealth OS[/bold] — type 'exit' to stop.")
    while True:
        prompt = console.input("\n[bold cyan]> [/bold cyan]").strip()
        if prompt.lower() in {"exit", "quit"}:
            break
        if prompt:
            console.print(Markdown(render(prompt, "cli-chat")))


@app.command()
def morning():
    """Generate and save the daily morning brief, including calendar context when connected."""
    prompt = (
        "Give me my morning brief. Compare my stated priorities with my recent and upcoming calendar. "
        "Identify what matters most today, exactly three priority actions, one thing to kill/avoid, "
        "and the most important risk or missing decision across wealth, deals, time, habits, and relationships. "
        "If my calendar allocation conflicts with my goals, say so explicitly. Be concise and concrete."
    )
    output = render(prompt, "morning-brief")
    path = write_report("morning-brief", output)
    console.print(Markdown(output))
    console.print(f"\n[dim]Saved: {path}[/dim]")


@app.command()
def review(period: Literal["weekly", "monthly", "quarterly", "annual"] = "weekly"):
    """Run and save a structured CEO review."""
    prompt = (
        f"Run my {period} CEO review. Use my current operating state and calendar allocation, challenge weak assumptions, "
        "and finish with exactly three priority actions plus one stop-doing item."
    )
    output = render(prompt, f"review-{period}")
    path = write_report(f"{period}-review", output)
    console.print(Markdown(output))
    console.print(f"\n[dim]Saved: {path}[/dim]")


@app.command("calendar-auth")
def calendar_auth():
    """Authorize read-only access to Google Calendar using a local OAuth browser flow."""
    authorize_calendar()
    console.print("[green]Google Calendar connected with read-only access.[/green]")


@app.command("calendar-status")
def calendar_status():
    """Show Google Calendar connection status."""
    status = "connected" if calendar_is_connected() else "not connected"
    console.print(f"Google Calendar: [bold]{status}[/bold]")


@app.command("calendar-audit")
def calendar_audit(days_back: int = 7, days_forward: int = 2):
    """Audit calendar allocation against stated priorities."""
    if not calendar_is_connected():
        console.print("[yellow]Calendar is not connected. Run `wealth-os calendar-auth` first.[/yellow]")
        raise typer.Exit(code=1)
    prompt = (
        f"Audit my calendar using the supplied calendar context ({days_back} days back and {days_forward} days forward). "
        "Categorize the time into high-leverage creation/ownership work, sales/deal sourcing, relationships, operations/admin, "
        "and low-value/reactive work. Compare the pattern with my goals. Give me three calendar changes for next week."
    )
    custom = calendar_digest(days_back=days_back, days_forward=days_forward)
    output = render(custom + "\n\n" + prompt, "calendar-audit", include_calendar=False)
    console.print(Markdown(output))


@app.command("cre-underwrite")
def cre_underwrite(
    name: str = typer.Option(...),
    purchase_price: float = typer.Option(..., min=0),
    current_noi: float = typer.Option(...),
    stabilized_noi: float = typer.Option(...),
    loan_amount: float = typer.Option(0.0, min=0),
    interest_rate: float = typer.Option(0.0, help="Decimal rate, e.g. 0.065 for 6.5%"),
    amortization_years: int = typer.Option(25, min=1),
    closing_costs: float = typer.Option(0.0, min=0),
    capex: float = typer.Option(0.0, min=0),
    exit_cap_rate: float = typer.Option(0.07, min=0.001),
    hold_years: int = typer.Option(5, min=1),
    annual_noi_growth: float = typer.Option(0.02),
):
    """Run deterministic CRE underwriting metrics and stress tests, then ask the Deal Agent to interpret them."""
    debt = None
    if loan_amount > 0:
        debt = CREDebt(
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            amortization_years=amortization_years,
        )
    deal = CREDeal(
        name=name,
        purchase_price=purchase_price,
        current_noi=current_noi,
        stabilized_noi=stabilized_noi,
        closing_costs=closing_costs,
        capex=capex,
        debt=debt,
        exit_cap_rate=exit_cap_rate,
        hold_years=hold_years,
        annual_noi_growth=annual_noi_growth,
    )
    metrics = deal.metrics()
    flags = kill_flags(metrics)
    console.print_json(json.dumps({"metrics": metrics, "kill_flags": flags}, default=str))
    prompt = (
        "Use the Deal Agent to interpret this deterministic CRE underwriting output. Do not recalculate unless necessary. "
        "Identify missing diligence, challenge assumptions, and conclude pursue, investigate, renegotiate, park, or kill.\n\n"
        + json.dumps({"metrics": metrics, "kill_flags": flags}, default=str, indent=2)
    )
    console.print(Markdown(render(prompt, "cre-underwriting", include_calendar=False)))


@app.command("check-in")
def check_in(
    sleep_hours: float = typer.Option(..., min=0, max=14),
    deep_work_hours: float = typer.Option(..., min=0, max=12),
    energy: int = typer.Option(..., min=1, max=10),
    exercise: bool = typer.Option(False),
    top_outcome: str = typer.Option(""),
    win: str = typer.Option(""),
    friction: str = typer.Option(""),
):
    """Record today's operating check-in."""
    upsert_daily_checkin(DailyCheckIn(
        sleep_hours=sleep_hours,
        deep_work_hours=deep_work_hours,
        energy=energy,
        exercise=exercise,
        top_outcome=top_outcome,
        win=win,
        friction=friction,
    ))
    console.print("[green]Daily check-in saved.[/green]")


@app.command()
def state():
    """Print the current structured operating state."""
    console.print_json(load_state().model_dump_json())


@app.command()
def dashboard():
    """Launch the local Streamlit dashboard."""
    dashboard_file = Path(__file__).with_name("dashboard.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_file)], check=False)


if __name__ == "__main__":
    app()
