"""End-to-end pipeline: ingest -> extract -> validate -> policy + RAG
-> decision -> human-review gate. Every decision carries rule citations and
the retrieved policy passages that support it, so it is auditable."""

from __future__ import annotations

from decimal import Decimal

from . import policy as policy_mod
from .extraction import parse_invoice
from .gates import ReviewGate
from .models import Decision
from .rag import load_passages, retrieve
from .validation import DuplicateRegistry, check_money

LOW_CONFIDENCE_THRESHOLD = 0.7


def _to_cents(value: Decimal | None) -> int:
    if value is None:
        return 0
    return int((value * 100).to_integral_value())


def run_claim(text: str, claim_id: str, duplicates: DuplicateRegistry | None = None,
              passages: list | None = None, gate: ReviewGate | None = None) -> Decision:
    ext = parse_invoice(text)
    duplicates = duplicates or DuplicateRegistry()
    passages = passages if passages is not None else load_passages()
    reasons = list(ext.problems)
    failures = check_money(ext)
    reasons.extend(failures)
    dup = duplicates.check(ext)
    if dup:
        reasons.append(dup)
    total_cents = _to_cents(ext.total)
    citations, policy_failures = policy_mod.match_policy(ext.category, total_cents)
    reasons.extend(policy_failures)
    retrieved = retrieve(f"{ext.category} reimbursement cap receipt approval",
                         passages, top_k=3, boost_terms={ext.category})
    retrieved_ids = [p["rule_id"] for p in retrieved]
    needs_review = (
        ext.confidence < LOW_CONFIDENCE_THRESHOLD
        or bool(failures)
        or bool(policy_failures)
        or dup is not None
        or total_cents > policy_mod.APPROVAL_THRESHOLD_CENTS
    )
    if dup is not None:
        outcome, payable = "REJECTED", 0
    elif needs_review:
        outcome, payable = "NEEDS_REVIEW", 0
        if gate is not None:
            gate.request_review(claim_id, "; ".join(reasons) or "review required")
    else:
        outcome, payable = "APPROVED", total_cents
    return Decision(claim_id=claim_id, outcome=outcome, payable_cents=payable,
                    citations=citations, retrieved_passages=retrieved_ids,
                    reasons=reasons, confidence=ext.confidence)
