"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import uuid

import pytest


def _table_name(prefix="t"):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _create_table_args(name):
    return [
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=pk,AttributeType=S",
        "--key-schema", "AttributeName=pk,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    ]


def test_list_tables_empty_is_valid_json_with_empty_list(cli):
    res = cli("dynamodb", "list-tables")
    assert res.returncode == 0
    assert res.stderr == ""
    body = json.loads(res.stdout)
    names = body.get("TableNames", body)
    assert names == [] or names == {"TableNames": []}


def test_create_table_then_appears_in_list_tables(cli):
    name = _table_name("create")
    res = cli(*_create_table_args(name))
    assert res.returncode == 0
    assert res.stderr == ""
    json.loads(res.stdout)  # stdout must be valid json

    res2 = cli("dynamodb", "list-tables")
    assert res2.returncode == 0
    body = json.loads(res2.stdout)
    assert name in body["TableNames"]


def test_duplicate_create_table_fails_resource_in_use(cli):
    name = _table_name("dup")
    r1 = cli(*_create_table_args(name))
    assert r1.returncode == 0

    r2 = cli(*_create_table_args(name))
    assert r2.returncode == 254
    assert r2.stdout == ""
    assert "ResourceInUseException" in r2.stderr


def test_get_item_on_nonexistent_table_fails(cli):
    name = _table_name("ghost")
    res = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"pk": {"S": "x"}}),
    )
    assert res.returncode == 254
    assert res.stdout == ""
    assert "ResourceNotFoundException" in res.stderr


def test_put_item_then_get_item_roundtrip_and_number_as_string(cli):
    name = _table_name("roundtrip")
    r = cli(*_create_table_args(name))
    assert r.returncode == 0

    key = {"pk": {"S": "item1"}}
    item = {"pk": {"S": "item1"}, "count": {"N": "42"}}
    put_res = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps(item),
    )
    assert put_res.returncode == 0
    assert put_res.stderr == ""
    json.loads(put_res.stdout)

    get_res = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps(key),
        "--consistent-read",
    )
    assert get_res.returncode == 0
    assert get_res.stderr == ""
    body = json.loads(get_res.stdout)
    assert body["Item"]["pk"] == {"S": "item1"}
    assert body["Item"]["count"] == {"N": "42"}
    assert isinstance(body["Item"]["count"]["N"], str)


def test_get_item_absent_key_returns_success_without_item(cli):
    name = _table_name("absent")
    r = cli(*_create_table_args(name))
    assert r.returncode == 0

    get_res = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"pk": {"S": "does-not-exist"}}),
    )
    assert get_res.returncode == 0
    assert get_res.stderr == ""
    body = json.loads(get_res.stdout)
    assert "Item" not in body


def test_conditional_put_failure_does_not_mutate_stored_item(cli):
    name = _table_name("cond")
    r = cli(*_create_table_args(name))
    assert r.returncode == 0

    original = {"pk": {"S": "k1"}, "v": {"S": "original"}}
    put1 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps(original),
    )
    assert put1.returncode == 0

    conflicting = {"pk": {"S": "k1"}, "v": {"S": "changed"}}
    put2 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps(conflicting),
        "--condition-expression", "attribute_not_exists(pk)",
    )
    assert put2.returncode == 254
    assert put2.stdout == ""
    assert "ConditionalCheckFailedException" in put2.stderr

    get_res = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--key", json.dumps({"pk": {"S": "k1"}}),
    )
    body = json.loads(get_res.stdout)
    assert body["Item"]["v"] == {"S": "original"}


def test_unknown_flag_is_usage_error_no_network(cli):
    name = _table_name("badflag")
    res = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=pk,AttributeType=S",
        "--key-schema", "AttributeName=pk,KeyType=HASH",
        "--totally-bogus-flag", "x",
    )
    assert res.returncode == 252
    assert res.stdout == ""

    listed = cli("dynamodb", "list-tables")
    body = json.loads(listed.stdout)
    assert name not in body["TableNames"]


def test_duplicate_flag_is_usage_error(cli):
    name = _table_name("dupflag")
    res = cli(
        "dynamodb", "get-item",
        "--table-name", name,
        "--table-name", name,
        "--key", json.dumps({"pk": {"S": "x"}}),
    )
    assert res.returncode == 252
    assert res.stdout == ""


def test_oversized_table_name_is_usage_error(cli):
    name = "x" * 512
    res = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=pk,AttributeType=S",
        "--key-schema", "AttributeName=pk,KeyType=HASH",
    )
    assert res.returncode == 252
    assert res.stdout == ""


def test_malformed_json_in_key_flag_is_usage_error(cli):
    res = cli(
        "dynamodb", "get-item",
        "--table-name", "some-table",
        "--key", "{not valid json",
    )
    assert res.returncode == 252
    assert res.stdout == ""


def test_key_schema_attribute_definitions_mismatch_is_validation_error(cli):
    name = _table_name("mismatch")
    res = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=other,AttributeType=S",
        "--key-schema", "AttributeName=pk,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert res.returncode == 254
    assert res.stdout == ""
    assert "ValidationException" in res.stderr