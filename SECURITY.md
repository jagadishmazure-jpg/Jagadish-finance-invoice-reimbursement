# Security policy

This is a synthetic-data portfolio project. It must never be pointed at real
employee invoices, real bank details, or a production payment system.

- No credentials are accepted, stored, or read anywhere in this repo.
- The notification channel is dry-run by default and refuses to send in CI.
- Banking details, card numbers, and email addresses are redacted from every
  log string and error message; extraction drops bank/card fields outright.
- Database reads go through a view-only authorizer (see docs/guardrails.md).
- To report a security issue, open a private issue in the repo; do not paste
  real personal or financial data into any report.
