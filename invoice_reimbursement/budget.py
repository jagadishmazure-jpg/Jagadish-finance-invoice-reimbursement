"""Cost/budget inputs. Negative amounts are rejected, never clamped."""

from __future__ import annotations

from decimal import Decimal


class BudgetError(Exception):
    pass


def validate_amount_cents(amount_cents: int) -> int:
    if not isinstance(amount_cents, int) or isinstance(amount_cents, bool):
        raise BudgetError("amount must be an integer number of cents")
    if amount_cents < 0:
        raise BudgetError(f"negative amount rejected: {amount_cents}")
    return amount_cents


def estimate_cost_cents(line_costs_cents: list) -> int:
    """Sum per-line cost estimates; any negative input rejects the whole estimate."""
    total = 0
    for cost in line_costs_cents:
        total += validate_amount_cents(cost)
    return total


def estimate_cost_decimal(line_costs) -> Decimal:
    total = Decimal("0")
    for cost in line_costs:
        value = Decimal(str(cost))
        if value < 0:
            raise BudgetError(f"negative cost rejected: {cost}")
        total += value
    return total
