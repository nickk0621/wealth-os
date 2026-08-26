from __future__ import annotations

import asyncio
import json
from datetime import date

import streamlit as st

from .calendar_google import calendar_digest, calendar_is_connected, list_events
from .cre import CREDebt, CREDeal, kill_flags
from .runtime import run_chief
from .state import DailyCheckIn, OperatingState, load_state, save_state, upsert_daily_checkin, write_report

st.set_page_config(page_title="Wealth OS", page_icon="📈", layout="wide")
st.title("Wealth OS")
st.caption("Chief of Staff + wealth, deals, calendar, habits, relationships, and CEO reviews")

state = load_state()

with st.sidebar:
    st.header("Operating rhythm")
    page = st.radio("View", ["Today", "Scoreboard", "Calendar", "CRE Underwriting", "Deals", "Relationships", "State Editor"])
    st.caption(f"Google Calendar: {'connected' if calendar_is_connected() else 'not connected'}")
    if st.button("Run morning brief", use_container_width=True):
        with st.spinner("Chief of Staff is reviewing your operating state and calendar..."):
            brief = asyncio.run(run_chief(
                "Give me my morning brief. Compare my stated priorities with my recent and upcoming calendar. "
                "Identify what matters most today, exactly three actions, one thing to kill or avoid, and any financial/deal/habit risk I should not ignore.",
                session_id="morning-brief",
            ))
        path = write_report("morning-brief", brief)
        st.session_state["latest_brief"] = brief
        st.success(f"Saved locally to {path.name}")

if page == "Today":
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Daily check-in")
        with st.form("daily-checkin"):
            sleep = st.number_input("Sleep hours", min_value=0.0, max_value=14.0, value=7.5, step=0.25)
            exercise = st.checkbox("Exercise / training completed")
            deep = st.number_input("Deep work hours", min_value=0.0, max_value=12.0, value=2.0, step=0.25)
            energy = st.slider("Energy", 1, 10, 7)
            top_outcome = st.text_input("Most important outcome today")
            win = st.text_input("Biggest recent win")
            friction = st.text_input("Biggest friction / constraint")
            if st.form_submit_button("Save check-in", use_container_width=True):
                upsert_daily_checkin(DailyCheckIn(
                    date=date.today().isoformat(), sleep_hours=sleep, exercise=exercise,
                    deep_work_hours=deep, energy=energy, top_outcome=top_outcome,
                    win=win, friction=friction,
                ))
                st.success("Check-in saved")
    with right:
        st.subheader("Chief of Staff")
        prompt = st.text_area("Ask about priorities, a deal, capital allocation, habits, or a decision", height=140)
        if st.button("Ask Chief of Staff", use_container_width=True) and prompt.strip():
            with st.spinner("Thinking across the specialist agents..."):
                answer = asyncio.run(run_chief(prompt, session_id="dashboard-chief"))
            st.markdown(answer)
        if "latest_brief" in st.session_state:
            st.divider()
            st.subheader("Latest morning brief")
            st.markdown(st.session_state["latest_brief"])

elif page == "Scoreboard":
    st.subheader("Personal scoreboard")
    ws = state.wealth_snapshot
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Net worth", ws.get("net_worth", "Not set"))
    c2.metric("Investable liquidity", ws.get("investable_liquidity", "Not set"))
    c3.metric("Recurring / ownership income", ws.get("recurring_income", "Not set"))
    c4.metric("Debt", ws.get("debt", "Not set"))

    st.subheader("Current priorities")
    if state.priorities:
        for i, item in enumerate(state.priorities, 1):
            st.write(f"{i}. {item}")
    else:
        st.info("No priorities set yet. Add them in State Editor.")

    if state.daily_checkins:
        rows = [c.model_dump() for c in state.daily_checkins[-30:]]
        st.subheader("Recent daily check-ins")
        st.dataframe(rows, use_container_width=True, hide_index=True)

elif page == "Calendar":
    st.subheader("Calendar intelligence")
    if not calendar_is_connected():
        st.warning("Google Calendar is not connected. From your terminal, run `wealth-os calendar-auth` after placing your Google OAuth desktop-client JSON in `secrets/google_calendar_client_secret.json`.")
    else:
        days_back = st.slider("Days back", 1, 30, 7)
        days_forward = st.slider("Days forward", 1, 14, 2)
        try:
            events = list_events(days_back=days_back, days_forward=days_forward)
            st.dataframe([e.to_dict() for e in events], use_container_width=True, hide_index=True)
            if st.button("Audit time allocation", use_container_width=True):
                digest = calendar_digest(days_back=days_back, days_forward=days_forward)
                result = asyncio.run(run_chief(
                    digest + "\n\nAudit this calendar against my stated priorities. Categorize time into high-leverage creation/ownership work, deal sourcing/sales, relationships, operations/admin, and low-value/reactive work. Give me exactly three changes for next week.",
                    session_id="calendar-audit-dashboard",
                    include_calendar=False,
                ))
                st.markdown(result)
        except Exception as exc:
            st.error(f"Calendar error: {exc}")

