from wealth_os.cre import CREDebt, CREDeal, kill_flags


def test_debt_service_and_metrics_are_positive():
    debt = CREDebt(loan_amount=1_500_000, interest_rate=0.065, amortization_years=25)
    deal = CREDeal(
        name="Example",
        purchase_price=2_500_000,
        current_noi=175_000,
        stabilized_noi=225_000,
        closing_costs=50_000,
        capex=200_000,
        debt=debt,
        exit_cap_rate=0.07,
    )
    metrics = deal.metrics()
    assert metrics["annual_debt_service"] > 0
    assert metrics["going_in_cap_rate"] == 0.07
    assert metrics["equity_required"] == 1_250_000
    assert metrics["projected_exit_value"] > 0


def test_stress_case_can_trigger_coverage_flag():
    debt = CREDebt(loan_amount=1_900_000, interest_rate=0.08, amortization_years=20)
    deal = CREDeal(
        name="Thin coverage",
        purchase_price=2_300_000,
        current_noi=150_000,
        stabilized_noi=165_000,
        debt=debt,
        exit_cap_rate=0.075,
    )
    flags = kill_flags(deal.metrics())
    assert any("DSCR" in flag for flag in flags)
