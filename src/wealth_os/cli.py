import asyncio
from typing import Literal

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from agents import Runner

from .agents import build_agents
from .state import load_state

load_dotenv()
app = typer.Typer(help="Wealth OS — agent-driven personal operating system")
console = Console()


def context_block() -> str:
    state = load_state()
    return "CURRENT USER-ENTERED OPERATING STATE:\n" + state.model_dump_json(indent=2)


async def run_chief(prompt: str) -> str:
    chief = build_agents()["chief"]
    result = await Runner.run(chief, context_block() + "\n\nUSER REQUEST:\n" + prompt)
    return result.final_output


@app.command()
def ask(prompt: str):
    """Ask the Chief of Staff a one-off question."""
    console.print(Markdown(asyncio.run(run_chief(prompt))))


@app.command()
def chat():
    """Interactive Chief of Staff session."""
    console.print("[bold]Wealth OS[/bold] — type 'exit' to stop.")
    while True:
        prompt = console.input("\n[bold cyan]> [/bold cyan]").strip()
        if prompt.lower() in {"exit", "quit"}:
            break
        if prompt:
            console.print(Markdown(asyncio.run(run_chief(prompt))))


@app.command()
def review(period: Literal["weekly", "monthly", "quarterly", "annual"] = "weekly"):
    """Run a structured CEO review."""
    prompt = f"Run my {period} CEO review. Use my current state, challenge weak assumptions, and finish with exactly three priority actions plus a stop-doing item."
    console.print(Markdown(asyncio.run(run_chief(prompt))))


if __name__ == "__main__":
    app()
