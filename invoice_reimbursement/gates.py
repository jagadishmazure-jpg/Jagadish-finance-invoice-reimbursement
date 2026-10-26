"""Human-review gate. Nothing is approved by accident.

A claim enters review only through request_review(). Approval requires an
explicit, unambiguous "yes" at adequate confidence. Anything else — a
rejection, a missing reply, a low-confidence reply, or a self-contradicting
reply such as "yes, wait, no" — leaves the claim unapproved. Calling
approve() without a pending request is a bypass and raises GateError.
"""

from __future__ import annotations

MIN_CONSENT_CONFIDENCE = 0.6
_REJECT_WORDS = ("no", "reject", "deny", "stop", "cancel")
_HEDGE_WORDS = ("wait", "hold", "not yet", "maybe", "unsure")


class GateError(Exception):
    pass


class ReviewGate:
    def __init__(self):
        self._pending = {}  # claim_id -> reason
        self._outcomes = {}  # claim_id -> outcome dict

    def request_review(self, claim_id: str, reason: str) -> None:
        self._pending[claim_id] = reason

    def is_pending(self, claim_id: str) -> bool:
        return claim_id in self._pending

    def respond(self, claim_id: str, consent: str | None,
                confidence: float = 1.0) -> dict:
        if claim_id not in self._pending:
            raise GateError(f"no pending review for claim {claim_id}: bypass denied")
        reason = self._pending.pop(claim_id)
        if consent is None or not str(consent).strip():
            self._outcomes[claim_id] = {"outcome": "ABSENT",
                                        "reason": "no reply recorded"}
            return self._outcomes[claim_id]
        text = str(consent).strip().lower()
        words = set(text.replace(",", " ").split())
        says_yes = "yes" in words or text == "approve"
        says_no = bool(words & set(_REJECT_WORDS))
        hedges = any(h in text for h in _HEDGE_WORDS)
        if says_yes and (says_no or hedges):
            self._outcomes[claim_id] = {
                "outcome": "REJECTED",
                "reason": "self-contradicting consent: yes combined with "
                          "rejection or hesitation wording"}
            return self._outcomes[claim_id]
        if says_no:
            self._outcomes[claim_id] = {"outcome": "REJECTED",
                                        "reason": "reviewer rejected"}
            return self._outcomes[claim_id]
        if not says_yes:
            self._outcomes[claim_id] = {"outcome": "ABSENT",
                                        "reason": "reply was not an explicit yes"}
            return self._outcomes[claim_id]
        if confidence < MIN_CONSENT_CONFIDENCE:
            self._outcomes[claim_id] = {
                "outcome": "LOW_CONFIDENCE",
                "reason": f"consent confidence {confidence} below "
                          f"{MIN_CONSENT_CONFIDENCE}"}
            return self._outcomes[claim_id]
        self._outcomes[claim_id] = {"outcome": "APPROVED",
                                    "reason": f"reviewed: {reason}"}
        return self._outcomes[claim_id]

    def approve_without_request(self, claim_id: str):
        """Deliberately unsupported path: must raise, never approve."""
        raise GateError(f"approval without a pending review is not allowed: {claim_id}")
