"""Demo: run the pipeline over the bundled synthetic invoice and print
the decision with its citations and retrieved passages."""

from __future__ import annotations

from pathlib import Path

from .pipeline import run_claim

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_invoice.txt"


def main() -> None:
    decision = run_claim(SAMPLE.read_text(encoding="utf-8"), "CLM-DEMO-001")
    print(f"claim: {decision.claim_id}")
    print(f"outcome: {decision.outcome}")
    print(f"payable_cents: {decision.payable_cents}")
    print(f"confidence: {decision.confidence}")
    print(f"citations: {', '.join(decision.citations)}")
    print(f"retrieved_passages: {', '.join(decision.retrieved_passages)}")
    print(f"reasons: {'; '.join(decision.reasons) or '(none)'}")


if __name__ == "__main__":
    main()
