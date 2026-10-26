# Related repos

Cross-links, not duplication: each neighbouring project covers one slice
that this repo touches but does not own.

- **Jagadish-document-intelligence** — generic document extraction and
  posting. This repo's extractor is deliberately narrower: invoice-shaped
  records only, with money checks attached. For general document types,
  start there.
- **Jagadish-finance-data-validation** (sibling finance build) — data
  quality checks over finance datasets. Its validation scope is broader
  than invoices; this repo's money checks are invoice-specific.
- **Jagadish-finance-compliance-rag** (sibling finance build) — retrieval
  over compliance material. This repo's retriever is scoped to one small
  rulebook; for a general compliance corpus, use that project.
- **Jagadish-fraud-detection-agents** — fraud patterns including duplicate
  and anomalous claims. This repo rejects exact duplicates only; fraud
  judgement (rings, anomalies, triage narratives) belongs there.
- **Jagadish-pii-guard** — PII detection and redaction as a standalone
  capability. This repo's redactor is a small, invoice-focused subset
  (cards, emails, phones, SSNs, bank hints).

If a future change needs a capability listed above, extend the owning
repo and link it here rather than copying its code into this one.
