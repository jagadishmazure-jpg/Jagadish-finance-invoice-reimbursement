# Guardrails and security controls

Every claim below is proven by a named test. If a test is removed, the
claim goes with it.

## SQLite authorizer (strict, view-aware)

- View reads allowed: `test_view_read_allowed`,
  `test_view_invoice_read_allowed`.
- Base-table reads denied: `test_base_table_read_denied`,
  `test_decisions_base_table_read_denied`.
- `sqlite_master` read denied: `test_sqlite_master_read_denied`.
- Writes through the reader denied: `test_write_through_reader_denied`,
  `test_update_through_reader_denied`, `test_delete_through_reader_denied`.
- PRAGMA denied: `test_pragma_through_reader_denied`.
- ATTACH denied: `test_attach_through_reader_denied`.

## Human-review gate

- Explicit yes approves: `test_gate_explicit_yes_approves`.
- Bypass raises: `test_gate_bypass_raises`,
  `test_gate_approve_without_request_raises`.
- Reject paths: `test_gate_reject_path`, `test_gate_reject_word_path`.
- Absent paths: `test_gate_absent_consent_none`,
  `test_gate_absent_consent_empty`, `test_gate_absent_consent_vague`.
- Low confidence blocked: `test_gate_low_confidence_yes_not_approved`.
- Self-contradicting consent blocked: `test_gate_contradicting_consent_yes_wait_no`,
  `test_gate_contradicting_consent_yes_then_no`,
  `test_gate_hedged_yes_not_approved`.

## Approvals: named-person, single-use, scoped, expiring

`test_approval_named_person_required`, `test_approval_single_use`,
`test_approval_scoped_to_claim`, `test_approval_scoped_to_amount`,
`test_approval_expired`, `test_approval_negative_scope_rejected`.

## PII redaction (cards and emails included)

`test_redact_card_number`, `test_redact_card_number_dashes`,
`test_redact_email_address`, `test_redact_phone_and_ssn`,
`test_extraction_drops_bank_field`,
`test_validation_error_never_contains_card`.

## Row cap, budgets, brands, notifications

- Row cap via `fetchmany(MAX+1)`, no LIMIT rewriting, no fetchall:
  `test_row_cap_enforced_via_fetchmany`,
  `test_row_cap_exact_boundary_passes`.
- Negative costs rejected, not clamped: `test_negative_cost_rejected`,
  `test_negative_amount_rejected_not_clamped`.
- Non-empty hashed brand blocklist: `test_brand_blocklist_non_empty`,
  `test_brand_check_flags_blocked_name`, `test_brand_check_passes_clean_text`.
- Notifications dry-run by default, explicit opt-in, refused in CI:
  `test_notify_dry_run_by_default`, `test_notify_requires_explicit_opt_in`,
  `test_notify_refused_in_ci`, `test_notify_redacts_body`.

## Money and duplicates

`test_money_line_sum_mismatch_fails`, `test_money_total_mismatch_fails`,
`test_money_tax_arithmetic_fails`,
`test_money_line_quantity_price_mismatch_fails`,
`test_duplicate_invoice_detected`,
`test_duplicate_case_insensitive_invoice_number`.
