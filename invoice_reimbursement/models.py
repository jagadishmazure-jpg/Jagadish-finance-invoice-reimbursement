"""Typed records for the reimbursement pipeline. Money is Decimal cents."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class LineItem:
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal


@dataclass
class Extraction:
    vendor: str = ""
    invoice_number: str = ""
    date: str = ""
    employee: str = ""
    category: str = ""
    lines: list = field(default_factory=list)
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    tax_rate: Decimal | None = None
    total: Decimal | None = None
    confidence: float = 1.0
    problems: list = field(default_factory=list)
    # Banking or card details are never stored: see extraction.py.
    dropped_sensitive_fields: list = field(default_factory=list)


@dataclass
class PolicyRule:
    rule_id: str
    category: str
    cap_cents: int | None
    text: str


@dataclass
class Decision:
    claim_id: str
    outcome: str  # APPROVED, NEEDS_REVIEW, REJECTED
    payable_cents: int
    citations: list = field(default_factory=list)
    retrieved_passages: list = field(default_factory=list)
    reasons: list = field(default_factory=list)
    confidence: float = 0.0
