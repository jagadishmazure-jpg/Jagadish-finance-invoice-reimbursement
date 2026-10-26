"""Confirmation-gate proofs: bypass, reject, absent, low-confidence,
self-contradicting consent, and the happy path."""

import pytest

from invoice_reimbursement.approvals import ApprovalError, make_approval
from invoice_reimbursement.gates import GateError, ReviewGate


def _pending_gate():
    gate = ReviewGate()
    gate.request_review("CLM-9", "amount above threshold")
    return gate


def test_gate_explicit_yes_approves():
    gate = _pending_gate()
    assert gate.respond("CLM-9", "yes", confidence=0.9)["outcome"] == "APPROVED"


def test_gate_bypass_raises():
    gate = ReviewGate()
    with pytest.raises(GateError):
        gate.respond("CLM-9", "yes")


def test_gate_approve_without_request_raises():
    gate = ReviewGate()
    with pytest.raises(GateError):
        gate.approve_without_request("CLM-9")


def test_gate_reject_path():
    gate = _pending_gate()
    assert gate.respond("CLM-9", "no")["outcome"] == "REJECTED"


def test_gate_reject_word_path():
    gate = _pending_gate()
    assert gate.respond("CLM-9", "reject")["outcome"] == "REJECTED"


def test_gate_absent_consent_none():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", None)
    assert outcome["outcome"] == "ABSENT"


def test_gate_absent_consent_empty():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", "   ")
    assert outcome["outcome"] == "ABSENT"


def test_gate_absent_consent_vague():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", "looks fine")
    assert outcome["outcome"] == "ABSENT"


def test_gate_low_confidence_yes_not_approved():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", "yes", confidence=0.3)
    assert outcome["outcome"] == "LOW_CONFIDENCE"


def test_gate_contradicting_consent_yes_wait_no():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", "yes, wait, no")
    assert outcome["outcome"] == "REJECTED"


def test_gate_contradicting_consent_yes_then_no():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", "yes no")
    assert outcome["outcome"] == "REJECTED"


def test_gate_hedged_yes_not_approved():
    gate = _pending_gate()
    outcome = gate.respond("CLM-9", "yes, wait")
    assert outcome["outcome"] == "REJECTED"


# -- approvals: named-person, single-use, scoped, expiring ---------------

def test_approval_named_person_required():
    with pytest.raises(ApprovalError):
        make_approval("  ", "CLM-9", 1000)


def test_approval_single_use():
    approval = make_approval("Priya Nair", "CLM-9", 5000)
    approval.use("CLM-9", 4000)
    with pytest.raises(ApprovalError):
        approval.use("CLM-9", 4000)


def test_approval_scoped_to_claim():
    approval = make_approval("Priya Nair", "CLM-9", 5000)
    with pytest.raises(ApprovalError):
        approval.use("CLM-OTHER", 100)


def test_approval_scoped_to_amount():
    approval = make_approval("Priya Nair", "CLM-9", 5000)
    with pytest.raises(ApprovalError):
        approval.use("CLM-9", 5001)


def test_approval_expired():
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    approval = make_approval("Priya Nair", "CLM-9", 5000, ttl_minutes=1, now=now)
    with pytest.raises(ApprovalError):
        approval.use("CLM-9", 100, now=now + timedelta(minutes=2))


def test_approval_negative_scope_rejected():
    with pytest.raises(ApprovalError):
        make_approval("Priya Nair", "CLM-9", -1)
