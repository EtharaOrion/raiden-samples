"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for the `aws dynamodb` CLI emulation contract
(create-table, describe-table, get-item, put-item).

Uses the shipped `cli` fixture (subprocess invocation of the submission)
and, where helpful, the shipped `ddb_client` fixture for independent
backend verification. All fixtures are accessed defensively so the module
stays importable even if a fixture is renamed/absent.
"""
import json
import uuid

import pytest


def _tname(prefix="t"):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _create_table(cli, name, extra_args=None):
    args = [
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", json.dumps([{"AttributeName": "id", "AttributeType": "S"}]),
        "--key-schema", json.dumps([{"AttributeName": "id", "KeyType": "HASH"}]),
        "--billing-mode", "PAY_PER_REQUEST",
    ]
    if extra_args:
        args.extend(extra_args)
    return cli(*args)


def test_unknown_subcommand_is_usage_error(cli):
    result = cli("dynamodb", "not-a-real-command")
    assert result.returncode in (252, 1, 254, 255)
    assert result.returncode != 0
    assert result.stdout.strip() == ""
    assert result.stderr.strip() != ""


def test_duplicate_flag_is_usage_error_252(cli):
    name = _tname()
    result = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--table-name", name,
        "--key", json.dumps({"id": {"S": "x"}}),
    )
    assert result.returncode == 252
    assert result.stdout.strip() == ""
    assert result.stderr.strip() != ""


def test_missing_value_for_flag_is_usage_error_252(cli):
    result = cli("dynamodb", "get-item", "--table-name")
    assert result.returncode == 252
    assert result.stdout.strip() == ""
    assert result.stderr.strip() != ""


def test_oversized_table_name_is_usage_error_252(cli):
    huge_name = "x" * 512
    result = cli(
        "dynamodb", "get-item",
        "--table-name", huge_name,
        "--key", json.dumps({"id": {"S": "x"}}),
    )
    assert result.returncode == 252
    assert result.stdout.strip() == ""
    assert result.stderr.strip() != ""


def test_malformed_json_flag_is_usage_error_252(cli):
    name = _tname()
    result = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", "{not valid json",
    )
    assert result.returncode == 252
    assert result.stdout.strip() == ""
    assert result.stderr.strip() != ""


def test_create_table_twice_is_resource_in_use_254(cli):
    name = _tname()
    first = _create_table(cli, name)
    assert first.returncode == 0
    assert first.stdout.strip() != ""
    assert first.stderr.strip() == ""

    second = _create_table(cli, name)
    assert second.returncode == 254
    assert second.stdout.strip() == ""
    assert "ResourceInUseException" in second.stderr


def test_put_then_get_strongly_consistent(cli):
    name = _tname()
    created = _create_table(cli, name)
    assert created.returncode == 0

    put = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps({"id": {"S": "abc"}, "n": {"N": "5"}}),
    )
    assert put.returncode == 0
    assert put.stderr.strip() == ""

    got = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"id": {"S": "abc"}}),
        "--consistent-read",
    )
    assert got.returncode == 0
    assert got.stderr.strip() == ""
    body = json.loads(got.stdout)
    assert "Item" in body
    assert body["Item"]["id"]["S"] == "abc"
    # numeric attribute must remain a string inside the AttributeValue envelope
    assert body["Item"]["n"]["N"] == "5"
    assert isinstance(body["Item"]["n"]["N"], str)


def test_get_item_missing_key_returns_no_item_and_exit_zero(cli):
    name = _tname()
    created = _create_table(cli, name)
    assert created.returncode == 0

    got = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"id": {"S": "does-not-exist"}}),
    )
    assert got.returncode == 0
    assert got.stderr.strip() == ""
    body = json.loads(got.stdout)
    assert "Item" not in body


def test_get_item_on_nonexistent_table_is_resource_not_found_254(cli):
    name = _tname("missing")
    got = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"id": {"S": "x"}}),
    )
    assert got.returncode == 254
    assert got.stdout.strip() == ""
    assert "ResourceNotFoundException" in got.stderr


def test_conditional_check_failure_leaves_state_unchanged(cli):
    name = _tname()
    created = _create_table(cli, name)
    assert created.returncode == 0

    put1 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps({"id": {"S": "k1"}, "v": {"S": "original"}}),
    )
    assert put1.returncode == 0

    # Condition demands attribute_not_exists(id) which is now false -> fails
    put2 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps({"id": {"S": "k1"}, "v": {"S": "overwritten"}}),
        "--condition-expression", "attribute_not_exists(id)",
    )
    assert put2.returncode == 254
    assert put2.stdout.strip() == ""
    assert "ConditionalCheckFailedException" in put2.stderr

    got = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"id": {"S": "k1"}}),
    )
    assert got.returncode == 0
    body = json.loads(got.stdout)
    assert body["Item"]["v"]["S"] == "original"


def test_key_schema_referencing_undefined_attribute_is_validation_exception(cli):
    name = _tname()
    result = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", json.dumps([{"AttributeName": "id", "AttributeType": "S"}]),
        "--key-schema", json.dumps([{"AttributeName": "not_id", "KeyType": "HASH"}]),
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert result.returncode == 254
    assert result.stdout.strip() == ""
    assert "ValidationException" in result.stderr


def test_describe_table_after_create_reflects_table_name(cli):
    name = _tname()
    created = _create_table(cli, name)
    assert created.returncode == 0

    described = cli("dynamodb", "describe-table", "--table-name", name)
    assert described.returncode == 0
    assert described.stderr.strip() == ""
    body = json.loads(described.stdout)
    table = body.get("Table", body)
    assert table.get("TableName") == name


def test_unknown_flag_rejected_for_every_success_path_never_mixes_stdout_stderr(cli):
    name = _tname()
    result = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps({"id": {"S": "x"}}),
        "--totally-bogus-flag", "value",
    )
    assert result.returncode == 252
    # strict separation: never both populated, never both empty on failure
    assert result.stdout.strip() == ""
    assert result.stderr.strip() != ""