# Wealth OS

An agent-driven personal operating system for building wealth, protecting attention, evaluating opportunities, and running disciplined daily/weekly/monthly reviews.

## What it does now

Wealth OS uses a manager-style multi-agent pattern with the OpenAI Agents SDK:

- **Chief of Staff** — orchestrates the system and turns analysis into a small number of concrete actions.
- **Deal Agent** — evaluates real-estate and business opportunities, searches for kill criteria, and prevents sunk-cost thinking.
- **CFO / Wealth Agent** — reasons in after-tax, after-fee, risk-adjusted terms and protects liquidity and solvency.
- **Time & Habits Agent** — audits attention, deep work, routines, delegation, and calendar quality.
- **Relationship Agent** — identifies relationships to deepen, maintain, or initiate.
- **CEO Review Agent** — runs weekly, monthly, quarterly, and annual operating reviews.

The Chief of Staff has persistent conversational memory through an SDK `SQLiteSession`. Separate structured operating state lives locally in `data/state.json`, with local history snapshots and saved markdown reports.

## Wealth Constitution

`config/wealth_constitution.yaml` contains durable rules the agents should apply: preserve optionality, never risk ruin, measure after-tax outcomes, seek bad news early, build ownership, protect liquidity and attention, protect reputation, reject sunk-cost thinking, and avoid lifestyle-driven scarcity.

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
export OPENAI_API_KEY="your-key"
```

## Dashboard

Launch the local operating dashboard:

```bash
wealth-os dashboard
```

The dashboard includes:

- daily sleep / exercise / deep-work / energy check-ins
- personal wealth scoreboard
- current priorities
- deal pipeline and Deal Agent analysis
- relationship portfolio and relationship actions
- structured state editor
- Chief of Staff chat
- one-click morning brief generation

## Daily commands

```bash
wealth-os check-in --sleep-hours 7.5 --deep-work-hours 2 --energy 8 --exercise --top-outcome "Underwrite target acquisition"
wealth-os morning
wealth-os chat
```

## CEO reviews

```bash
wealth-os review weekly
wealth-os review monthly
wealth-os review quarterly
wealth-os review annual
```

Reviews and morning briefs are saved locally under `data/reports/`.

## Deal qualification

```bash
wealth-os ask "Evaluate this acquisition: $2.4M purchase, $1.5M debt, current NOI $170k, upside from lease-up..."
```

## Data and safety model

Private operating state, session memory, histories, and reports live under `data/` and are gitignored. Do not commit personal financial data or API keys.

Agents analyze and recommend, but V1 does **not** move money, execute trades, sign documents, borrow funds, or send external messages automatically. Tax, legal, accounting, and investment conclusions should be treated as analysis for discussion with qualified professionals, not final professional advice.

See `docs/OPERATING_RHYTHM.md` for the daily/weekly/monthly cadence and local scheduling example.

## Next build targets

1. Calendar integration so the Chief of Staff can compare stated priorities with actual time allocation.
2. Gmail integration with explicit human approval before sending anything.
3. A typed commercial-real-estate deal database and underwriting model.
4. Automated metrics and trend charts from state history.
5. Human-in-the-loop approval gates for any future external write actions.
6. Automated tests/evals for Wealth Constitution compliance and deal scoring.

Built on the OpenAI Agents SDK manager / agents-as-tools pattern.