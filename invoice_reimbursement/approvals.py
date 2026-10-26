"""Named-person, single-use, scoped, expiring approvals.

An approval names exactly one approver, covers exactly one claim up to a
stated amount, can be used once, and stops working after its expiry. Every
violation raises ApprovalError instead of silently degrading.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


class ApprovalError(Exception):
    pass


@dataclass
class Approval:
    approver: str
    claim_id: str
    scope_amount_cents: int
    expires_at: datetime
    used: bool = False

    def use(self, claim_id: str, amount_cents: int,
            now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)
        if not self.approver.strip():
            raise ApprovalError("approval requires a named person")
        if self.used:
            raise ApprovalError("approval is single-use and already consumed")
        if claim_id != self.claim_id:
            raise ApprovalError("approval is scoped to a different claim")
        if amount_cents > self.scope_amount_cents:
            raise ApprovalError("amount exceeds the approval scope")
        if now > self.expires_at:
            raise ApprovalError("approval has expired")
        self.used = True


def make_approval(approver: str, claim_id: str, scope_amount_cents: int,
                  ttl_minutes: int = 60,
                  now: datetime | None = None) -> Approval:
    now = now or datetime.now(timezone.utc)
    if not approver or not approver.strip():
        raise ApprovalError("approval requires a named person")
    if scope_amount_cents < 0:
        raise ApprovalError("approval scope must not be negative")
    return Approval(approver=approver.strip(), claim_id=claim_id,
                    scope_amount_cents=scope_amount_cents,
                    expires_at=now + timedelta(minutes=ttl_minutes))
