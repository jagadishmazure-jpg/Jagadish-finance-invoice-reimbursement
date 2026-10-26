"""Notification channel. Dry run is the default; real sending needs an
explicit opt-in and is refused outright when CI is detected. No credential
is read, stored, or accepted anywhere in this module."""

from __future__ import annotations

import os

from .redaction import redact


class NotifyError(Exception):
    pass


def send_notification(to: str, subject: str, body: str,
                      dry_run: bool = True, confirm_send: bool = False) -> dict:
    """Send (or dry-run) a notification. Redacted body is returned in both cases."""
    record = {"to": redact(to), "subject": redact(subject),
              "body": redact(body), "sent": False, "dry_run": dry_run}
    if dry_run:
        return record
    if not confirm_send:
        raise NotifyError("sending requires explicit confirm_send=True opt-in")
    if os.environ.get("CI"):
        raise NotifyError("sending is refused in CI")
    # No transport is wired in this scaffold: returning sent=True would be a
    # claim without a mechanism, so even opted-in calls stay recorded, unsent.
    record["note"] = "no transport configured; recorded only"
    return record
