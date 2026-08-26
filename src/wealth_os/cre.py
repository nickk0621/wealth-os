from __future__ import annotations

from dataclasses import dataclass, asdict
from math import pow
from typing import Any


@dataclass
class CREDebt:
    loan_amount: float
    interest_rate: float
    amortization_years: int = 25
    term_years: int = 5
    interest_only_years: int = 0

    def annual_debt_service(self) -> float:
        if self.loan_amount <= 0:
            return 0.0
        if self.interest_only_years > 0:
            return self.loan_amount * self.interest_rate
        monthly_rate = self.interest_rate / 12
        n = self.amortization_years * 12
        if monthly_rate == 0:
            return self.loan_amount / self.amortization_years
        payment = self.loan_amount * monthly_rate / (1 - pow(1 + monthly_rate, -n))
        return payment * 12


@dataclass
class CREDeal:
    name: str
    purchase_price: float
    current_noi: float
    stabilized_noi: float
    closing_costs: float = 0.0
    capex: float = 0.0
    debt: CREDebt | None = None
    exit_cap_rate: float = 0.07
    hold_years: int = 5
    annual_noi_growth: float = 0.02

    @property
    def total_basis(self) -> float:
        return self.purchase_price + self.closing_costs + self.capex

    @property
    def equity_required(self) -> float:
        loan = self.debt.loan_amount if self.debt else 0.0
        return max(self.total_basis - loan, 0.0)

    @property
    def going_in_cap_rate(self) -> float:
        return self.current_noi / self.purchase_price if self.purchase_price else 0.0

    @property
    def stabilized_yield_on_cost(self) -> float:
        return self.stabilized_noi / self.total_basis if self.total_basis else 0.0

    @property
    def annual_debt_service(self) -> float:
        return self.debt.annual_debt_service() if self.debt else 0.0

    @property
    def current_dscr(self) -> float | None:
        ds = self.annual_debt_service
        return self.current_noi / ds if ds else None

    @property
    def stabilized_dscr(self) -> float | None:
        ds = self.annual_debt_service
        return self.stabilized_noi / ds if ds else None

    @property
    def current_cash_flow_after_debt(self) -> float:
        return self.current_noi - self.annual_debt_service

    @property
    def current_cash_on_cash(self) -> float | None:
        equity = self.equity_required
        return self.current_cash_flow_after_debt / equity if equity else None

    def projected_exit_noi(self) -> float:
        return self.stabilized_noi * pow(1 + self.annual_noi_growth, max(self.hold_years - 1, 0))

    def projected_exit_value(self) -> float:
        return self.projected_exit_noi() / self.exit_cap_rate if self.exit_cap_rate else 0.0

    def stress_test(
        self,
        noi_decline: float = 0.15,
        exit_cap_expansion: float = 0.01,
        interest_rate_shock: float = 0.02,
    ) -> dict[str, Any]:
        stressed_noi = self.current_noi * (1 - noi_decline)
        stressed_exit_cap = self.exit_cap_rate + exit_cap_expansion
        stressed_exit_value = self.projected_exit_noi() / stressed_exit_cap if stressed_exit_cap else 0.0

        stressed_debt_service = self.annual_debt_service
        if self.debt:
            shocked = CREDebt(
                loan_amount=self.debt.loan_amount,
                interest_rate=self.debt.interest_rate + interest_rate_shock,
                amortization_years=self.debt.amortization_years,
                term_years=self.debt.term_years,
                interest_only_years=0,
            )
            stressed_debt_service = shocked.annual_debt_service()

        stressed_dscr = stressed_noi / stressed_debt_service if stressed_debt_service else None
        return {
            "stressed_noi": stressed_noi,
            "stressed_debt_service": stressed_debt_service,
            "stressed_dscr": stressed_dscr,
            "stressed_exit_cap_rate": stressed_exit_cap,
            "stressed_exit_value": stressed_exit_value,
            "value_change_vs_purchase": stressed_exit_value - self.purchase_price,
        }

    def metrics(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "purchase_price": self.purchase_price,
            "total_basis": self.total_basis,
            "equity_required": self.equity_required,
            "going_in_cap_rate": self.going_in_cap_rate,
            "stabilized_yield_on_cost": self.stabilized_yield_on_cost,
            "annual_debt_service": self.annual_debt_service,
            "current_dscr": self.current_dscr,
            "stabilized_dscr": self.stabilized_dscr,
            "current_cash_flow_after_debt": self.current_cash_flow_after_debt,
            "current_cash_on_cash": self.current_cash_on_cash,
            "projected_exit_noi": self.projected_exit_noi(),
            "projected_exit_value": self.projected_exit_value(),
            "stress": self.stress_test(),
            "raw": asdict(self),
        }


def kill_flags(metrics: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if metrics.get("current_dscr") is not None and metrics["current_dscr"] < 1.10:
        flags.append("Current DSCR is below 1.10x; debt coverage is fragile.")
    if metrics.get("stabilized_dscr") is not None and metrics["stabilized_dscr"] < 1.25:
        flags.append("Stabilized DSCR is below 1.25x; the business plan may not create enough coverage.")
    stress = metrics.get("stress", {})
    if stress.get("stressed_dscr") is not None and stress["stressed_dscr"] < 1.0:
        flags.append("Stress-case DSCR falls below 1.0x; the property would not cover debt service from NOI.")
    if metrics.get("stabilized_yield_on_cost", 0) <= metrics.get("raw", {}).get("exit_cap_rate", 0):
        flags.append("Stabilized yield on cost does not exceed the assumed exit cap rate; development/value-add spread is weak.")
    return flags
