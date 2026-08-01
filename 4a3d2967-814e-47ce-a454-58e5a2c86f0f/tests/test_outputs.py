"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out tests for the `aws dynamodb query|scan` CLI stand-in.

These tests exercise the documented CLI contract (argv dispatch, flag
validation, exit codes, stdout/stderr separation, and cross-invocation
state consistency against the DynamoDB Local backend) without assuming
any particular internal implementation.
"""

import json

import pytest


def _mk_table(ddb_client, name):
    """Create a minimal single-key table via the backend client, skipping
    the test if the fixture doesn't expose a usable creation method (keeps
    this module importable/runnable even if the harness's client API
    differs slightly)."""
    try:
        ddb_client.create_table(
            TableName=name,
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
    except Exception as exc:  # pragma: no cover - defensive skip
        pytest.skip(f"backend client create_table not usable: {exc}")


def _put_item(ddb_client, name, item):
    try:
        ddb_client.put_item(TableName=name, Item=item)
    except Exception as exc:  # pragma: no cover - defensive skip
        pytest.skip(f"backend client put_item not usable: {exc}")


def test_missing_table_name_is_usage_error(cli):
    result = cli("dynamodb", "query", "--key-condition-expression", "pk = :v")
    assert result.returncode == 252
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_missing_subcommand_is_usage_error(cli):
    result = cli("dynamodb")
    assert result.returncode == 252
    assert result.stdout == ""


def test_unknown_flag_is_usage_error(cli):
    result = cli("dynamodb", "scan", "--table-name", "sometable", "--not-a-real-flag", "x")
    assert result.returncode == 252
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_duplicate_table_name_flag_is_usage_error(cli):
    result = cli(
        "dynamodb", "scan",
        "--table-name", "t1",
        "--table-name", "t2",
    )
    assert result.returncode == 252
    assert result.stdout == ""


def test_malformed_json_flag_is_usage_error(cli):
    result = cli(
        "dynamodb", "query",
        "--table-name", "sometable",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", "{not valid json",
    )
    assert result.returncode == 252
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_query_nonexistent_table_is_modeled_service_error(cli):
    result = cli(
        "dynamodb", "query",
        "--table-name", "definitely-does-not-exist-table-xyz",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", json.dumps({":v": {"S": "x"}}),
    )
    assert result.returncode == 254
    assert result.stdout == ""
    assert "ResourceNotFoundException" in result.stderr


def test_scan_nonexistent_table_is_modeled_service_error(cli):
    result = cli("dynamodb", "scan", "--table-name", "another-missing-table-abc")
    assert result.returncode == 254
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_no_stdout_stderr_mixing_on_failure(cli):
    result = cli("dynamodb", "scan", "--table-name", "missing-table-mixcheck")
    # Never both non-empty simultaneously on a failing invocation.
    assert not (result.stdout.strip() and result.stderr.strip())
    assert result.returncode != 0


def test_scan_success_returns_parseable_json_with_clean_streams(cli, ddb_client):
    table = "held-out-scan-success-table"
    _mk_table(ddb_client, table)
    result = cli("dynamodb", "scan", "--table-name", table)
    assert result.returncode == 0
    assert result.stderr == ""
    body = json.loads(result.stdout)
    assert "Items" in body


def test_put_item_then_query_cross_command_consistency(cli, ddb_client):
    table = "held-out-query-consistency-table"
    _mk_table(ddb_client, table)
    _put_item(ddb_client, table, {"pk": {"S": "abc123"}, "val": {"N": "5"}})

    result = cli(
        "dynamodb", "query",
        "--table-name", table,
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", json.dumps({":v": {"S": "abc123"}}),
    )
    assert result.returncode == 0
    assert result.stderr == ""
    body = json.loads(result.stdout)
    items = body.get("Items", [])
    assert any(
        item.get("pk", {}).get("S") == "abc123" for item in items
    ), f"expected written item to be retrievable via query, got: {items}"


def test_boolean_flag_consistent_read_accepted_without_value(cli, ddb_client):
    table = "held-out-bool-flag-table"
    _mk_table(ddb_client, table)
    result = cli("dynamodb", "scan", "--table-name", table, "--consistent-read")
    # Should be treated as a no-value boolean switch, not require an arg.
    assert result.returncode == 0
    assert result.stderr == ""
    json.loads(result.stdout)