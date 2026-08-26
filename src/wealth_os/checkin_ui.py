from __future__ import annotations

from datetime import date

import streamlit as st

from .checkins import DailyCEOCheckIn, dashboard_snapshot, get_checkin, save_checkin, score_checkin


def render_guided_checkin() -> None:
    st.subheader("Daily CEO Check-in")
    st.caption("Answer this in about 10 minutes. Wealth OS will score the behaviors, not just the outcomes.")

    existing = get_checkin() or DailyCEOCheckIn(date=date.today().isoformat())

    with st.form("guided-ceo-checkin"):
        st.markdown("**1. What are the three outcomes that would make today a win?**")
        c1 = st.text_input("Commitment 1", value=existing.commitments[0] if len(existing.commitments) > 0 else "")
        c2 = st.text_input("Commitment 2", value=existing.commitments[1] if len(existing.commitments) > 1 else "")
        c3 = st.text_input("Commitment 3", value=existing.commitments[2] if len(existing.commitments) > 2 else "")

        opportunity_creation = st.text_area(
            "2. What are you doing today to create opportunity / increase pipeline?",
            value=existing.opportunity_creation,
        )
        deal_decision = st.text_area(
            "3. Which deal, project, or decision needs to move, get qualified, or get killed?",
            value=existing.deal_decision,
        )
        ownership_building = st.text_area(
            "4. What are you doing today that builds ownership, equity, recurring cash flow, or a durable asset?",
            value=existing.ownership_building,
        )
        capital_allocation = st.text_area(
            "5. Is there a capital-allocation decision to make or a dollar that lacks an explicit purpose?",
            value=existing.capital_allocation,
        )
        relationship_deposit = st.text_area(
            "6. Who will you help, thank, call, introduce, or reconnect with today?",
            value=existing.relationship_deposit,
        )
        health_energy = st.text_area(
            "7. What will you do to protect energy, health, and decision quality today?",
            value=existing.health_energy,
        )
        kill_delegate_avoid = st.text_area(
            "8. What should you kill, delegate, automate, or refuse today?",
            value=existing.kill_delegate_avoid,
        )
        avoidance_or_fear = st.text_area(
            "9. What uncomfortable thing are you avoiding or hoping not to learn?",
            value=existing.avoidance_or_fear,
        )
        notes = st.text_area("Notes", value=existing.notes)

        submitted = st.form_submit_button("Lock today's commitments", type="primary", use_container_width=True)

    if submitted:
        commitments = [x.strip() for x in [c1, c2, c3] if x.strip()][:3]
        payload = DailyCEOCheckIn(
            date=date.today().isoformat(),
            commitments=commitments,
            opportunity_creation=opportunity_creation.strip(),
            deal_decision=deal_decision.strip(),
            ownership_building=ownership_building.strip(),
            capital_allocation=capital_allocation.strip(),
            relationship_deposit=relationship_deposit.strip(),
            health_energy=health_energy.strip(),
            kill_delegate_avoid=kill_delegate_avoid.strip(),
            avoidance_or_fear=avoidance_or_fear.strip(),
            completed_commitments=existing.completed_commitments,
            notes=notes.strip(),
        )
        save_checkin(payload)
        st.success("Today's CEO check-in is locked and now feeds your dashboard and future coaching.")
        st.rerun()

    current = get_checkin()
    if current:
        st.divider()
        metrics = score_checkin(current)
        a, b = st.columns([1, 2])
        a.metric("CEO behavior score", f"{metrics.overall_score:.0f}/100")
        with b:
            st.markdown("**Today's locked commitments**")
            if current.commitments:
                for item in current.commitments:
                    st.write(f"- {item}")
            else:
                st.write("No commitments locked yet.")

        completed = st.multiselect(
            "Mark completed commitments",
            options=current.commitments,
            default=[x for x in current.completed_commitments if x in current.commitments],
        )
        if st.button("Update completion", use_container_width=True):
            current.completed_commitments = completed
            save_checkin(current)
            st.success("Completion updated")
            st.rerun()


def render_ceo_scoreboard() -> None:
    st.subheader("CEO Scoreboard")
    snapshot = dashboard_snapshot(limit=30)
    rows = snapshot["history"]
    if not rows:
        st.info("Complete your first Daily CEO Check-in to start the scoreboard.")
        return

    latest = rows[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Latest CEO score", f"{latest['overall_score']:.0f}/100")
    c2.metric("Execution rate", f"{latest['execution_rate']:.0f}%")
    c3.metric("Days tracked", len(rows))

    st.line_chart({"CEO score": [r["overall_score"] for r in rows]})

    st.markdown("**Recent pattern log**")
    for row in reversed(rows[-7:]):
        avoidance = row.get("avoidance_or_fear") or "—"
        st.write(f"**{row['date']}** — score {row['overall_score']:.0f}/100 · execution {row['execution_rate']:.0f}%")
        st.caption(f"Avoidance / fear: {avoidance}")
