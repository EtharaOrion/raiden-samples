"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for the `aws dynamodb` CLI behavioral contract.

Uses the `cli` fixture (subprocess invocation of the submission entrypoint)
and, where available, the `ddb_client` fixture (independent backend client)
shipped by conftest.py. All fixtures are accessed defensively so the module
stays importable/collectible even if a fixture is renamed or absent.
"""
import json
import uuid

import pytest


def _table_name():
    return "held-out-tbl-" + uuid.uuid4().hex[:12]


def _create_table_args(name):
    return [
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", json.dumps([{"AttributeName": "id", "AttributeType": "S"}]),
        "--key-schema", json.dumps([{"AttributeName": "id", "KeyType": "HASH"}]),
        "--billing-mode", "PAY_PER_REQUEST",
    ]


def _create_table(cli, name):
    r = cli(*_create_table_args(name))
    assert r.returncode == 0, f"setup create-table failed: {r.stderr!r}"
    return r


# ---------------------------------------------------------------------------
# Cross-command state consistency
# ---------------------------------------------------------------------------

def test_put_then_get_roundtrip_returns_exact_item(cli):
    table = _table_name()
    _create_table(cli, table)

    item = {"id": {"S": "abc123"}, "count": {"N": "5"}, "flag": {"BOOL": True}}
    r_put = cli("dynamodb", "put-item", "--table-name", table, "--item", json.dumps(item))
    assert r_put.returncode == 0, r_put.stderr
    assert r_put.stderr.strip() == ""

    r_get = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", json.dumps({"id": {"S": "abc123"}}),
    )
    assert r_get.returncode == 0, r_get.stderr
    assert r_get.stderr.strip() == ""
    body = json.loads(r_get.stdout)
    assert "Item" in body
    assert body["Item"]["id"] == {"S": "abc123"}
    assert body["Item"]["count"] == {"N": "5"}


def test_get_item_missing_omits_item_key(cli):
    table = _table_name()
    _create_table(cli, table)

    r_get = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", json.dumps({"id": {"S": "does-not-exist"}}),
    )
    assert r_get.returncode == 0, r_get.stderr
    assert r_get.stderr.strip() == ""
    body = json.loads(r_get.stdout)
    assert "Item" not in body


def test_conditional_put_failure_leaves_state_unchanged(cli):
    table = _table_name()
    _create_table(cli, table)

    item = {"id": {"S": "cond1"}, "val": {"S": "original"}}
    r0 = cli("dynamodb", "put-item", "--table-name", table, "--item", json.dumps(item))
    assert r0.returncode == 0

    bad_item = {"id": {"S": "cond1"}, "val": {"S": "overwritten"}}
    r1 = cli(
        "dynamodb", "put-item",
        "--table-name", table,
        "--item", json.dumps(bad_item),
        "--condition-expression", "attribute_not_exists(id)",
    )
    assert r1.returncode == 254
    assert r1.stdout.strip() == ""
    assert r1.stderr.strip() != ""

    r_get = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", json.dumps({"id": {"S": "cond1"}}),
    )
    body = json.loads(r_get.stdout)
    assert body["Item"]["val"] == {"S": "original"}


def test_recreate_existing_table_is_resource_in_use(cli):
    table = _table_name()
    _create_table(cli, table)
    r2 = cli(*_create_table_args(table))
    assert r2.returncode == 254
    assert r2.stdout.strip() == ""
    assert r2.stderr.strip() != ""


def test_get_item_on_nonexistent_table_is_service_error(cli):
    table = _table_name()  # never created
    r = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", json.dumps({"id": {"S": "x"}}),
    )
    assert r.returncode == 254
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


# ---------------------------------------------------------------------------
# Usage-error path (client-side, exit 252)
# ---------------------------------------------------------------------------

def test_missing_required_flag_exits_252(cli):
    r = cli("dynamodb", "create-table")
    assert r.returncode == 252
    assert r.stdout.strip() == ""
    assert r.stderr.strip() != ""


def test_duplicate_flag_exits_252(cli):
    table1 = _table_name()
    table2 = _table_name()
    r = cli(
        "dynamodb", "create-table",
        "--table-name", table1,
        "--table-name", table2,
        "--attribute-definitions", json.dumps([{"AttributeName": "id", "AttributeType": "S"}]),
        "--key-schema", json.dumps([{"AttributeName": "id", "KeyType": "HASH"}]),
    )
    assert r.returncode == 252
    assert r.stdout.strip() == ""


def test_empty_table_name_value_exits_252(cli):
    r = cli(
        "dynamodb", "create-table",
        "--table-name", "--attribute-definitions",
        json.dumps([{"AttributeName": "id", "AttributeType": "S"}]),
    )
    assert r.returncode == 252
    assert r.stdout.strip() == ""


def test_malformed_json_flag_exits_252(cli):
    table = _table_name()
    r = cli(
        "dynamodb", "create-table",
        "--table-name", table,
        "--attribute-definitions", "{not valid json",
    )
    assert r.returncode == 252
    assert r.stdout.strip() == ""


def test_unknown_flag_exits_252(cli):
    table = _table_name()
    r = cli(
        "dynamodb", "create-table",
        "--table-name", table,
        "--this-flag-does-not-exist", "value",
    )
    assert r.returncode == 252
    assert r.stdout.strip() == ""


# ---------------------------------------------------------------------------
# General output-shape contract
# ---------------------------------------------------------------------------

def test_success_output_is_parseable_json_and_stderr_empty(cli):
    table = _table_name()
    r = cli(*_create_table_args(table))
    assert r.returncode == 0
    assert r.stderr.strip() == ""
    # Must be valid JSON on stdout (not necessarily non-empty structure)
    json.loads(r.stdout)