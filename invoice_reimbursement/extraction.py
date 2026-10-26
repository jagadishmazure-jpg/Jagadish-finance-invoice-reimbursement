"""Typed extraction from synthetic invoice text records.

The input format is a plain-text record, one field per line, for example::

    VENDOR: Harbor Office Supply
    INVOICE: INV-1001
    DATE: 2026-10-05
    EMPLOYEE: Alex Rivera
    CATEGORY: office
    LINE: Printer paper | 2 | 12.50 | 25.00
    SUBTOTAL: 25.00
    TAX: 2.00
    TAX_RATE: 0.08
    TOTAL: 27.00

Confidence starts at 1.0 and drops for every missing or unparsable field, so
downstream gates can see exactly how shaky an extraction is. Lines naming
bank accounts, cards, or payment credentials are dropped, never stored.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from .models import Extraction, LineItem
from .redaction import redact

_SENSITIVE_PREFIXES = ("BANK", "CARD", "ACCOUNT", "ROUTING", "IBAN", "PAYMENT")


def _money(raw: str):
    try:
        return Decimal(raw.strip())
    except (InvalidOperation, AttributeError):
        return None


def parse_invoice(text: str) -> Extraction:
    ext = Extraction()
    for raw_line in str(text).splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().upper()
        value = value.strip()
        if key in _SENSITIVE_PREFIXES:
            ext.dropped_sensitive_fields.append(key)
            ext.problems.append(f"sensitive field dropped: {key}")
            continue
        if key == "VENDOR":
            ext.vendor = redact(value)
        elif key == "INVOICE":
            ext.invoice_number = value
        elif key == "DATE":
            ext.date = value
        elif key == "EMPLOYEE":
            ext.employee = redact(value)
        elif key == "CATEGORY":
            ext.category = value.lower()
        elif key == "LINE":
            parts = [p.strip() for p in value.split("|")]
            if len(parts) != 4:
                ext.problems.append(f"unparsable line: {redact(value)}")
                continue
            qty, unit, amount = _money(parts[1]), _money(parts[2]), _money(parts[3])
            if qty is None or unit is None or amount is None:
                ext.problems.append(f"unparsable line amounts: {redact(value)}")
                continue
            ext.lines.append(LineItem(parts[0], qty, unit, amount))
        elif key == "SUBTOTAL":
            ext.subtotal = _money(value)
        elif key == "TAX":
            ext.tax = _money(value)
        elif key == "TAX_RATE":
            ext.tax_rate = _money(value)
        elif key == "TOTAL":
            ext.total = _money(value)
        else:
            ext.problems.append(f"unknown field ignored: {key}")
    # Confidence: penalise missing essentials and every recorded problem.
    for field_name, present in (
        ("vendor", bool(ext.vendor)),
        ("invoice_number", bool(ext.invoice_number)),
        ("date", bool(ext.date)),
        ("category", bool(ext.category)),
        ("total", ext.total is not None),
    ):
        if not present:
            ext.problems.append(f"missing field: {field_name}")
    penalty = 0.15 * sum(1 for p in ext.problems if p.startswith("missing field"))
    penalty += 0.25 * sum(1 for p in ext.problems if not p.startswith("missing field"))
    ext.confidence = round(max(0.0, 1.0 - penalty), 2)
    return ext
