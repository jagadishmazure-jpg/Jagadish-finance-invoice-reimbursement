# Purpose

Finance teams spend much of their time checking expense paperwork by hand:
does the arithmetic hold up, is this the second time this invoice appears,
and does the claim fit what the firm allows? This project automates that
checking for one narrow slice — invoice reimbursement — while keeping a
human in charge of every borderline case.

## Who it is for

- **Recruiters and reviewers:** a small, fully tested example of an
  auditable finance workflow, with every enforcement claim backed by a
  named test.
- **Builders:** a starting point for a governed claims pipeline — typed
  extraction, money checks, rule citations, retrieval-grounded decisions,
  and gated approvals, all in standard-library Python.
- **Finance operations (as a concept demo):** the shape of a system where
  no payment decision is made without a cited rule and a retrievable
  passage behind it.

## What it deliberately is not

- Not a payment system: nothing here moves money.
- Not a production claims product: no real invoices, no real policy, no
  OCR, no live model calls.
- Not affiliated with any real firm, university, or training provider.
