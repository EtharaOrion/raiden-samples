"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import pytest


def _parse_json_stdout(proc):
    assert proc.stdout, f"expected non-empty stdout, stderr={proc.stderr!r}"
    return json.loads(proc.stdout)


def test_create_user_pool_success_shape(cli):
    proc = cli("cognito-idp", "create-user-pool", "--pool-name", "pool-shape-test")
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ""
    data = _parse_json_stdout(proc)
    assert "UserPool" in data
    assert "Id" in data["UserPool"]
    assert isinstance(data["UserPool"]["Id"], str) and data["UserPool"]["Id"]


def test_created_pool_visible_in_separate_list_invocation(cli):
    create = cli("cognito-idp", "create-user-pool", "--pool-name", "pool-list-test")
    assert create.returncode == 0, create.stderr
    pool_id = json.loads(create.stdout)["UserPool"]["Id"]

    listed = cli("cognito-idp", "list-user-pools", "--max-results", "60")
    assert listed.returncode == 0, listed.stderr
    data = json.loads(listed.stdout)
    ids = [p["Id"] for p in data.get("UserPools", [])]
    assert pool_id in ids


def test_missing_required_flag_is_usage_error(cli):
    proc = cli("cognito-idp", "create-user-pool")
    assert proc.returncode == 252
    assert proc.stdout == ""
    assert proc.stderr.strip() != ""


def test_unknown_flag_is_usage_error(cli):
    proc = cli("cognito-idp", "create-user-pool", "--pool-name", "x", "--totally-bogus-flag", "value")
    assert proc.returncode == 252
    assert proc.stdout == ""
    assert proc.stderr.strip() != ""


def test_repeated_flag_is_usage_error(cli):
    proc = cli(
        "cognito-idp", "create-user-pool",
        "--pool-name", "first-name",
        "--pool-name", "second-name",
    )
    assert proc.returncode == 252
    assert proc.stdout == ""


def test_describe_nonexistent_pool_is_service_error(cli):
    proc = cli("cognito-idp", "describe-user-pool", "--user-pool-id", "us-east-1_doesnotexist")
    assert proc.returncode in (254, 1, 255)
    assert proc.stdout == ""
    assert proc.stderr.strip() != ""


def test_oversized_pool_id_is_usage_error(cli):
    long_id = "a" * 56  # limit is <=55
    proc = cli("cognito-idp", "describe-user-pool", "--user-pool-id", long_id)
    assert proc.returncode == 252
    assert proc.stdout == ""


def test_max_results_boundaries_for_list_user_pools(cli):
    too_low = cli("cognito-idp", "list-user-pools", "--max-results", "0")
    assert too_low.returncode == 252
    assert too_low.stdout == ""

    too_high = cli("cognito-idp", "list-user-pools", "--max-results", "61")
    assert too_high.returncode == 252
    assert too_high.stdout == ""

    low_ok = cli("cognito-idp", "list-user-pools", "--max-results", "1")
    assert low_ok.returncode == 0, low_ok.stderr
    json.loads(low_ok.stdout)

    high_ok = cli("cognito-idp", "list-user-pools", "--max-results", "60")
    assert high_ok.returncode == 0, high_ok.stderr
    json.loads(high_ok.stdout)


def test_delete_pool_removes_from_listing_and_errors_on_describe(cli):
    create = cli("cognito-idp", "create-user-pool", "--pool-name", "pool-to-delete")
    assert create.returncode == 0, create.stderr
    pool_id = json.loads(create.stdout)["UserPool"]["Id"]

    delete = cli("cognito-idp", "delete-user-pool", "--user-pool-id", pool_id)
    assert delete.returncode == 0, delete.stderr

    describe = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pool_id)
    assert describe.returncode in (254, 1, 255)
    assert describe.stdout == ""

    listed = cli("cognito-idp", "list-user-pools", "--max-results", "60")
    assert listed.returncode == 0, listed.stderr
    ids = [p["Id"] for p in json.loads(listed.stdout).get("UserPools", [])]
    assert pool_id not in ids


def test_admin_create_user_visible_via_list_and_get_in_separate_invocations(cli):
    create_pool = cli("cognito-idp", "create-user-pool", "--pool-name", "pool-for-users")
    assert create_pool.returncode == 0, create_pool.stderr
    pool_id = json.loads(create_pool.stdout)["UserPool"]["Id"]

    create_user = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", pool_id,
        "--username", "cross-cmd-user",
    )
    assert create_user.returncode == 0, create_user.stderr
    json.loads(create_user.stdout)

    get_user = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", "cross-cmd-user",
    )
    assert get_user.returncode == 0, get_user.stderr
    got = json.loads(get_user.stdout)
    assert got.get("Username") == "cross-cmd-user"

    listed = cli("cognito-idp", "list-users", "--user-pool-id", pool_id)
    assert listed.returncode == 0, listed.stderr
    usernames = [u.get("Username") for u in json.loads(listed.stdout).get("Users", [])]
    assert "cross-cmd-user" in usernames


def test_admin_get_user_unknown_username_is_service_error(cli):
    create_pool = cli("cognito-idp", "create-user-pool", "--pool-name", "pool-for-unknown-user")
    assert create_pool.returncode == 0, create_pool.stderr
    pool_id = json.loads(create_pool.stdout)["UserPool"]["Id"]

    proc = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", "no-such-user-exists",
    )
    assert proc.returncode in (254, 1, 255)
    assert proc.stdout == ""
    assert proc.stderr.strip() != ""


def test_create_user_pool_client_requires_real_pool(cli):
    proc = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", "us-east-1_nonexistentpool",
        "--client-name", "some-client",
    )
    assert proc.returncode in (254, 1, 255)
    assert proc.stdout == ""


def test_exit_code_never_outside_contract_and_never_mixed_streams(cli):
    ok = cli("cognito-idp", "list-user-pools")
    assert ok.returncode in (0, 1, 252, 254, 255)
    assert not (ok.stdout.strip() and ok.stderr.strip())

    bad = cli("cognito-idp", "list-user-pools", "--max-results", "0")
    assert bad.returncode in (0, 1, 252, 254, 255)
    assert not (bad.stdout.strip() and bad.stderr.strip())