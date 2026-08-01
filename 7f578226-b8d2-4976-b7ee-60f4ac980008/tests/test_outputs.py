"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import pytest


def _unique_table_name(prefix="tbl"):
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def test_unknown_subcommand_is_usage_error(cli):
    r = cli("dynamodb", "not-a-real-subcommand", "--table-name", "x")
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_unknown_flag_is_usage_error(cli):
    name = _unique_table_name()
    r = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
        "--not-a-real-flag", "value",
    )
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_duplicate_flag_is_usage_error(cli):
    name = _unique_table_name()
    r = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--table-name", "other_name",
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_missing_required_flag_put_item(cli):
    name = _unique_table_name()
    # --item omitted entirely -> usage error, no network call attempted
    r = cli("dynamodb", "put-item", "--table-name", name)
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_malformed_json_value_is_usage_error(cli):
    name = _unique_table_name()
    r = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", "{not valid json at all",
    )
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_oversized_table_name_is_usage_error(cli):
    huge_name = "x" * 512
    r = cli(
        "dynamodb", "create-table",
        "--table-name", huge_name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r.returncode == 252
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_create_table_success_then_recreate_conflict(cli):
    name = _unique_table_name()
    r1 = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r1.returncode == 0
    assert r1.stderr == ""
    body = json.loads(r1.stdout)
    assert isinstance(body, dict)

    r2 = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r2.returncode == 254
    assert r2.stdout == ""
    assert "ResourceInUse" in r2.stderr


def test_key_schema_attribute_mismatch_is_validation_error(cli):
    name = _unique_table_name()
    r = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=nonexistent_attr,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r.returncode == 254
    assert r.stdout == ""
    assert r.stderr.strip() != ""


def test_put_item_state_persists_across_processes_and_scan_reflects_it(cli):
    name = _unique_table_name()
    r_create = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r_create.returncode == 0

    item = json.dumps({"id": {"S": "abc123"}, "count": {"N": "5"}})
    r_put = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", item,
    )
    assert r_put.returncode == 0
    assert r_put.stderr == ""

    # separate subprocess invocation must see the write
    r_scan = cli("dynamodb", "scan", "--table-name", name)
    assert r_scan.returncode == 0
    assert r_scan.stderr == ""
    body = json.loads(r_scan.stdout)
    items = body.get("Items", [])
    assert len(items) == 1
    found = items[0]
    assert found["id"]["S"] == "abc123"
    # numbers must round-trip as strings under "N", never native JSON numbers
    assert isinstance(found["count"]["N"], str)
    assert found["count"]["N"] == "5"


def test_conditional_check_failed_on_existing_key(cli):
    name = _unique_table_name()
    r_create = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r_create.returncode == 0

    item = json.dumps({"id": {"S": "dup"}})
    r_put1 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", item,
        "--condition-expression", "attribute_not_exists(id)",
    )
    assert r_put1.returncode == 0

    r_put2 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", item,
        "--condition-expression", "attribute_not_exists(id)",
    )
    assert r_put2.returncode == 254
    assert r_put2.stdout == ""
    assert "ConditionalCheckFailed" in r_put2.stderr


def test_put_item_on_nonexistent_table_is_resource_not_found(cli):
    name = _unique_table_name("ghost")
    item = json.dumps({"id": {"S": "x"}})
    r = cli("dynamodb", "put-item", "--table-name", name, "--item", item)
    assert r.returncode == 254
    assert r.stdout == ""
    assert "ResourceNotFound" in r.stderr


def test_scan_and_describe_nonexistent_table_are_modeled_errors(cli):
    name = _unique_table_name("ghost2")
    r_scan = cli("dynamodb", "scan", "--table-name", name)
    assert r_scan.returncode == 254
    assert r_scan.stdout == ""
    assert r_scan.stderr.strip() != ""

    r_describe = cli("dynamodb", "describe-table", "--table-name", name)
    assert r_describe.returncode == 254
    assert r_describe.stdout == ""
    assert r_describe.stderr.strip() != ""


def test_no_stdout_stderr_mixing_on_success_and_failure(cli):
    name = _unique_table_name()
    r_ok = cli(
        "dynamodb", "create-table",
        "--table-name", name,
        "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST",
    )
    assert r_ok.returncode == 0
    assert r_ok.stderr == ""
    json.loads(r_ok.stdout)  # must be valid parseable JSON

    r_bad = cli("dynamodb", "put-item", "--table-name", name)
    assert r_bad.returncode == 252
    assert r_bad.stdout == ""
    assert r_bad.stderr.strip() != ""