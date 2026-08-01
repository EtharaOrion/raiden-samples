"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""Held-out tests for the `aws dynamodb` CLI emulator.

These tests exercise argv dispatch, flag-parsing error paths, exit-code
contract, output shape, and cross-invocation state consistency against the
live DynamoDB Local backend wired up by the shipped conftest.py fixtures.
"""

import json

import pytest


def _assert_usage_error(result):
    assert result.returncode == 252, (
        f"expected usage error exit 252, got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout == "", f"stdout should be empty on error, got {result.stdout!r}"
    assert result.stderr.strip() != "", "expected a one-line stderr message"
    assert "Traceback" not in result.stderr


def _assert_service_error(result):
    assert result.returncode in (254,), (
        f"expected modeled service error exit 254, got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout == ""
    assert result.stderr.strip() != ""
    assert "Traceback" not in result.stderr


def _assert_success(result):
    assert result.returncode == 0, (
        f"expected success exit 0, got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stderr == "", f"stderr should be empty on success, got {result.stderr!r}"
    assert result.stdout.strip() != ""
    return json.loads(result.stdout)


def _try_create_table(ddb_client, table_name):
    """Best-effort table creation using whatever API the shipped backend
    client exposes. Skips the calling test if no compatible method/signature
    is available, since create-table is intentionally not part of the CLI
    surface under test.
    """
    attempts = [
        dict(
            table_name=table_name,
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
            billing_mode="PAY_PER_REQUEST",
        ),
        dict(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        ),
    ]
    fn = getattr(ddb_client, "create_table", None)
    if fn is None:
        pytest.skip("backend client has no create_table helper")
    for kwargs in attempts:
        try:
            fn(**kwargs)
            return
        except TypeError:
            continue
        except Exception:
            continue
    pytest.skip("could not create table via available backend client API")


# ---------------------------------------------------------------------------
# argv dispatch / usage-error paths
# ---------------------------------------------------------------------------

def test_unknown_subcommand_is_usage_error(cli):
    result = cli("dynamodb", "not-a-real-subcommand", "--table-name", "t")
    _assert_usage_error(result)


def test_missing_required_table_name_is_usage_error(cli):
    result = cli("dynamodb", "get-item", "--key", '{"id":{"S":"x"}}')
    _assert_usage_error(result)


def test_duplicate_flag_is_usage_error(cli):
    result = cli(
        "dynamodb", "delete-table",
        "--table-name", "some_table_abc",
        "--table-name", "other_table_def",
    )
    _assert_usage_error(result)


def test_unknown_flag_rejected_even_with_valid_json(cli):
    result = cli(
        "dynamodb", "delete-table",
        "--table-name", "some_table_xyz",
        "--attribute-definitions", "{}",
    )
    _assert_usage_error(result)


def test_oversized_flag_value_is_usage_error(cli):
    huge = "t" * 600
    result = cli("dynamodb", "delete-table", "--table-name", huge)
    _assert_usage_error(result)


def test_malformed_json_key_flag_is_usage_error(cli):
    result = cli(
        "dynamodb", "get-item",
        "--table-name", "some_table_qqq",
        "--key", "{not valid json",
    )
    _assert_usage_error(result)


# ---------------------------------------------------------------------------
# modeled service errors (254)
# ---------------------------------------------------------------------------

def test_delete_nonexistent_table_is_service_error(cli):
    result = cli("dynamodb", "delete-table", "--table-name", "definitely_absent_table_1")
    _assert_service_error(result)


def test_get_item_on_missing_table_is_service_error(cli):
    result = cli(
        "dynamodb", "get-item",
        "--table-name", "definitely_absent_table_2",
        "--key", '{"id":{"S":"x"}}',
    )
    _assert_service_error(result)


# ---------------------------------------------------------------------------
# success-path output shape / state consistency
# ---------------------------------------------------------------------------

def test_list_tables_shape_when_empty(cli):
    result = cli("dynamodb", "list-tables")
    body = _assert_success(result)
    assert isinstance(body, dict)
    names = body.get("TableNames", [])
    assert isinstance(names, list)
    assert names == []


def test_get_item_absent_key_omits_item_member(cli, ddb_client):
    table = "held_out_absent_key_table"
    _try_create_table(ddb_client, table)
    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"id":{"S":"does-not-exist"}}',
    )
    body = _assert_success(result)
    assert "Item" not in body


def test_update_then_get_item_reflects_write_and_delete_removes_table(cli, ddb_client):
    table = "held_out_update_get_table"
    _try_create_table(ddb_client, table)

    upd = cli(
        "dynamodb", "update-item",
        "--table-name", table,
        "--key", '{"id":{"S":"row1"}}',
        "--update-expression", "SET #v = :val",
        "--expression-attribute-names", '{"#v":"value"}',
        "--expression-attribute-values", '{":val":{"S":"hello"}}',
    )
    _assert_success(upd)

    got = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"id":{"S":"row1"}}',
    )
    body = _assert_success(got)
    assert body.get("Item", {}).get("value", {}).get("S") == "hello"

    delr = cli("dynamodb", "delete-table", "--table-name", table)
    _assert_success(delr)

    listing = cli("dynamodb", "list-tables")
    listing_body = _assert_success(listing)
    assert table not in listing_body.get("TableNames", [])


def test_conditional_check_failure_does_not_mutate_state(cli, ddb_client):
    table = "held_out_conditional_table"
    _try_create_table(ddb_client, table)

    # Establish baseline value.
    base = cli(
        "dynamodb", "update-item",
        "--table-name", table,
        "--key", '{"id":{"S":"row2"}}',
        "--update-expression", "SET #v = :val",
        "--expression-attribute-names", '{"#v":"value"}',
        "--expression-attribute-values", '{":val":{"S":"original"}}',
    )
    _assert_success(base)

    failing = cli(
        "dynamodb", "update-item",
        "--table-name", table,
        "--key", '{"id":{"S":"row2"}}',
        "--update-expression", "SET #v = :val",
        "--condition-expression", "#v = :nope",
        "--expression-attribute-names", '{"#v":"value"}',
        "--expression-attribute-values",
        '{":val":{"S":"changed"},":nope":{"S":"not-the-real-value"}}',
    )
    assert failing.returncode == 254
    assert failing.stdout == ""

    after = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"id":{"S":"row2"}}',
    )
    body = _assert_success(after)
    assert body.get("Item", {}).get("value", {}).get("S") == "original"