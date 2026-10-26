"""PII redaction proofs, including card numbers and email addresses, and
the guarantee that banking details never leak into errors or stored fields."""

from invoice_reimbursement.extraction import parse_invoice
from invoice_reimbursement.redaction import redact
from invoice_reimbursement.validation import check_money


def test_redact_card_number():
    text = "paid with card 4111 1111 1111 1111 on file"
    out = redact(text)
    assert "4111" not in out
    assert "[REDACTED:CARD]" in out


def test_redact_card_number_dashes():
    out = redact("card 5500-0055-5555-5559 charged")
    assert "5500" not in out
    assert "[REDACTED:CARD]" in out


def test_redact_email_address():
    out = redact("contact alex.rivera@example.com for the receipt")
    assert "alex.rivera@example.com" not in out
    assert "[REDACTED:EMAIL]" in out


def test_redact_phone_and_ssn():
    out = redact("call 555-123-4567, ssn 123-45-6789")
    assert "555-123-4567" not in out
    assert "123-45-6789" not in out


def test_extraction_drops_bank_field():
    text = (
        "VENDOR: Harbor Office Supply\nINVOICE: INV-7\nDATE: 2026-10-05\n"
        "EMPLOYEE: Alex Rivera\nCATEGORY: office\n"
        "LINE: Paper | 1 | 10.00 | 10.00\nSUBTOTAL: 10.00\nTAX: 0.00\n"
        "TOTAL: 10.00\nBANK: account 987654321 routing 021000021\n")
    ext = parse_invoice(text)
    assert "BANK" in ext.dropped_sensitive_fields
    assert "987654321" not in repr(ext)
    assert "021000021" not in repr(ext)


def test_validation_error_never_contains_card():
    text = (
        "VENDOR: Harbor Office Supply\nINVOICE: INV-8\nDATE: 2026-10-05\n"
        "EMPLOYEE: Alex Rivera\nCATEGORY: office\n"
        "LINE: Paper | 1 | 10.00 | 10.00\nSUBTOTAL: 99.00\nTAX: 0.00\n"
        "TOTAL: 10.00\nCARD: 4111111111111111\n")
    ext = parse_invoice(text)
    failures = check_money(ext)
    assert failures
    joined = " ".join(failures)
    assert "4111111111111111" not in joined
