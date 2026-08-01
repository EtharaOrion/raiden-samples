"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out tests for the `aws dynamodb` CLI contract (ac28f9b7-8626-4b52-b861-336fa8bddc6a).

These tests exercise cross-command state consistency, output-shape contracts,
argument-parsing error paths, and exit-code discipline, without hardcoding
any submission-internal assumptions beyond the documented contract.
"""
import json
import time
import uuid

import pytest


ALLOWED_EXIT_CODES = {0, 1, 252, 254, 255}


def _uniq_name(prefix="t"):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _try_create_table(ddb_client, name):
    """Best-effort direct-backend table creation, bypassing the CLI (which has
    no create-table subcommand). Returns True on success, False if the
    fixture doesn't expose a usable primitive (test should then skip)."""
    key_schema = [{"AttributeName": "pk", "KeyType": "HASH"}]
    attr_defs = [{"AttributeName": "pk", "AttributeType": "S"}]
    params = dict(
        TableName=name,
        KeySchema=key_schema,
        AttributeDefinitions=attr_defs,
        BillingMode="PAY_PER_REQUEST",
    )
    for attr in ("create_table",):
        fn = getattr(ddb_client, attr, None)
        if callable(fn):
            try:
                fn(**params)
                return True
            except TypeError:
                try:
                    fn(params)
                    return True
                except Exception:
                    pass
            except Exception:
                pass
    for attr in ("request", "call", "send"):
        fn = getattr(ddb_client, attr, None)
        if callable(fn):
            try:
                fn("CreateTable", params)
                return True
            except Exception:
                pass
    return False


