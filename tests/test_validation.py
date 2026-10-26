"""Money cross-check and duplicate-detection proofs."""

from invoice_reimbursement.extraction import parse_invoice
from invoice_reimbursement.validation import DuplicateRegistry, check_money

BASE = (
    "VENDOR: Harbor Office Supply\nINVOICE: INV-100\nDATE: 2026-10-05\n"
    "EMPLOYEE: Alex Rivera\nCATEGORY: office\n"
    "LINE: Paper | 2 | 12.50 | 25.00\nLINE: Organizer | 1 | 40.00 | 40.00\n"
    "SUBTOTAL: 65.00\nTAX: 5.20\nTAX_RATE: 0.08\nTOTAL: 70.20\n")


def test_money_checks_pass_on_clean_invoice():
    assert check_money(parse_invoice(BASE)) == []


def test_money_line_sum_mismatch_fails():
    broken = BASE.replace("SUBTOTAL: 65.00", "SUBTOTAL: 60.00")
    failures = check_money(parse_invoice(broken))
    assert any("line items sum" in f for f in failures)


def test_money_total_mismatch_fails():
    broken = BASE.replace("TOTAL: 70.20", "TOTAL: 71.20")
    failures = check_money(parse_invoice(broken))
    assert any("subtotal" in f and "total" in f for f in failures)


def test_money_tax_arithmetic_fails():
    broken = BASE.replace("TAX: 5.20", "TAX: 9.99")
    failures = check_money(parse_invoice(broken))
    assert any("tax" in f.lower() for f in failures)


def test_money_line_quantity_price_mismatch_fails():
    broken = BASE.replace("LINE: Paper | 2 | 12.50 | 25.00",
                          "LINE: Paper | 2 | 12.50 | 30.00")
    failures = check_money(parse_invoice(broken))
    assert any("Paper" in f for f in failures)


def test_duplicate_invoice_detected():
    registry = DuplicateRegistry()
    assert registry.check(parse_invoice(BASE)) is None
    second = registry.check(parse_invoice(BASE))
    assert second is not None and "duplicate" in second


def test_duplicate_case_insensitive_invoice_number():
    registry = DuplicateRegistry()
    registry.check(parse_invoice(BASE))
    variant = BASE.replace("INV-100", "inv-100")
    assert registry.check(parse_invoice(variant)) is not None


def test_different_total_is_not_duplicate():
    registry = DuplicateRegistry()
    registry.check(parse_invoice(BASE))
    variant = BASE.replace("TOTAL: 70.20", "TOTAL: 70.21")
    # Total changed, so money checks would fail elsewhere, but the
    # duplicate key (vendor, number, total) no longer matches.
    assert registry.check(parse_invoice(variant)) is None


def test_extraction_confidence_drops_on_missing_fields():
    sparse = "VENDOR: Harbor Office Supply\nINVOICE: INV-101\n"
    ext = parse_invoice(sparse)
    assert ext.confidence < 1.0
    assert ext.problems
