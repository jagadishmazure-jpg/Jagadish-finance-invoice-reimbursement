# Real code excerpts and their real output

## Running the pipeline on the bundled sample

```python
from invoice_reimbursement.pipeline import run_claim
from pathlib import Path

text = Path("data/sample_invoice.txt").read_text()
decision = run_claim(text, "CLM-DEMO-001")
print(decision.outcome, decision.payable_cents, decision.citations)
```

Real output:

```
APPROVED 7020 ['POL-OFFICE-01', 'POL-RECEIPT-01', 'POL-THRESHOLD-01', 'POL-DUP-01']
```

## A money failure routes to review, not to payment

```python
broken = text.replace("TOTAL: 70.20", "TOTAL: 99.99")
decision = run_claim(broken, "CLM-201")
print(decision.outcome, decision.payable_cents)
```

Real output:

```
NEEDS_REVIEW 0
```

## The authorizer in one function

```python
def _authorizer(action, param1, param2, db_name, source):
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        if source in ALLOWED_VIEWS or param1 in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_DENY
```

A direct read of a base table has `source=None` and `param1` naming the
base table, so it is denied; a read that arrives through a view carries
the view as `source` (or as `param1` for the view's own columns) and is
allowed. Writes, PRAGMA, and ATTACH through the reader are denied.