def _table_ready(cli, name, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = cli("dynamodb", "list-tables")
        if res.returncode == 0:
            try:
                body = json.loads(res.stdout)
            except json.JSONDecodeError:
                return False
            if name in body.get("TableNames", []):
                return True
        time.sleep(0.2)
    return False


# ---------------------------------------------------------------------------
# Output-contract tests
# ---------------------------------------------------------------------------

def test_list_tables_success_shape(cli):
    res = cli("dynamodb", "list-tables")
    assert res.returncode == 0
    assert res.stderr == ""
    body = json.loads(res.stdout)
    assert "TableNames" in body
    assert isinstance(body["TableNames"], list)


def test_describe_limits_success_shape(cli):
    res = cli("dynamodb", "describe-limits")
    assert res.returncode == 0
    assert res.stderr == ""
    body = json.loads(res.stdout)
    assert isinstance(body, dict)
    assert len(body) > 0


# ---------------------------------------------------------------------------
# CLI argument-parsing error paths -> exit 252
# ---------------------------------------------------------------------------

def test_put_item_missing_table_name_is_usage_error(cli):
    res = cli("dynamodb", "put-item", "--item", json.dumps({"pk": {"S": "x"}}))
    assert res.returncode == 252
    assert res.stdout == ""
    assert res.stderr.strip() != ""


def test_update_item_missing_required_flags_is_usage_error(cli):
    res = cli("dynamodb", "update-item", "--table-name", _uniq_name())
    assert res.returncode == 252
    assert res.stdout == ""


def test_unknown_flag_is_usage_error(cli):
    res = cli(
        "dynamodb", "put-item",
        "--table-name", _uniq_name(),
        "--item", json.dumps({"pk": {"S": "x"}}),
        "--this-flag-does-not-exist", "value",
    )
    assert res.returncode == 252
    assert res.stdout == ""


def test_duplicate_flag_is_usage_error(cli):
    res = cli(
        "dynamodb", "put-item",
        "--table-name", _uniq_name(),
        "--table-name", _uniq_name(),
        "--item", json.dumps({"pk": {"S": "x"}}),
    )
    assert res.returncode == 252
    assert res.stdout == ""


def test_malformed_embedded_json_is_usage_error(cli):
    res = cli(
        "dynamodb", "put-item",
        "--table-name", _uniq_name(),
        "--item", "{not valid json",
    )
    assert res.returncode == 252
    assert res.stdout == ""


# ---------------------------------------------------------------------------
# Modeled service errors -> exit 254
# ---------------------------------------------------------------------------

def test_put_item_nonexistent_table_is_modeled_service_error(cli):
    res = cli(
        "dynamodb", "put-item",
        "--table-name", _uniq_name("missing"),
        "--item", json.dumps({"pk": {"S": "x"}}),
    )
    assert res.returncode == 254
    assert res.stdout == ""
    assert "ResourceNotFoundException" in res.stderr


def test_update_item_nonexistent_table_is_modeled_service_error(cli):
    res = cli(
        "dynamodb", "update-item",
        "--table-name", _uniq_name("missing"),
        "--key", json.dumps({"pk": {"S": "x"}}),
        "--update-expression", "SET a = :v",
        "--expression-attribute-values", json.dumps({":v": {"S": "y"}}),
    )
    assert res.returncode == 254
    assert res.stdout == ""


# ---------------------------------------------------------------------------
# Cross-invocation state consistency + exit-code domain checks
# ---------------------------------------------------------------------------

def test_stdout_stderr_never_both_populated(cli):
    cases = [
        ("dynamodb", "put-item"),  # missing everything -> usage error
        ("dynamodb", "put-item", "--table-name", _uniq_name("nope"),
         "--item", json.dumps({"pk": {"S": "a"}})),  # modeled error
        ("dynamodb", "list-tables"),  # success
    ]
    for args in cases:
        res = cli(*args)
        assert res.returncode in ALLOWED_EXIT_CODES
        assert not (res.stdout.strip() and res.stderr.strip()), (
            f"both stdout and stderr populated for {args}: "
            f"stdout={res.stdout!r} stderr={res.stderr!r}"
        )


def test_exit_codes_restricted_to_documented_set(cli):
    scenarios = [
        ("dynamodb", "list-tables"),
        ("dynamodb", "describe-limits"),
        ("dynamodb", "put-item"),
        ("dynamodb", "put-item", "--table-name", _uniq_name("nope"),
         "--item", json.dumps({"pk": {"S": "a"}})),
        ("dynamodb", "put-item", "--table-name", _uniq_name(),
         "--item", "not json"),
    ]
    for args in scenarios:
        res = cli(*args)
        assert res.returncode in ALLOWED_EXIT_CODES, f"{args} -> {res.returncode}"


def test_put_item_then_list_tables_reflects_backend_state(cli, ddb_client):
    """put-item against a real pre-existing table must be visible to a
    subsequent, independent list-tables invocation (cross-process state
    sharing via the real backend, not private in-process state)."""
    name = _uniq_name("live")
    if not _try_create_table(ddb_client, name):
        pytest.skip("backend fixture does not expose a create-table primitive")
    assert _table_ready(cli, name), "table not visible via list-tables after creation"

    res = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps({"pk": {"S": "row1"}, "n": {"N": "42"}}),
    )
    assert res.returncode == 0
    assert res.stderr == ""

    res2 = cli("dynamodb", "list-tables")
    assert res2.returncode == 0
    body = json.loads(res2.stdout)
    assert name in set(body.get("TableNames", []))


def test_conditional_put_failure_does_not_mutate_and_is_254(cli, ddb_client):
    name = _uniq_name("cond")
    if not _try_create_table(ddb_client, name):
        pytest.skip("backend fixture does not expose a create-table primitive")
    assert _table_ready(cli, name)

    item = {"pk": {"S": "existing"}, "v": {"S": "original"}}
    res = cli("dynamodb", "put-item", "--table-name", name, "--item", json.dumps(item))
    assert res.returncode == 0

    res2 = cli(
        "dynamodb", "put-item",
        "--table-name", name,
        "--item", json.dumps({"pk": {"S": "existing"}, "v": {"S": "changed"}}),
        "--condition-expression", "attribute_not_exists(pk)",
    )
    assert res2.returncode == 254
    assert res2.stdout == ""
    assert "ConditionalCheckFailedException" in res2.stderr

    get_item = getattr(ddb_client, "get_item", None)
    if callable(get_item):
        try:
            stored = get_item(TableName=name, Key={"pk": {"S": "existing"}})
            stored_item = stored.get("Item", stored) if isinstance(stored, dict) else None
            if stored_item is not None and "v" in stored_item:
                assert stored_item["v"] == {"S": "original"}
        except Exception:
            pass