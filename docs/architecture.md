# Architecture

```mermaid
flowchart TD
    A[Invoice text record] --> B[extraction.py: typed fields + confidence]
    B --> C[validation.py: money checks + duplicate registry]
    C --> D[policy.py: rulebook matching + citations]
    D --> E[rag.py: keyword retrieval over data/policy_rulebook.md]
    E --> F[pipeline.py: decision]
    F -->|APPROVED| G[store.py: view-only audit store]
    F -->|NEEDS_REVIEW| H[gates.py: human-review gate]
    F -->|REJECTED| G
    H -->|named approval| I[approvals.py: single-use, scoped, expiring]
    I --> G
    B --> J[redaction.py: cards, emails, phones, SSNs masked]
    G --> K[notify.py: dry-run notification]
```

## Module map

| Module | Job |
| --- | --- |
| `extraction.py` | Parse the record; score confidence; drop bank/card fields |
| `validation.py` | Decimal money checks; duplicate registry |
| `policy.py` | Synthetic rulebook; per-decision rule citations |
| `rag.py` | Deterministic keyword retrieval over the rulebook |
| `gates.py` | Human-review gate with strict consent handling |
| `approvals.py` | Named-person, single-use, scoped, expiring approvals |
| `store.py` | SQLite with a view-only authorizer and a fetchmany row cap |
| `budget.py` | Cost inputs that reject negatives |
| `notify.py` | Dry-run-by-default notifications, refused in CI |
| `brandcheck.py` | Hashed blocklist guard for names the repo must not use |
| `pipeline.py` | Orchestrates the whole flow into one auditable decision |

## Data flow

Raw text never reaches the audit store unexamined: extraction strips
sensitive fields, validation and policy checks run on Decimal values, and
only the decision (outcome, payable cents, citations, retrieved passages,
reasons) is recorded. Reads of that store go through public views only.
