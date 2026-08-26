# Wealth OS

An agent-driven personal operating system for building wealth, protecting attention, evaluating opportunities, and running disciplined weekly/monthly reviews.

## V1 architecture

Wealth OS uses a manager-style multi-agent pattern with the OpenAI Agents SDK:

- **Chief of Staff** — orchestrates the system and turns analysis into a small number of concrete actions.
- **Deal Agent** — evaluates real-estate and business opportunities, searches for kill criteria, and prevents sunk-cost thinking.
- **CFO / Wealth Agent** — reasons in after-tax, after-fee, risk-adjusted terms and protects liquidity and solvency.
- **Time & Habits Agent** — audits attention, deep work, routines, delegation, and calendar quality.
- **Relationship Agent** — identifies relationships to deepen, maintain, or initiate.
- **CEO Review Agent** — runs weekly, monthly, quarterly, and annual operating reviews.

The specialist agents are exposed as tools to the Chief of Staff, which is the primary interface.

## Wealth Constitution

The file `config/wealth_constitution.yaml` contains the rules the agents should treat as durable constraints: preserve optionality, never risk ruin, measure after-tax outcomes, seek bad news early, build ownership, protect reputation, avoid lifestyle-driven scarcity, and favor compounding.

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
export OPENAI_API_KEY="your-key"
```

Run the interactive Chief of Staff:

```bash
wealth-os chat
```

Run a structured review:

```bash
wealth-os review weekly
wealth-os review monthly
wealth-os review quarterly
wealth-os review annual
```

Evaluate an opportunity:

```bash
wealth-os ask "Evaluate this acquisition: $2.4M purchase, $1.5M debt, current NOI $170k, upside from lease-up..."
```

## Data and safety model

V1 stores user-entered operating state locally in `data/state.json`. Do not commit personal financial data; `data/` is ignored except for its README. Agents advise and analyze, but V1 does **not** move money, execute trades, sign documents, borrow funds, or send messages automatically.

Tax, legal, accounting, and investment conclusions should be treated as analysis for discussion with qualified professionals, not final professional advice.

## Codex workflow

This repo is intentionally simple so Codex can evolve it safely. Good next tasks include:

1. Add a web dashboard for the personal scoreboard.
2. Add Google Calendar and Gmail integrations behind explicit approval gates.
3. Add a real-estate underwriting schema and deal database.
4. Add scheduled morning/weekly/monthly brief generation.
5. Add human-in-the-loop approval for any external write action.
6. Add tests and evals for the wealth constitution and opportunity-scoring behavior.

Built on the OpenAI Agents SDK manager / agents-as-tools pattern.