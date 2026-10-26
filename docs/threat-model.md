# Threat model

## STRIDE sketch

| Threat | Where it bites | Mitigation in this repo |
| --- | --- | --- |
| Spoofing | A caller claims a reviewer's approval | Approvals name a person and are single-use, scoped, expiring; the gate requires a pending request |
| Tampering | Editing a recorded decision | Reader connection denies all writes; raw tables are not readable through it |
| Repudiation | "Nobody approved that" | Decisions record citations, retrieved passages, and reasons; approvals record approver + expiry |
| Information disclosure | Banking details in logs/errors | Redaction of cards, emails, phones, SSNs; sensitive fields dropped at extraction; tests prove errors stay clean |
| Denial of service | A query pulls the whole audit table | Row cap via fetchmany(MAX+1), raising on overflow |
| Elevation of privilege | Self-approving a claim | Gate bypass raises; approvals cannot be minted without a name, scope, and expiry |

## LLM-related risks (OWASP LLM Top 10, as applicable)

- **Prompt injection:** there is no hosted model call in this scaffold,
  so injected invoice text cannot steer a model. If a model is added
  later, invoice text must be treated as untrusted data, never as
  instruction, and the extraction output must still pass the Decimal
  money checks before any decision.
- **Sensitive information disclosure:** covered by redaction + the
  view-only store (see above).
- **Excessive agency:** the pipeline cannot pay anything and cannot
  approve its own doubtful claims; the gate is the only approval path
  and it demands an explicit human yes.
- **Overreliance:** confidence is a routing heuristic, not a calibrated
  probability; low-confidence claims are forced to review by design.

## Out of scope for this scaffold

Real authentication, real payment rails, real employee data, and any
network-facing service — none exist here, so none are modelled.
