"""Authorizer proofs. These tests exercise real queries through the guarded
reader connection; they do not inspect SQL text or rely on any text check."""

import sqlite3

import pytest

from invoice_reimbursement.store import Store


@pytest.fixture
def store():
    s = Store()
    s.record_invoice("CLM-1", "Harbor Office Supply", "INV-1", "office", 7020)
    s.record_decision("CLM-1", "APPROVED", 7020, ["POL-OFFICE-01"], [])
    return s


def test_view_read_allowed(store):
    rows = store.list_decisions()
    assert rows == [("CLM-1", "APPROVED", 7020)]


def test_view_invoice_read_allowed(store):
    rows = store.list_invoices()
    assert rows[0][1] == "Harbor Office Supply"


def test_base_table_read_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute("SELECT * FROM invoices_raw").fetchall()


def test_decisions_base_table_read_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute("SELECT * FROM decisions_raw").fetchall()


def test_sqlite_master_read_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute(
            "SELECT name FROM sqlite_master").fetchall()


def test_write_through_reader_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute(
            "INSERT INTO decisions_raw VALUES ('X','APPROVED',1,'','')")


def test_update_through_reader_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute(
            "UPDATE decisions_raw SET outcome='REJECTED' WHERE claim_id='CLM-1'")


def test_delete_through_reader_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute("DELETE FROM decisions_raw")


def test_pragma_through_reader_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute("PRAGMA table_info(v_decisions)").fetchall()


def test_attach_through_reader_denied(store):
    with pytest.raises(sqlite3.DatabaseError):
        store.raw_reader().execute("ATTACH ':memory:' AS other")
