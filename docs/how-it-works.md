# How it works, step by step

1. **Ingest.** `parse_invoice()` reads a plain-text record line by line.
   `LINE:` rows become typed `LineItem`s; `SUBTOTAL`, `TAX`, `TAX_RATE`,
   and `TOTAL` become `Decimal`s. Any `BANK`, `CARD`, or `ACCOUNT` line is
   dropped and noted, never stored.
2. **Score confidence.** Confidence starts at 1.0 and loses 0.15 per
   missing essential field and 0.25 per unparsable or sensitive line, so a
   shaky record is visible before any decision is made.
3. **Check the money.** `check_money()` verifies four things in cents:
   lines sum to subtotal; subtotal + tax equals total; tax equals
   subtotal × rate; each line equals quantity × unit price.
4. **Check for duplicates.** The registry keys on vendor + invoice number
   + total (invoice number matched case-insensitively). A repeat is a
   rejection, not a review item.
5. **Match policy.** `match_policy()` returns every rule that applies to
   the category plus any cap or threshold breach, as citable rule ids.
6. **Retrieve.** The retriever scores rulebook passages by shared terms
   with the claim (with a bonus for the claim's category) and returns the
   top three, so the decision record names the passages behind it.
7. **Decide.** Clean claims are `APPROVED` for the full total. Money
   failures, policy breaches, low confidence, or amounts above $1000 yield
   `NEEDS_REVIEW` and a pending gate request. Duplicates are `REJECTED`.
8. **Review.** A reviewer answers the gate. Only a plain "yes" at
   confidence ≥ 0.6 approves. "No", a missing reply, a vague reply, a
   low-confidence yes, or a self-contradicting reply ("yes, wait, no")
   leaves the claim unapproved. Large claims additionally need a
   named-person approval that is single-use, scoped, and expiring.
9. **Record.** Decisions land in SQLite, readable only through the
   public views, capped at 100 rows per fetch.
