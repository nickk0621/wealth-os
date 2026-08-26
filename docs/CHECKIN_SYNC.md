# Check-in → Dashboard Sync

Wealth OS v0.4 separates the **operating record** from the user interface.

## Local mode

By default, CEO check-ins are stored in:

`data/wealth_os.db`

The Streamlit dashboard and the Chief of Staff both read from the same SQLite database, so completing a check-in immediately updates the CEO Scoreboard and future agent context.

Run:

```bash
wealth-os dashboard
```

or from the terminal:

```bash
wealth-os ceo-checkin
wealth-os morning
```

## API mode

Wealth OS also exposes a small FastAPI service so another authenticated process can write into the same check-in model.

Run locally:

```bash
wealth-os api
```

Health check:

```text
GET http://127.0.0.1:8765/health
```

Write a check-in:

```text
POST /api/checkins
Authorization: Bearer <WEALTH_OS_API_TOKEN>
Content-Type: application/json
```

Example body:

```json
{
  "date": "2026-08-26",
  "commitments": ["Call lender", "Source five owners", "Finish acquisition memo"],
  "opportunity_creation": "Source five owners and two brokers",
  "deal_decision": "Get leverage answer and kill the deal if financing fails",
  "ownership_building": "Finish acquisition memo",
  "capital_allocation": "Set liquidity reserve target",
  "relationship_deposit": "Call broker with useful market data",
  "health_energy": "Train and protect sleep",
  "kill_delegate_avoid": "Delegate admin follow-up",
  "avoidance_or_fear": "I am avoiding the lender call because I may get bad news"
}
```

Dashboard data:

```text
GET /api/dashboard
GET /api/checkins
GET /api/checkins/{YYYY-MM-DD}
```

## Security

Set a long random token before exposing the API beyond your own machine:

```bash
export WEALTH_OS_API_TOKEN="a-long-random-secret"
```

Do **not** expose the local API directly to the public internet without HTTPS, authentication, backups, and an appropriate hosting environment. `wealth-os api` defaults to `127.0.0.1`, which means only your own computer can reach it.

## ChatGPT/email reply loop

The data layer required for this workflow now exists. The remaining integration is a secure bridge that receives a reply from ChatGPT/email and sends the structured check-in to `POST /api/checkins`.

A local `localhost` API cannot receive writes from ChatGPT while it is running on OpenAI's servers. To make the loop fully automatic, host the API/data layer on an authenticated HTTPS endpoint or use an approved connected datastore. The local dashboard can then read that same remote record.

Until that remote bridge is configured, the guided dashboard check-in and `wealth-os ceo-checkin` command both write to exactly the same check-in schema the remote API uses, so no data migration or redesign is required later.
