# Interview points

- **Why retrieval at all?** A bare rule match can cite a rule id, but a
  reviewer cannot check it without the passage. Retrieval makes the
  decision checkable by a person who was not in the room — that is what
  "auditable" means here, and the test `test_rag_retrieves_governing_passage`
  pins the governing passage to the top for a meals claim.
- **Why Decimal, not float?** Money equality checks must be exact to the
  cent. Float rounding would turn a correct invoice into a review item
  (or worse, pass a wrong one). Every money test uses values where float
  drift would be visible.
- **Why is the authorizer strict instead of just hiding tables?** Hiding
  is a convention; the authorizer is enforcement at the database layer.
  The tests prove it by issuing the forbidden queries and watching them
  fail — including the subtle case where SQLite authorises a view's own
  columns with no source, which the first implementation missed.
- **Why treat "yes, wait, no" as a rejection?** Consent that contradicts
  itself is not consent. The gate treats any yes mixed with rejection or
  hesitation wording as a rejection, and a missing or vague reply as
  absent — never as approval.
- **Why a row cap at fetch time?** A reporting query over a growing audit
  table must not be able to pull the whole table into memory by accident.
  `fetchmany(MAX+1)` bounds the fetch and raises instead of truncating
  silently, so a caller that expected 100 rows learns there were more.
- **Why hash the brand blocklist?** The blocklist guards names the repo
  must not present as its own; storing them in plain text would put those
  names in the repo anyway. Hashes let the check work without the leak.
- **What would you change first in production?** Persistent approval
  routing, a real OCR/PDF ingest step, and calibrated confidence — in
  that order. The limitations doc says why each is still missing.
