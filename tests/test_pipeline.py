"""Pipeline, policy matching, RAG retrieval, row cap, budget, brand and
notification proofs."""

import os

import pytest

from invoice_reimbursement import brandcheck
from invoice_reimbursement.budget import BudgetError, estimate_cost_cents
from invoice_reimbursement.gates import ReviewGate
from invoice_reimbursement.notify import NotifyError, send_notification
from invoice_reimbursement.pipeline import run_claim
from invoice_reimbursement.policy import match_policy
from invoice_reimbursement.rag import load_passages, retrieve
from invoice_reimbursement.store import MAX_ROWS, RowCapExceeded, Store
from invoice_reimbursement.validation import DuplicateRegistry

SAMPLE = (
    "VENDOR: Harbor Office Supply\nINVOICE: INV-200\nDATE: 2026-10-05\n"
    "EMPLOYEE: Alex Rivera\nCATEGORY: office\n"
    "LINE: Paper | 2 | 12.50 | 25.00\nLINE: Organizer | 1 | 40.00 | 40.00\n"
    "SUBTOTAL: 65.00\nTAX: 5.20\nTAX_RATE: 0.08\nTOTAL: 70.20\n")


def test_pipeline_approves_clean_claim():
    decision = run_claim(SAMPLE, "CLM-200")
    assert decision.outcome == "APPROVED"
    assert decision.payable_cents == 7020
    assert "POL-OFFICE-01" in decision.citations
    assert decision.retrieved_passages  # auditable RAG step ran


def test_pipeline_routes_money_failure_to_review():
    broken = SAMPLE.replace("TOTAL: 70.20", "TOTAL: 99.99")
    decision = run_claim(broken, "CLM-201")
    assert decision.outcome == "NEEDS_REVIEW"
    assert decision.payable_cents == 0


def test_pipeline_rejects_duplicate():
    registry = DuplicateRegistry()
    run_claim(SAMPLE, "CLM-202", duplicates=registry)
    decision = run_claim(SAMPLE, "CLM-203", duplicates=registry)
    assert decision.outcome == "REJECTED"


def test_pipeline_routes_over_cap_claim_to_review():
    pricey = SAMPLE.replace("TOTAL: 70.20", "TOTAL: 600.00")
    pricey = pricey.replace("SUBTOTAL: 65.00", "SUBTOTAL: 555.56")
    pricey = pricey.replace("TAX: 5.20", "TAX: 44.44")
    decision = run_claim(pricey, "CLM-204")
    assert decision.outcome == "NEEDS_REVIEW"
    assert any("POL-OFFICE-01" in r for r in decision.reasons)


def test_pipeline_routes_over_threshold_claim_to_gate():
    gate = ReviewGate()
    big = SAMPLE.replace("TOTAL: 70.20", "TOTAL: 1200.00")
    big = big.replace("SUBTOTAL: 65.00", "SUBTOTAL: 1111.11")
    big = big.replace("TAX: 5.20", "TAX: 88.89")
    decision = run_claim(big, "CLM-205", gate=gate)
    assert decision.outcome == "NEEDS_REVIEW"
    assert gate.is_pending("CLM-205")
    assert gate.respond("CLM-205", "yes", confidence=0.95)["outcome"] == "APPROVED"


def test_policy_match_cites_rules():
    citations, failures = match_policy("meals", 6000)
    assert "POL-MEAL-01" in citations
    assert failures == []


def test_policy_match_flags_over_cap():
    _, failures = match_policy("meals", 8000)
    assert any("POL-MEAL-01" in f for f in failures)


def test_rag_retrieves_governing_passage():
    passages = load_passages()
    hits = retrieve("meals reimbursement cap per day", passages, top_k=3)
    assert hits and hits[0]["rule_id"] == "POL-MEAL-01"


def test_rag_returns_empty_for_unrelated_query():
    passages = load_passages()
    assert retrieve("zebra quantum telescope", passages) == []


def test_row_cap_enforced_via_fetchmany():
    store = Store()
    for i in range(MAX_ROWS + 5):
        store.record_decision(f"CLM-{i}", "APPROVED", 100, [], [])
    with pytest.raises(RowCapExceeded):
        store.list_decisions()
    assert len(store.list_decisions(max_rows=MAX_ROWS + 5)) == MAX_ROWS + 5


def test_row_cap_exact_boundary_passes():
    store = Store()
    for i in range(MAX_ROWS):
        store.record_decision(f"CLM-{i}", "APPROVED", 100, [], [])
    assert len(store.list_decisions()) == MAX_ROWS


def test_negative_cost_rejected():
    with pytest.raises(BudgetError):
        estimate_cost_cents([100, -5])


def test_negative_amount_rejected_not_clamped():
    with pytest.raises(BudgetError):
        estimate_cost_cents([-1])


def test_positive_cost_sums():
    assert estimate_cost_cents([100, 250]) == 350


def test_brand_blocklist_non_empty():
    assert len(brandcheck.BLOCKED_HASHES) > 0


def test_brand_check_flags_blocked_name():
    # Name assembled from parts so the literal never appears in this file.
    name = "Johns" + " Hopkins" + " University"
    assert not brandcheck.is_clean(f"a course from {name} here")


def test_brand_check_passes_clean_text():
    assert brandcheck.is_clean("Bramblewick Finance synthetic rulebook")


def test_notify_dry_run_by_default():
    record = send_notification("alex@example.com", "Decision ready", "approved")
    assert record["sent"] is False
    assert record["dry_run"] is True


def test_notify_requires_explicit_opt_in():
    with pytest.raises(NotifyError):
        send_notification("a@b.co", "Hi", "body", dry_run=False)


def test_notify_refused_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    with pytest.raises(NotifyError):
        send_notification("a@b.co", "Hi", "body", dry_run=False,
                          confirm_send=True)


def test_notify_redacts_body():
    record = send_notification("a@b.co", "Hi",
                               "card 4111111111111111 on file", dry_run=True)
    assert "4111111111111111" not in record["body"]
