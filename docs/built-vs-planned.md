# Built vs planned

| Status | Item | Evidence |
| --- | --- | --- |
| Built | Invoice ingestion + typed extraction + confidence | `extraction.py`, tests in `test_validation.py` |
| Built | Money cross-checks (lines, subtotal, tax, total) | `validation.py`, money failure tests |
| Built | Duplicate-invoice detection | `DuplicateRegistry`, duplicate tests |
| Built | Policy matching with per-decision rule citations | `policy.py`, policy tests |
| Built | RAG retrieval of the governing passage | `rag.py`, retrieval tests |
| Built | Human-review gate (bypass/reject/absent/low-confidence/contradicting) | `gates.py`, gate tests |
| Built | Named-person, single-use, scoped, expiring approvals | `approvals.py`, approval tests |
| Built | View-only SQLite authorizer + row cap | `store.py`, authorizer + row-cap tests |
| Built | PII redaction incl. cards and emails | `redaction.py`, redaction tests |
| Built | Negative-cost rejection, hashed brand blocklist, dry-run notifications | `budget.py`, `brandcheck.py`, `notify.py` |
| Built | Demo + docs + knowledge notes | `demo.py`, `docs/`, `knowledge/` |
| Written-not-run | Nothing shipped untested | Full suite green (64 tests) |
| Planned | PDF/image invoice parsing | — |
| Planned | Multi-currency and mixed-rate invoices | — |
| Planned | Embeddings-based retrieval behind the same interface | — |
| Planned | Web UI for the human-review queue | — |
| Planned | Persistent audit store with signed decision records | — |
