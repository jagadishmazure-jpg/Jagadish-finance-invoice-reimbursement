# Limitations and known failures

Kept visible on purpose; each item is either a test or an explicit gap.

- **Plain-text records only.** There is no PDF or image parsing. A scanned
  invoice cannot be ingested; that is planned work, not a hidden gap.
- **Keyword retrieval, not semantic search.** The retriever matches
  shared terms. A passage phrased with none of the claim's words will not
  be retrieved, even if it is topically relevant. Test
  `test_rag_returns_empty_for_unrelated_query` pins the empty-result
  behaviour; there is no test claiming semantic recall, because the
  retriever does not have it.
- **Single currency, single tax rate per invoice.** Multi-currency totals
  and mixed-rate invoices are out of scope; the money checks would flag
  them as mismatches rather than handle them.
- **Duplicate key is narrow.** Only vendor + invoice number + total is
  compared. Two genuinely different invoices that share those three
  fields would be treated as one duplicate — a false rejection, kept as a
  known failure mode rather than silently widened.
- **No real approval workflow.** Approvals are in-process objects, not
  routed to a person through any channel; the notification module records
  but never sends.
- **Small synthetic test set.** The 64 tests are regression checks over
  hand-written cases, not a quality claim about real-world accuracy. No
  accuracy, precision, or recall figure is claimed anywhere in this repo.
- **Confidence is heuristic.** The 0.15/0.25 penalties are chosen
  constants, not calibrated probabilities; treat the score as a routing
  signal, not a probability.
