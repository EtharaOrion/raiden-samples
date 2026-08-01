"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out behavioral tests for the emulated `aws dynamodb` CLI subset
(create-table, delete-item, delete-table, put-item).

These tests exercise:
  - success output contract (stdout JSON-only, stderr empty, exit 0)
  - usage-error path (exit 252): duplicate flags, unknown flags, missing
    required flags, empty flag values
  - service-error path (exit 254-ish, i.e. nonzero): bare create-table
    (no attribute-definitions/key-schema), duplicate table creation,
    operating on a non-existent table
  - idempotency of delete-item on a missing key
  - cross-invocation state consistency against the real backend via the
    ddb_client fixture (each `cli()` call is a fresh subprocess, so any
    state visible must have gone through the real endpoint)
  - numeric AttributeValue strings are preserved verbatim
"""
import json
import uuid

import pytest


def _table_name():
    return "t_" + uuid.uuid4().hex[:20]


def _create_table(cli, name):
    return cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )


def test_create_table_success_output_contract(cli):
    name = _table_name()
    result = _create_table(cli, name)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    # stdout must be pure, parseable JSON
    body = json.loads(result.stdout)
    assert isinstance(body, dict)


def test_create_table_duplicate_flag_is_usage_error(cli):
    name = _table_name()
    result = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--table-name", "other-name",
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
    )
    assert result.returncode == 252
    assert result.stdout == ""
    assert result.stderr.strip() != ""
    assert "Traceback" not in result.stderr


def test_unknown_flag_is_usage_error(cli):
    name = _table_name()
    result = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--not-a-real-flag", "xyz",
    )
    assert result.returncode == 252
    assert result.stdout == ""
    assert "Traceback" not in result.stderr


def test_put_item_missing_item_flag_is_usage_error(cli):
    name = _table_name()
    create = _create_table(cli, name)
    assert create.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", name)
    assert result.returncode == 252
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_delete_item_missing_key_flag_is_usage_error(cli):
    name = _table_name()
    result = cli("dynamodb", "delete-item", "--table-name", name)
    assert result.returncode == 252
    assert result.stdout == ""


def test_empty_flag_value_is_usage_error(cli):
    # value for --table-name is missing (next token is another flag)
    result = cli(
        "dynamodb", "create-table",
        "--table-name", "--attribute-definitions",
        "AttributeName=id,AttributeType=S",
    )
    assert result.returncode == 252
    assert result.stdout == ""


def test_create_table_bare_name_is_service_error_not_usage_error(cli):
    # per spec: omitting attribute-definitions/key-schema must NOT be
    # rejected client-side (252); it is forwarded to the service which
    # rejects it (nonzero, non-252-per-spec's natural mapping is 254,
    # but we only assert it's a *service* rejection, i.e. != 252, and
    # generally nonzero).
    name = _table_name()
    result = cli("dynamodb", "create-table", "--table-name", name)
    assert result.returncode != 0
    assert result.returncode != 252
    assert result.stdout == ""
    assert "Traceback" not in result.stderr


def test_recreate_existing_table_fails_without_traceback(cli):
    name = _table_name()
    first = _create_table(cli, name)
    assert first.returncode == 0, first.stderr

    second = _create_table(cli, name)
    assert second.returncode != 0
    assert second.stdout == ""
    assert second.stderr.strip() != ""
    assert "Traceback" not in second.stderr


def test_put_item_on_missing_table_is_service_error(cli):
    name = _table_name()  # never created
    item = json.dumps({"id": {"S": "abc"}})
    result = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", item,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "Traceback" not in result.stderr


def test_delete_item_on_nonexistent_key_is_idempotent(cli):
    name = _table_name()
    create = _create_table(cli, name)
    assert create.returncode == 0

    key = json.dumps({"id": {"S": "does-not-exist"}})
    result = cli("dynamodb", "delete-item", "--table-name", name, "--key", key)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    json.loads(result.stdout)  # must still be valid JSON


def test_put_item_state_consistency_and_numeric_preservation(cli, ddb_client):
    if ddb_client is None:
        pytest.skip("ddb_client fixture unavailable")
    name = _table_name()
    create = _create_table(cli, name)
    assert create.returncode == 0, create.stderr

    item = {"id": {"S": "row-1"}, "count": {"N": "5"}}
    put = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps(item),
    )
    assert put.returncode == 0, put.stderr

    # Verify through the real backend directly (independent of the CLI),
    # since each `cli()` invocation is a fresh subprocess with no shared
    # in-memory state.
    get_item = getattr(ddb_client, "get_item", None)
    if get_item is None:
        pytest.skip("ddb_client has no get_item helper")
    stored = get_item(name, {"id": {"S": "row-1"}})
    assert stored is not None
    stored_item = stored.get("Item", stored)
    assert stored_item["id"] == {"S": "row-1"}
    assert stored_item["count"] == {"N": "5"}

    # now delete and confirm it's gone
    delete = cli(
        "dynamodb", "delete-item",
        "--table-name", name,
        "--key", json.dumps({"id": {"S": "row-1"}}),
    )
    assert delete.returncode == 0, delete.stderr

    stored_after = get_item(name, {"id": {"S": "row-1"}})
    stored_after_item = (stored_after or {}).get("Item") if stored_after else None
    assert not stored_after_item


def test_delete_table_removes_from_backend(cli, ddb_client):
    if ddb_client is None:
        pytest.skip("ddb_client fixture unavailable")
    name = _table_name()
    create = _create_table(cli, name)
    assert create.returncode == 0, create.stderr

    delete = cli("dynamodb", "delete-table", "--table-name", name)
    assert delete.returncode == 0, delete.stderr
    assert delete.stderr == ""
    json.loads(delete.stdout)

    list_tables = getattr(ddb_client, "list_tables", None)
    if list_tables is None:
        pytest.skip("ddb_client has no list_tables helper")
    tables = list_tables()
    names = tables.get("TableNames", tables) if isinstance(tables, dict) else tables
    assert name not in names