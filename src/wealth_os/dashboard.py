from __future__ import annotations

import asyncio
import json

import streamlit as st

from .calendar_google import calendar_digest, calendar_is_connected, list_events
from .checkin_ui import render_ceo_scoreboard, render_guided_checkin
from .checkins import get_checkin, score_checkin
from .cre import CREDebt, CREDeal, kill_flags
from .runtime import run_chief
from .state import OperatingState, load_state, save_state, write_report

st.set_page_config(page_title="Wealth OS", page_icon="📈", layout="wide")
st.title("Wealth OS")
st.caption("A personal CEO operating system: decide, execute, track, review, improve.")

state = load_state()

with st.sidebar:
    st.header("CEO operating rhythm")
    page = st.radio(
        "View",
        ["Today", "CEO Scoreboard", "Weekly Review", "Calendar", "CRE Underwriting", "Deals", "Relationships", "State Editor"],
    )
    st.caption(f"Google Calendar: {'connected' if calendar_is_connected() else 'not connected'}")

if page == "Today":
    today = get_checkin()
    if today:
        metrics = score_checkin(today)
        c1, c2, c3 = st.columns(3)
        c1.metric("CEO behavior score", f"{metrics.overall_score:.0f}/100")
        c2.metric("Execution", f"{metrics.execution_rate:.0f}%")
        c3.metric("Locked commitments", len(today.commitments))

    tab1, tab2 = st.tabs(["Morning CEO Check-in", "Chief of Staff"])
    with tab1:
        render_guided_checkin()
    with tab2:
        st.subheader("Chief of Staff")
        st.caption("Use this after your check-in. The agent sees your recent CEO check-ins and structured operating state.")
        prompt = st.text_area(
            "What decision, obstacle, or opportunity do you want help with?",
            height=150,
            placeholder="Example: I keep avoiding the lender call because I may get bad news on leverage. What should I do?",
        )
        if st.button("Ask Chief of Staff", type="primary", use_container_width=True) and prompt.strip():
            with st.spinner("Reviewing your operating history and decision rules..."):
                answer = asyncio.run(run_chief(prompt, session_id="dashboard-chief"))
            st.markdown(answer)

        if st.button("Generate today's operating plan", use_container_width=True):
            with st.spinner("Building today's plan..."):
                brief = asyncio.run(run_chief(
                    "Using today's CEO check-in, my recent patterns, my calendar, and Wealth Constitution, give me exactly three priority actions in order, one uncomfortable action to do before noon, one thing to kill/delegate/avoid, and one sentence explaining why this day matters. Do not give generic motivation.",
                    session_id="morning-brief",
                ))
            path = write_report("morning-operating-plan", brief)
            st.markdown(brief)
            st.caption(f"Saved locally to {path.name}")

elif page == "CEO Scoreboard":
    render_ceo_scoreboard()
    st.divider()
    st.subheader("What the score means")
    st.write(
        "The score weights execution most heavily, then opportunity creation, ownership-building, decision velocity, leverage/delegation, relationships, and energy. It is a behavioral leading indicator—not a measure of your worth or a guarantee of financial outcomes."
    )

elif page == "Weekly Review":
    st.subheader("Weekly CEO Review")
    st.caption("Run this once per week. The Chief of Staff uses your tracked check-ins to identify patterns rather than relying on memory.")
    if st.button("Run weekly CEO review", type="primary", use_container_width=True):
        with st.spinner("Reviewing the week..."):
            review = asyncio.run(run_chief(
                "Run my weekly CEO review from the tracked CEO check-ins and operating state. Tell me: 1) where I behaved like an owner, 2) where scarcity/avoidance showed up, 3) what I repeatedly deferred, 4) what created the most opportunity or ownership value, 5) what to stop doing, and 6) exactly three priorities for next week. Be specific and cite patterns from the supplied history.",
                session_id="weekly-ceo-review",
            ))
        path = write_report("weekly-ceo-review", review)
        st.markdown(review)
        st.caption(f"Saved locally to {path.name}")