elif page == "CRE Underwriting":
    st.subheader("Commercial real estate underwriting")
    with st.form("cre-form"):
        name = st.text_input("Deal name", value="New acquisition")
        a, b, c = st.columns(3)
        purchase_price = a.number_input("Purchase price", min_value=0.0, value=2500000.0, step=50000.0)
        current_noi = b.number_input("Current NOI", value=175000.0, step=5000.0)
        stabilized_noi = c.number_input("Stabilized NOI", value=225000.0, step=5000.0)
        a, b, c = st.columns(3)
        closing_costs = a.number_input("Closing costs", min_value=0.0, value=50000.0, step=5000.0)
        capex = b.number_input("CapEx / value-add budget", min_value=0.0, value=200000.0, step=10000.0)
        exit_cap = c.number_input("Exit cap rate", min_value=0.001, max_value=0.25, value=0.07, step=0.0025, format="%.4f")
        a, b, c = st.columns(3)
        loan = a.number_input("Loan amount", min_value=0.0, value=1500000.0, step=50000.0)
        rate = b.number_input("Interest rate", min_value=0.0, max_value=0.30, value=0.065, step=0.0025, format="%.4f")
        amort = c.number_input("Amortization years", min_value=1, max_value=50, value=25)
        a, b = st.columns(2)
        hold = a.number_input("Hold years", min_value=1, max_value=30, value=5)
        growth = b.number_input("Annual NOI growth", min_value=-0.25, max_value=0.25, value=0.02, step=0.005, format="%.3f")
        submitted = st.form_submit_button("Underwrite deal", type="primary", use_container_width=True)

    if submitted:
        debt = CREDebt(loan_amount=loan, interest_rate=rate, amortization_years=int(amort)) if loan > 0 else None
        deal = CREDeal(
            name=name, purchase_price=purchase_price, current_noi=current_noi, stabilized_noi=stabilized_noi,
            closing_costs=closing_costs, capex=capex, debt=debt, exit_cap_rate=exit_cap,
            hold_years=int(hold), annual_noi_growth=growth,
        )
        metrics = deal.metrics()
        flags = kill_flags(metrics)
        st.session_state["cre_metrics"] = metrics
        st.session_state["cre_flags"] = flags

    if "cre_metrics" in st.session_state:
        metrics = st.session_state["cre_metrics"]
        flags = st.session_state["cre_flags"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Going-in cap", f"{metrics['going_in_cap_rate']:.2%}")
        c2.metric("Yield on cost", f"{metrics['stabilized_yield_on_cost']:.2%}")
        c3.metric("Current DSCR", "N/A" if metrics['current_dscr'] is None else f"{metrics['current_dscr']:.2f}x")
        c4.metric("Current cash-on-cash", "N/A" if metrics['current_cash_on_cash'] is None else f"{metrics['current_cash_on_cash']:.2%}")
        st.write("**Stress test**", metrics["stress"])
        if flags:
            for flag in flags:
                st.error(flag)
        else:
            st.success("No automatic kill flags were triggered. This does not replace diligence.")
        if st.button("Ask Deal Agent to interpret", use_container_width=True):
            result = asyncio.run(run_chief(
                "Use the Deal Agent to interpret this CRE underwriting. Identify missing diligence, challenge assumptions, and conclude pursue, investigate, renegotiate, park, or kill.\n\n" + json.dumps({"metrics": metrics, "kill_flags": flags}, default=str, indent=2),
                session_id="cre-dashboard",
                include_calendar=False,
            ))
            st.markdown(result)

elif page == "Deals":
    st.subheader("Deal pipeline")
    if state.deals:
        st.dataframe(state.deals, use_container_width=True, hide_index=True)
    else:
        st.info("No deals in the pipeline yet.")
    deal_text = st.text_area("Describe a deal to qualify", height=180)
    if st.button("Run Deal Agent", use_container_width=True) and deal_text.strip():
        result = asyncio.run(run_chief(
            "Use the Deal Agent to evaluate this opportunity. Apply the scorecard and kill questions, identify missing inputs, and conclude pursue, investigate, renegotiate, park, or kill.\n\n" + deal_text,
            session_id="deal-desk",
        ))
        st.markdown(result)

elif page == "Relationships":
    st.subheader("Relationship portfolio")
    if state.relationships:
        st.dataframe(state.relationships, use_container_width=True, hide_index=True)
    else:
        st.info("No relationships entered yet.")
    if st.button("Recommend relationship actions", use_container_width=True):
        result = asyncio.run(run_chief(
            "Review my relationship portfolio. Recommend the three highest-value relationship deposits or follow-ups for this week. Prioritize long-term trust and usefulness over asks.",
            session_id="relationships",
        ))
        st.markdown(result)

elif page == "State Editor":
    st.subheader("Structured operating state")
    st.caption("This file stays local and is gitignored. Use JSON so the agents can reason over explicit, measurable facts.")
    raw = st.text_area("State JSON", value=state.model_dump_json(indent=2), height=600)
    if st.button("Validate and save state", type="primary", use_container_width=True):
        try:
            updated = OperatingState.model_validate(json.loads(raw))
            save_state(updated, reason="dashboard_state_editor")
            st.success("State validated and saved")
        except Exception as exc:
            st.error(f"Invalid state: {exc}")
