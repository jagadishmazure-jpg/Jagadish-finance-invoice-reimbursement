# Knowledge notes — distilled patterns

Notes written in the author's own words after reading a published
programme brochure about AI in finance. No brochure wording is copied
here; an 8-word overlap check against the extracted brochure text
returns 0 hits (see `tools/overlap_check.py`).

## Patterns taken from the source, restated

1. **Regulated work needs a paper trail, not just an answer.** In
   finance, a system that cannot show its reasoning will not be trusted,
   however accurate it looks. This repo therefore records, per decision:
   the rules cited, the passages retrieved, and the reasons a claim went
   to review.
2. **Retrieval grounds decisions in written policy.** Rather than letting
   a model restate policy from memory, the pipeline fetches the governing
   passage from a rulebook file and attaches it to the decision. The
   passage is the evidence; the model (or, here, the keyword scorer) is
   only the finder.
3. **Human oversight belongs on the risky tail, not on every item.**
   Routine clean claims can flow through; the scarce human attention goes
   to low-confidence reads, arithmetic failures, policy breaches, and
   large amounts. That is the shape of the gate in this repo.
4. **Explainability is a design input, not a report added later.** The
   decision record was designed before the pipeline: outcome, payable
   amount, citations, passages, reasons, confidence. Everything the
   pipeline computes must fit that record, or it does not ship.
5. **Governance is part of the workflow, not a separate review board.**
   Caps, thresholds, duplicate rules, and approval expiry live inside the
   decision path, enforced by code and tests, rather than documented
   beside it.

## Patterns deliberately not copied

- The brochure's programme structure, course list, and marketing claims
  are irrelevant to this build and are not reflected here.
- No real-world dataset, vendor claim, or institutional endorsement is
  used or implied. All firms, people, invoices, and rules here are
  invented.
