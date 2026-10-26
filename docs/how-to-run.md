# How to run

Offline first. Standard library only; the only extra tool is pytest for
the test suite. No network, no API key, no cloud account, no database
server — the store is a temporary SQLite file.

```bash
# Full test suite (64 tests)
python3 -m pytest

# Demo decision over the bundled synthetic invoice
python3 -m invoice_reimbursement.demo

# 8-word overlap check against a source text file (source not committed)
python3 tools/overlap_check.py --source /path/to/source.txt
```

Python 3.10+ is required; the suite was run with system Python 3.12.3 and
pytest 9.1.1. Do not create a `.venv` inside the repo (it is gitignored
and excluded from any packaging walk).

## Optional next steps (not wired in)

- Point `rag.load_passages()` at a different rulebook file to model
  another firm's policy set.
- Replace the keyword retriever with an embeddings retriever behind the
  same `retrieve()` signature; the pipeline only consumes rule ids.
- Swap the temporary SQLite file for a persistent path via `Store(path)`.
