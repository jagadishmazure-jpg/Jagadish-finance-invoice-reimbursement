"""Money cross-checks and duplicate detection. All arithmetic uses Decimal
and is rounded to cents, so floating-point drift can never approve a claim."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from .models import Extraction
from .redaction import safe_message

CENT = Decimal("0.01")
TOLERANCE = Decimal("0.01")


def _cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class ValidationFailure(Exception):
    """Raised with a redacted message whenever a check fails."""


def check_money(ext: Extraction) -> list:
    """Return a list of failure strings (empty means every check passed)."""
    failures = []
    if ext.lines and ext.subtotal is not None:
        line_sum = sum((li.amount for li in ext.lines), Decimal("0"))
        if abs(_cents(line_sum) - _cents(ext.subtotal)) > TOLERANCE:
            failures.append(
                safe_message(
                    f"line items sum to {line_sum} but subtotal states {ext.subtotal}"
                )
            )
    if ext.subtotal is not None and ext.tax is not None and ext.total is not None:
        if abs(_cents(ext.subtotal + ext.tax) - _cents(ext.total)) > TOLERANCE:
            failures.append(
                safe_message(
                    f"subtotal {ext.subtotal} + tax {ext.tax} != total {ext.total}"
                )
            )
    if ext.subtotal is not None and ext.tax is not None and ext.tax_rate is not None:
        expected_tax = _cents(ext.subtotal * ext.tax_rate)
        if abs(expected_tax - _cents(ext.tax)) > TOLERANCE:
            failures.append(
                safe_message(
                    f"tax {ext.tax} != subtotal {ext.subtotal} * rate {ext.tax_rate} "
                    f"(expected {expected_tax})"
                )
            )
    if ext.lines:
        for li in ext.lines:
            expected = _cents(li.quantity * li.unit_price)
            if abs(expected - _cents(li.amount)) > TOLERANCE:
                failures.append(
                    safe_message(
                        f"line '{li.description}': {li.quantity} x {li.unit_price} "
                        f"!= {li.amount}"
                    )
                )
    return failures


class DuplicateRegistry:
    """In-memory duplicate detector keyed on vendor + invoice number + total."""

    def __init__(self):
        self._seen = set()

    def check(self, ext: Extraction) -> str | None:
        if not ext.vendor or not ext.invoice_number or ext.total is None:
            return None
        key = (ext.vendor.lower(), ext.invoice_number.strip().upper(),
               str(_cents(ext.total)))
        if key in self._seen:
            return safe_message(
                f"duplicate invoice: vendor {ext.vendor}, "
                f"number {ext.invoice_number}, total {ext.total}"
            )
        self._seen.add(key)
        return None
