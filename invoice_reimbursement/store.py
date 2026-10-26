"""View-aware SQLite store.

Writes go through an internal writer connection. Every read goes through a
reader connection guarded by a strict authorizer:

* SQLITE_SELECT is allowed.
* SQLITE_READ is allowed ONLY when the authorizer's source argument names
  one of the allowed views (v_invoices, v_decisions, v_approvals). A direct
  read of a base table has source None and is denied; so is any read of
  sqlite_master.
* Everything else — INSERT/UPDATE/DELETE through the reader, PRAGMA,
  ATTACH, functions such as load_extension — is denied.

The public views expose decision fields only; raw invoice tables are never
readable through the reader. By default the store lives in a temporary file
so writer and reader connections see the same database without sharing
state between Store instances.
"""

from __future__ import annotations

import sqlite3
import tempfile

ALLOWED_VIEWS = frozenset({"v_invoices", "v_decisions", "v_approvals"})
MAX_ROWS = 100

_SCHEMA = """
    CREATE TABLE IF NOT EXISTS invoices_raw (
        claim_id TEXT PRIMARY KEY, vendor TEXT, invoice_number TEXT,
        category TEXT, total_cents INTEGER, raw_text TEXT);
    CREATE TABLE IF NOT EXISTS decisions_raw (
        claim_id TEXT PRIMARY KEY, outcome TEXT, payable_cents INTEGER,
        citations TEXT, reasons TEXT);
    CREATE TABLE IF NOT EXISTS approvals_raw (
        claim_id TEXT PRIMARY KEY, approver TEXT, expires_at TEXT);
    CREATE VIEW IF NOT EXISTS v_invoices AS
        SELECT claim_id, vendor, invoice_number, category, total_cents
        FROM invoices_raw;
    CREATE VIEW IF NOT EXISTS v_decisions AS
        SELECT claim_id, outcome, payable_cents, citations, reasons
        FROM decisions_raw;
    CREATE VIEW IF NOT EXISTS v_approvals AS
        SELECT claim_id, approver, expires_at FROM approvals_raw;
"""


class RowCapExceeded(Exception):
    pass


def _authorizer(action, param1, param2, db_name, source):
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        # Base-table columns are authorised with source = the view used to
        # reach them; SQLite additionally authorises the view's own columns
        # with source None and param1 = the view name. Both are view reads.
        # A direct base-table read has param1 = the base table and
        # source = None, and is denied.
        if source in ALLOWED_VIEWS or param1 in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_DENY


class Store:
    def __init__(self, path: str | None = None):
        if path is None:
            handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            path = handle.name
            handle.close()
        self._path = path
        self._writer = sqlite3.connect(path)
        self._writer.executescript(_SCHEMA)
        self._writer.commit()
        self._reader = sqlite3.connect(path)
        self._reader.set_authorizer(_authorizer)

    # -- writes (internal only) -------------------------------------------
    def record_invoice(self, claim_id, vendor, invoice_number, category,
                       total_cents, raw_text=""):
        self._writer.execute(
            "INSERT OR REPLACE INTO invoices_raw VALUES (?,?,?,?,?,?)",
            (claim_id, vendor, invoice_number, category, total_cents, raw_text))
        self._writer.commit()

    def record_decision(self, claim_id, outcome, payable_cents, citations, reasons):
        self._writer.execute(
            "INSERT OR REPLACE INTO decisions_raw VALUES (?,?,?,?,?)",
            (claim_id, outcome, payable_cents, ",".join(citations),
             "; ".join(reasons)))
        self._writer.commit()

    def record_approval(self, claim_id, approver, expires_at):
        self._writer.execute(
            "INSERT OR REPLACE INTO approvals_raw VALUES (?,?,?)",
            (claim_id, approver, expires_at))
        self._writer.commit()

    # -- reads (authorizer-guarded, row-capped) ------------------------------
    def _fetch_capped(self, sql: str, max_rows: int = MAX_ROWS):
        cursor = self._reader.execute(sql)
        rows = cursor.fetchmany(max_rows + 1)
        if len(rows) > max_rows:
            raise RowCapExceeded(
                f"result exceeds row cap of {max_rows}; refine the query")
        return rows

    def list_decisions(self, max_rows: int = MAX_ROWS):
        return self._fetch_capped(
            "SELECT claim_id, outcome, payable_cents FROM v_decisions",
            max_rows=max_rows)

    def list_invoices(self, max_rows: int = MAX_ROWS):
        return self._fetch_capped(
            "SELECT claim_id, vendor, invoice_number, category, total_cents "
            "FROM v_invoices", max_rows=max_rows)

    def list_approvals(self, max_rows: int = MAX_ROWS):
        return self._fetch_capped(
            "SELECT claim_id, approver, expires_at FROM v_approvals",
            max_rows=max_rows)

    def raw_reader(self):
        """Expose the guarded reader connection for authorizer tests."""
        return self._reader