elif page == "Calendar":
    st.subheader("Calendar intelligence")
    if not calendar_is_connected():
        st.warning("Google Calendar is not connected yet. Wealth OS still works without it.")
    else:
        days_back = st.slider("Days back", 1, 30, 7)
        days_forward = st.slider("Days forward", 1, 14, 2)
        try:
            events = list_events(days_back=days_back, days_forward=days_forward)
            st.dataframe([e.to_dict() for e in events], use_container_width=True, hide_index=True)
            if st.button("Audit my time against my goals", type="primary", use_container_width=True):
                digest = calendar_digest(days_back=days_back, days_forward=days_forward)
                result = asyncio.run(run_chief(
                    digest + "\n\nAudit this calendar against my stated priorities and recent CEO check-ins. Categorize time into opportunity creation, ownership-building, relationships, operations/admin, and reactive/low-value work. Give me exactly three calendar changes for next week.",
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
        st.session_state["cre_metrics"] = deal.metrics()
        st.session_state["cre_flags"] = kill_flags(st.session_state["cre_metrics"])

    if "cre_metrics" in st.session_state:
        metrics = st.session_state["cre_metrics"]
        flags = st.session_state["cre_flags"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Going-in cap", f"{metrics['going_in_cap_rate']:.2%}")
        c2.metric("Yield on cost", f"{metrics['stabilized_yield_on_cost']:.2%}")
        c3.metric("Current DSCR", "N/A" if metrics['current_dscr'] is None else f"{metrics['current_dscr']:.2f}x")
        c4.metric("Cash-on-cash", "N/A" if metrics['current_cash_on_cash'] is None else f"{metrics['current_cash_on_cash']:.2%}")
        st.write("**Stress test**", metrics["stress"])
        if flags:
            for flag in flags:
                st.error(flag)
        else:
            st.success("No automatic kill flags were triggered. This does not replace diligence.")
        if st.button("Ask Deal Agent to interpret", use_container_width=True):
            result = asyncio.run(run_chief(
                "Use the Deal Agent to interpret this underwriting. Identify missing diligence, challenge assumptions, and conclude pursue, investigate, renegotiate, park, or kill.\n\n" + json.dumps({"metrics": metrics, "kill_flags": flags}, default=str, indent=2),
                session_id="cre-dashboard",
                include_calendar=False,
            ))
            st.markdown(result)

elif page == "Deals":
    st.subheader("Deal pipeline")
    if state.deals:
        st.dataframe(state.deals, use_container_width=True, hide_index=True)
    else:
        st.info("No deals entered yet.")
    deal_text = st.text_area("Describe a deal or opportunity that needs a decision", height=180)
    if st.button("Qualify this opportunity", type="primary", use_container_width=True) and deal_text.strip():
        result = asyncio.run(run_chief(
            "Use the Deal Agent. Seek bad news first, apply kill criteria, identify missing inputs, and conclude pursue, investigate, renegotiate, park, or kill.\n\n" + deal_text,
            session_id="deal-desk",
        ))
        st.markdown(result)

elif page == "Relationships":
    st.subheader("Relationship portfolio")
    if state.relationships:
        st.dataframe(state.relationships, use_container_width=True, hide_index=True)
    else:
        st.info("No relationships entered yet.")
    if st.button("Choose this week's relationship deposits", type="primary", use_container_width=True):
        result = asyncio.run(run_chief(
            "Review my relationships and recent CEO check-ins. Recommend exactly three high-value relationship deposits for this week. Prefer helping, thanking, introducing, or reconnecting over asking for something.",
            session_id="relationships",
        ))
        st.markdown(result)

elif page == "State Editor":
    st.subheader("Structured operating state")
    st.caption("Your private operating facts live locally and are gitignored.")
    raw = st.text_area("State JSON", value=state.model_dump_json(indent=2), height=600)
    if st.button("Validate and save state", type="primary", use_container_width=True):
        try:
            updated = OperatingState.model_validate(json.loads(raw))
            save_state(updated, reason="dashboard_state_editor")
            st.success("State validated and saved")
        except Exception as exc:
            st.error(f"Invalid state: {exc}")
