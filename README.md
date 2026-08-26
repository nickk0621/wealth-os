# Wealth OS

An agent-driven personal CEO operating system for building wealth through disciplined execution, opportunity creation, ownership, capital allocation, relationship building, and fast qualification of weak opportunities.

## The core loop

Wealth OS is designed to run a repeatable operating cadence rather than just display information:

1. **Morning CEO Check-in** — lock exactly three commitments and answer the questions that drive opportunity creation, deal decisions, ownership-building, capital allocation, relationships, energy, and what to kill/delegate/avoid.
2. **Execute** — work from those commitments instead of a generic to-do list.
3. **Track** — mark commitments completed and record avoidance/scarcity patterns.
4. **Score** — the CEO Scoreboard tracks leading wealth-building behaviors over time.
5. **Review** — weekly/monthly/quarterly reviews use the actual history instead of relying on memory.
6. **Adapt** — the Chief of Staff sees recent check-ins and uses them when coaching the next day.

The behavioral score is a leading indicator, not a prediction of wealth. Execution is weighted most heavily, followed by opportunity creation, ownership-building, decision velocity, leverage/delegation, relationships, and energy.

## One-command local setup

Requires Python 3.10+ and Git.

### macOS / Linux

```bash
git clone https://github.com/nickk0621/wealth-os.git
cd wealth-os
bash scripts/setup.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/nickk0621/wealth-os.git
cd wealth-os
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

If the repo is already installed:

```bash
git pull
source .venv/bin/activate
pip install -e .
wealth-os dashboard
```

Run diagnostics with:

```bash
wealth-os doctor
```

## Daily use

The normal workflow is:

```bash
wealth-os dashboard
```

Then use **Today → Morning CEO Check-in**. Alternatively run the check-in from Terminal:

```bash
wealth-os ceo-checkin
wealth-os morning
```

The dashboard now centers on:

- Morning CEO Check-in
- exactly three locked commitments
- commitment completion
- CEO behavior score and trend
- avoidance/scarcity pattern log
- Chief-of-Staff coaching using actual check-in history
- weekly CEO reviews
- Calendar Intelligence
- commercial-real-estate underwriting and kill criteria
- deal qualification
- relationship deposits

## Wealth Constitution

`config/wealth_constitution.yaml` contains the durable rules the agents should apply: preserve optionality, never risk ruin, measure after-tax outcomes, seek bad news early, build ownership, protect liquidity and attention, protect reputation, reject sunk-cost thinking, and avoid lifestyle-driven scarcity.

## Check-in data

CEO check-ins are stored locally in:

`data/wealth_os.db`

That database is gitignored. The dashboard and Chief of Staff read the same record, so a saved check-in immediately changes the scoreboard and future agent context.

## Remote sync API

Wealth OS v0.4 includes a FastAPI data layer so an authenticated external process can eventually write the same CEO check-ins that the local dashboard reads.

Run locally:

```bash
wealth-os api
```

It defaults to:

`http://127.0.0.1:8765`

Endpoints include:

```text
GET  /health
GET  /api/dashboard
GET  /api/checkins
GET  /api/checkins/{YYYY-MM-DD}
POST /api/checkins
```

For authentication set:

```bash
export WEALTH_OS_API_TOKEN="a-long-random-secret"
```

See `docs/CHECKIN_SYNC.md` for the request format and architecture.

A local `127.0.0.1` API cannot receive writes directly from ChatGPT running on OpenAI's servers. To make the full **8 AM prompt → reply → automatic dashboard update** loop work, this API/data layer must later be placed behind an authenticated HTTPS endpoint (or another approved connected datastore). The application is already structured so that remote bridge does not require redesigning the check-in schema or coaching logic.

## Google Calendar — read only

Calendar access is deliberately read-only. Once configured, morning plans and reviews can compare your stated priorities with actual time allocation.

```bash
wealth-os calendar-auth
wealth-os calendar-status
wealth-os calendar-audit
```

OAuth client secrets and tokens remain local and gitignored.

## Commercial real-estate underwriting

The CRE module calculates deterministic metrics before an agent interprets them, including total basis, equity requirement, cap rate, yield on cost, debt service, DSCR, cash-on-cash, exit value, stress cases, and automatic kill flags.

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

## Reviews

```bash
wealth-os review weekly
wealth-os review monthly
wealth-os review quarterly
wealth-os review annual
```

The reviews now use tracked CEO check-ins, not just free-form conversation history.

## Data and safety model

Private operating state, CEO check-ins, session memory, histories, reports, OAuth tokens, API keys, and client secrets are gitignored.

Agents analyze and recommend, but Wealth OS does **not** move money, execute trades, sign documents, borrow funds, or send external messages automatically. Tax, legal, accounting, and investment conclusions are analysis for discussion with qualified professionals, not final professional advice.
