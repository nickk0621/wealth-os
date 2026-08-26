import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Literal

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .runtime import run_chief
from .state import DailyCheckIn, load_state, upsert_daily_checkin, write_report

load_dotenv()
app = typer.Typer(help="Wealth OS — agent-driven personal operating system")
console = Console()


def render(prompt: str, session_id: str) -> str:
    return asyncio.run(run_chief(prompt, session_id=session_id))


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
    """Generate and save the daily morning brief."""
    prompt = (
        "Give me my morning brief. Identify what matters most today, exactly three priority actions, "
        "one thing to kill/avoid, and the most important risk or missing decision across wealth, deals, "
        "time, habits, and relationships. Be concise and concrete."
    )
    output = render(prompt, "morning-brief")
    path = write_report("morning-brief", output)
    console.print(Markdown(output))
    console.print(f"\n[dim]Saved: {path}[/dim]")


@app.command()
def review(period: Literal["weekly", "monthly", "quarterly", "annual"] = "weekly"):
    """Run and save a structured CEO review."""
    prompt = (
        f"Run my {period} CEO review. Use my current operating state, challenge weak assumptions, "
        "and finish with exactly three priority actions plus one stop-doing item."
    )
    output = render(prompt, f"review-{period}")
    path = write_report(f"{period}-review", output)
    console.print(Markdown(output))
    console.print(f"\n[dim]Saved: {path}[/dim]")


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
