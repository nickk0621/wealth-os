from __future__ import annotations

import asyncio
import json
from datetime import date

import streamlit as st

from .runtime import run_chief
from .state import DailyCheckIn, OperatingState, load_state, save_state, upsert_daily_checkin, write_report

st.set_page_config(page_title="Wealth OS", page_icon="📈", layout="wide")
st.title("Wealth OS")
st.caption("Chief of Staff + wealth, deals, habits, relationships, and CEO reviews")

state = load_state()

with st.sidebar:
    st.header("Operating rhythm")
    page = st.radio("View", ["Today", "Scoreboard", "Deals", "Relationships", "State Editor"])
    if st.button("Run morning brief", use_container_width=True):
        with st.spinner("Chief of Staff is reviewing your operating state..."):
            brief = asyncio.run(run_chief(
                "Give me my morning brief. Identify what matters most today, the top three actions, one thing to kill or avoid, "
                "and any financial/deal/habit risk I should not ignore. Be concise and concrete.",
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

elif page == "Deals":
    st.subheader("Deal pipeline")
    if state.deals:
        st.dataframe(state.deals, use_container_width=True, hide_index=True)
    else:
        st.info("No deals in the pipeline yet.")
    deal_text = st.text_area("Describe a deal to qualify", height=180)
    if st.button("Run Deal Agent", use_container_width=True) and deal_text.strip():
        result = asyncio.run(run_chief(
            "Use the Deal Agent to evaluate this opportunity. Apply the scorecard and kill questions, identify missing inputs, "
            "and conclude pursue, investigate, renegotiate, park, or kill.\n\n" + deal_text,
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
            "Review my relationship portfolio. Recommend the three highest-value relationship deposits or follow-ups for this week. "
            "Prioritize long-term trust and usefulness over asks.",
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
