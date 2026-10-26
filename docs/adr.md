# Architecture decision records

## ADR-1: Standard library only

**Decision:** No third-party dependencies, including for the retriever
and the store.
**Why:** The whole pipeline must run offline with one command, and the
portfolio value is in the design, not in framework choice.
**Consequence:** Keyword retrieval instead of embeddings; SQLite instead
of a server database. Both are swappable behind stable interfaces.

## ADR-2: Decimal money, integer cents at the boundary

**Decision:** Parse money as Decimal; convert to integer cents for
decisions and storage.
**Why:** Cent-exact equality is the core correctness property of the
money checks.
**Consequence:** No float anywhere in the money path; tests use values
that would expose float drift.

## ADR-3: Retrieval over a prose rulebook, not just coded rules

**Decision:** Keep the rulebook as prose (`data/policy_rulebook.md`) and
retrieve passages for each decision, alongside coded cap enforcement.
**Why:** A coded rule can be cited but not read back by a reviewer; the
passage is the auditable artefact.
**Consequence:** Prose and code can drift — adopters must test that they
agree (see the implementation guide).

## ADR-4: View-only authorizer, not application-level hiding

**Decision:** Enforce read restrictions in SQLite's authorizer.
**Why:** Application code can forget a check; the authorizer cannot be
bypassed by a new query path that reuses the reader connection.
**Consequence:** Two connections (writer, guarded reader); schema work
must happen before the authorizer is set.

## ADR-5: Strict consent semantics in the review gate

**Decision:** Only a plain "yes" at confidence ≥ 0.6 approves.
**Why:** Ambiguous, missing, hedged, or self-contradicting replies are
the realistic failure modes of human-in-the-loop approval, and the safe
default for all of them is "not approved".
**Consequence:** Reviewers must answer plainly; the gate never guesses.

## ADR-6: Dry-run notifications with no transport

**Decision:** Ship no email transport at all.
**Why:** A half-wired sender that "usually" works is worse than an honest
stub: it invites credential handling in a portfolio repo.
**Consequence:** Adopters add a transport behind the existing opt-in and
CI-refusal guards.
