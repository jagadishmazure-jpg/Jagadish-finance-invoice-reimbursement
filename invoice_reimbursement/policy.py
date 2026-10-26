"""Synthetic reimbursement rulebook for the fictional firm Bramblewick Finance.

These rules are invented for this portfolio project. They cite no real
employer policy and no external document. Each rule carries a stable id so
every decision can point at the exact rule that governed it.
"""

from __future__ import annotations

from .models import PolicyRule

RULES = [
    PolicyRule("POL-MEAL-01", "meals", 7500,
               "Meals are reimbursed up to $75.00 per claim day."),
    PolicyRule("POL-LODGE-01", "lodging", 18000,
               "Lodging is reimbursed up to $180.00 per night."),
    PolicyRule("POL-OFFICE-01", "office", 50000,
               "Office supplies are reimbursed up to $500.00 per claim."),
    PolicyRule("POL-TRAVEL-01", "travel", 100000,
               "Travel is reimbursed up to $1000.00 per claim; a trip log is required."),
    PolicyRule("POL-RECEIPT-01", "*", None,
               "Any single line above $75.00 must carry a receipt reference."),
    PolicyRule("POL-THRESHOLD-01", "*", None,
               "Claims above $1000.00 need a named-person approval before payment."),
    PolicyRule("POL-DUP-01", "*", None,
               "A vendor invoice number may be reimbursed only once."),
]

APPROVAL_THRESHOLD_CENTS = 100000
RECEIPT_LINE_THRESHOLD_CENTS = 7500


def rules_for(category: str) -> list:
    return [r for r in RULES if r.category in (category, "*")]


def match_policy(category: str, total_cents: int) -> tuple:
    """Return (citations, failures) for a category total against the rulebook."""
    citations, failures = [], []
    for rule in rules_for(category):
        citations.append(rule.rule_id)
        if rule.cap_cents is not None and total_cents > rule.cap_cents:
            failures.append(
                f"{rule.rule_id}: total ${total_cents / 100:.2f} exceeds "
                f"cap ${rule.cap_cents / 100:.2f} for category '{category}'"
            )
    if total_cents > APPROVAL_THRESHOLD_CENTS:
        failures.append("POL-THRESHOLD-01: amount above $1000.00 needs approval")
    return citations, failures
