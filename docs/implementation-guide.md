# Implementation guide (for adopters)

## Adapting the rulebook

1. Edit `data/policy_rulebook.md`: one `## RULE-ID` block per rule, in
   plain language. The retriever reads this file; no code change is needed
   for wording changes.
2. Mirror any cap change in `policy.py` (`RULES` and
   `APPROVAL_THRESHOLD_CENTS`), because caps are enforced numerically
   there, not parsed from prose. A rule whose prose and code disagree is a
   bug — add a test that asserts they agree before shipping.
3. Keep rule ids stable: decisions already recorded cite them.

## Adapting the record format

`extraction.py` is the only place that knows the line format. Add a new
field by adding a `KEY:` branch and a confidence penalty for its absence;
add a money rule in `validation.py` the same day, with a failing-first
test (a passing check with no test is not a check).

## Wiring a real review queue

Replace `ReviewGate`'s in-process pending map with a persistent queue,
but keep the consent semantics exactly: explicit "yes" at adequate
confidence approves; everything else does not. Reuse the gate tests as
the contract — port them, don't drop them.

## Wiring a real notification

`notify.py` deliberately has no transport. When adding one, keep
`dry_run=True` as the default, keep the CI refusal, and keep redacting
every body before it leaves the process. Never pass credentials through
this module; use the deploy environment's secret store.

## What not to change casually

- The authorizer's allow-list: widening it to a base table defeats the
  audit store's purpose. Add a view instead.
- The row-cap mechanism: `fetchmany(MAX+1)` is the cap. Do not replace it
  with LIMIT rewriting or fetchall.
- The consent rules: "yes, wait, no" must stay a rejection.
