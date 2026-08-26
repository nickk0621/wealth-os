# Wealth OS

An agent-driven personal operating system for building wealth, protecting attention, evaluating commercial real estate, and running disciplined daily/weekly/monthly reviews.

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

On Windows PowerShell, activation is typically:

```powershell
.venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY="your-key"
```

## Dashboard

Launch the local operating dashboard:

```bash
wealth-os dashboard
```

The dashboard includes daily check-ins, the personal wealth scoreboard, Chief-of-Staff chat, calendar intelligence, structured CRE underwriting/stress testing, deal analysis, relationship review, and a structured state editor.

## Google Calendar — read only

Calendar access is deliberately read-only.

1. Enable Google Calendar API in a Google Cloud project.
2. Configure Google Auth and create an OAuth 2.0 **Desktop app** client.
3. Download the credentials JSON to:

   `secrets/google_calendar_client_secret.json`

4. Run:

```bash
wealth-os calendar-auth
wealth-os calendar-status
wealth-os calendar-audit
```

The browser authorization flow stores the resulting local token at `secrets/google_calendar_token.json`. Both credential files are gitignored.

Once connected, morning briefs and CEO reviews can compare your stated priorities with your actual calendar allocation.

## Commercial real-estate underwriting

The CRE module calculates deterministic metrics before the Deal Agent interprets them, including:

- total basis and equity required
- going-in cap rate
- stabilized yield on cost
- annual debt service
- current and stabilized DSCR
- cash flow after debt and cash-on-cash return
- projected exit NOI/value
- stress-case NOI decline, interest-rate shock, and exit-cap expansion
- automatic coverage/spread kill flags

CLI example:

```bash
wealth-os cre-underwrite \
  --name "Main Street" \
  --purchase-price 2500000 \
  --current-noi 175000 \
  --stabilized-noi 225000 \
  --loan-amount 1500000 \
  --interest-rate 0.065 \
  --capex 200000 \
  --exit-cap-rate 0.07
```

Or use the **CRE Underwriting** page in the dashboard.

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

## Local but internet-connected

The application runs on your computer, but the Python process can make outbound HTTPS calls to OpenAI and Google. The dashboard itself normally stays on `localhost`, so it does not need to be publicly exposed.

See `docs/LOCAL_INTERNET.md` for a diagram and a fuller explanation.

## Data and safety model

Private operating state, session memory, histories, reports, OAuth tokens, and client secrets are gitignored.

Agents analyze and recommend, but Wealth OS does **not** move money, execute trades, sign documents, borrow funds, or send external messages automatically. Tax, legal, accounting, and investment conclusions should be treated as analysis for discussion with qualified professionals, not final professional advice.

See `docs/OPERATING_RHYTHM.md` for the daily/weekly/monthly cadence and local scheduling example.

## Next build targets

1. Gmail integration with explicit human approval before any external send.
2. Persistent typed CRE deal database with scenario/version history.
3. Automated metrics and trend charts from state history.
4. Richer calendar categorization and time-budget targets.
5. Human-in-the-loop approval gates for any future external write action.
6. Evals for Wealth Constitution compliance and deal qualification.

Built on the OpenAI Agents SDK manager / agents-as-tools pattern.