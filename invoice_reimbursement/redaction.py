"""PII redaction. Card numbers and email addresses are redacted alongside
phone numbers and SSNs. Banking details must never reach logs or errors."""

import re

_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"\b(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-. ]?\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_BANK_HINT = re.compile(r"(?i)\b(account|routing|iban|sort code)\b[^,\n]*")


def redact(text: str) -> str:
    """Return text with card numbers, emails, phones, SSNs and bank hints masked."""
    out = _CARD.sub("[REDACTED:CARD]", str(text))
    out = _EMAIL.sub("[REDACTED:EMAIL]", out)
    out = _SSN.sub("[REDACTED:SSN]", out)
    out = _PHONE.sub("[REDACTED:PHONE]", out)
    out = _BANK_HINT.sub("[REDACTED:BANK]", out)
    return out


def safe_message(text: str) -> str:
    """Build an error/log message that is guaranteed redacted."""
    return redact(text)
