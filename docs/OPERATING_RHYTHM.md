# Wealth OS operating rhythm

The system is designed around a small number of recurring loops rather than constant AI chatter.

## Every morning

Run:

```bash
wealth-os check-in --sleep-hours 7.5 --deep-work-hours 2 --energy 8 --exercise --top-outcome "Underwrite target acquisition"
wealth-os morning
```

The morning brief should answer:

1. What matters most today?
2. What are the three highest-leverage actions?
3. What should be killed, avoided, delegated, or ignored?
4. What risk or missing decision is most important?

## During the day

Use the Chief of Staff for consequential decisions rather than every tiny task:

```bash
wealth-os ask "I have four hours free this afternoon. Given my priorities, what is the highest-leverage use of them?"
wealth-os ask "Use the Deal Agent to qualify this opportunity: ..."
```

## Weekly

```bash
wealth-os review weekly
```

Focus: value creation, wasted attention, pipeline pruning, delegation, relationships, and next week's three outcomes.

## Monthly

```bash
wealth-os review monthly
```

Before running it, update the state with current net worth, investable liquidity, debt, recurring income, major obligations, active opportunities, and concentration risks.

## Quarterly

```bash
wealth-os review quarterly
```

Use this review to remove commitments, replace yourself on recurring tasks, audit relationships, identify the next capability to build, and stress-test the plan.

## Annual

```bash
wealth-os review annual
```

This is the capital-allocation review: where money and attention went, what produced the strongest after-tax risk-adjusted results, what should receive more or less capital, and which risks could permanently impair the plan.

## Dashboard

```bash
wealth-os dashboard
```

The local dashboard is the easiest place to maintain the system. Structured financial and relationship data stays in `data/state.json`, which is gitignored.

## Scheduling the morning brief

The safest V1 is to schedule the **local command** on a machine you control so private state never needs to live in GitHub.

macOS/Linux cron example for 7:00 AM every weekday:

```cron
0 7 * * 1-5 cd /path/to/wealth-os && /path/to/.venv/bin/wealth-os morning >> data/morning.log 2>&1
```

Because the brief calls the OpenAI API, the scheduled environment must have `OPENAI_API_KEY` available. Keep API keys and private operating state out of the repository.

## Human-approval boundary

V1 may analyze and recommend. It should not autonomously move money, trade, borrow, sign, send external messages, or commit to transactions. Future integrations should keep approval gates for external write actions.
