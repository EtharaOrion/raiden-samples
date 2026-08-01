"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

import json
import uuid

import pytest


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _assert_success(res):
    assert res.returncode == 0, f"expected exit 0, got {res.returncode}; stderr={res.stderr!r}"
    assert res.stderr == "" or res.stderr.strip() == "", f"stderr should be empty on success, got {res.stderr!r}"
    assert res.stdout.strip() != "", "stdout should contain JSON on success"
    return json.loads(res.stdout)


def _assert_failure(res):
    assert res.returncode != 0
    assert res.returncode in (1, 252, 254, 255)
    assert res.stdout.strip() == "", f"stdout should be empty on failure, got {res.stdout!r}"
    assert res.stderr.strip() != "", "stderr should contain an error message on failure"
    return res


def _create_pool(cli, name=None):
    name = name or _uniq("pool")
    res = cli("cognito-idp", "create-user-pool", "--pool-name", name)
    body = _assert_success(res)
    pool_id = body.get("UserPool", {}).get("Id") or body.get("UserPoolId") or body.get("Id")
    assert pool_id, f"expected a pool id in response: {body}"
    return pool_id, name


def test_create_and_describe_user_pool_roundtrip(cli):
    pool_id, name = _create_pool(cli)
    res = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pool_id)
    body = _assert_success(res)
    pool = body.get("UserPool", body)
    assert pool.get("Id") == pool_id
    assert pool.get("Name") == name


def test_list_user_pools_reflects_created_pool(cli):
    pool_id, name = _create_pool(cli)
    res = cli("cognito-idp", "list-user-pools", "--max-results", "60")
    body = _assert_success(res)
    pools = body.get("UserPools", [])
    ids = {p.get("Id") for p in pools}
    assert pool_id in ids


def test_create_user_pool_client_then_describe(cli):
    pool_id, _ = _create_pool(cli)
    client_name = _uniq("client")
    res = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", pool_id,
        "--client-name", client_name,
    )
    body = _assert_success(res)
    client = body.get("UserPoolClient", body)
    client_id = client.get("ClientId")
    assert client_id

    res2 = cli(
        "cognito-idp", "describe-user-pool-client",
        "--user-pool-id", pool_id,
        "--client-id", client_id,
    )
    body2 = _assert_success(res2)
    client2 = body2.get("UserPoolClient", body2)
    assert client2.get("ClientId") == client_id
    assert client2.get("ClientName") == client_name


def test_duplicate_admin_create_user_fails_with_username_exists(cli):
    pool_id, _ = _create_pool(cli)
    username = _uniq("user")
    res1 = cli("cognito-idp", "admin-create-user", "--user-pool-id", pool_id, "--username", username)
    _assert_success(res1)

    res2 = cli("cognito-idp", "admin-create-user", "--user-pool-id", pool_id, "--username", username)
    _assert_failure(res2)
    assert res2.returncode in (1, 254)
    assert "UsernameExists" in res2.stderr or "usernameexists" in res2.stderr.lower()


def test_delete_user_pool_cascades_to_resource_not_found(cli):
    pool_id, _ = _create_pool(cli)
    username = _uniq("user")
    res_user = cli("cognito-idp", "admin-create-user", "--user-pool-id", pool_id, "--username", username)
    _assert_success(res_user)

    del_res = cli("cognito-idp", "delete-user-pool", "--user-pool-id", pool_id)
    _assert_success(del_res)

    desc_res = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pool_id)
    fail = _assert_failure(desc_res)
    assert "ResourceNotFound" in fail.stderr or "resourcenotfound" in fail.stderr.lower() or "not found" in fail.stderr.lower()

    get_user_res = cli("cognito-idp", "admin-get-user", "--user-pool-id", pool_id, "--username", username)
    _assert_failure(get_user_res)


def test_unknown_flag_is_client_usage_error(cli):
    res = cli("cognito-idp", "create-user-pool", "--pool-name", "x", "--totally-bogus-flag", "y")
    assert res.returncode == 252, f"expected exit 252 for unknown flag, got {res.returncode}"
    assert res.stdout.strip() == ""
    assert res.stderr.strip() != ""


def test_missing_required_flag_is_client_usage_error(cli):
    # create-user-pool-client requires --user-pool-id and --client-name at minimum
    res = cli("cognito-idp", "create-user-pool-client", "--client-name", "nopool")
    assert res.returncode == 252, f"expected exit 252 for missing required flag, got {res.returncode}"
    assert res.stdout.strip() == ""
    assert res.stderr.strip() != ""


def test_group_lifecycle_create_get_list_delete(cli):
    pool_id, _ = _create_pool(cli)
    group_name = _uniq("grp")

    res_create = cli("cognito-idp", "create-group", "--user-pool-id", pool_id, "--group-name", group_name)
    _assert_success(res_create)

    res_get = cli("cognito-idp", "get-group", "--user-pool-id", pool_id, "--group-name", group_name)
    body_get = _assert_success(res_get)
    group = body_get.get("Group", body_get)
    assert group.get("GroupName") == group_name

    res_list = cli("cognito-idp", "list-groups", "--user-pool-id", pool_id)
    body_list = _assert_success(res_list)
    names = {g.get("GroupName") for g in body_list.get("Groups", [])}
    assert group_name in names

    res_del = cli("cognito-idp", "delete-group", "--user-pool-id", pool_id, "--group-name", group_name)
    _assert_success(res_del)

    res_get2 = cli("cognito-idp", "get-group", "--user-pool-id", pool_id, "--group-name", group_name)
    _assert_failure(res_get2)


def test_admin_add_user_to_group_reflected_in_membership_list(cli):
    pool_id, _ = _create_pool(cli)
    username = _uniq("user")
    group_name = _uniq("grp")

    _assert_success(cli("cognito-idp", "admin-create-user", "--user-pool-id", pool_id, "--username", username))
    _assert_success(cli("cognito-idp", "create-group", "--user-pool-id", pool_id, "--group-name", group_name))
    _assert_success(cli(
        "cognito-idp", "admin-add-user-to-group",
        "--user-pool-id", pool_id, "--username", username, "--group-name", group_name,
    ))

    res_groups = cli("cognito-idp", "admin-list-groups-for-user", "--user-pool-id", pool_id, "--username", username)
    body_groups = _assert_success(res_groups)
    names = {g.get("GroupName") for g in body_groups.get("Groups", [])}
    assert group_name in names

    res_users_in_group = cli("cognito-idp", "list-users-in-group", "--user-pool-id", pool_id, "--group-name", group_name)
    body_users = _assert_success(res_users_in_group)
    usernames = {u.get("Username") for u in body_users.get("Users", [])}
    assert username in usernames

    _assert_success(cli(
        "cognito-idp", "admin-remove-user-from-group",
        "--user-pool-id", pool_id, "--username", username, "--group-name", group_name,
    ))
    res_groups2 = cli("cognito-idp", "admin-list-groups-for-user", "--user-pool-id", pool_id, "--username", username)
    body_groups2 = _assert_success(res_groups2)
    names2 = {g.get("GroupName") for g in body_groups2.get("Groups", [])}
    assert group_name not in names2


def test_update_user_pool_client_state_is_persisted_across_invocations(cli):
    pool_id, _ = _create_pool(cli)
    client_name = _uniq("client")
    res = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", pool_id, "--client-name", client_name,
    )
    body = _assert_success(res)
    client_id = body.get("UserPoolClient", body).get("ClientId")

    new_name = _uniq("client-renamed")
    res_update = cli(
        "cognito-idp", "update-user-pool-client",
        "--user-pool-id", pool_id, "--client-id", client_id, "--client-name", new_name,
    )
    _assert_success(res_update)

    # Fresh subprocess invocation must see the update — proving state lives server-side.
    res_desc = cli(
        "cognito-idp", "describe-user-pool-client",
        "--user-pool-id", pool_id, "--client-id", client_id,
    )
    body_desc = _assert_success(res_desc)
    client = body_desc.get("UserPoolClient", body_desc)
    assert client.get("ClientName") == new_name


def test_operation_on_nonexistent_pool_is_resource_not_found(cli):
    fake_pool_id = _uniq("us-east-1_FAKE")
    res = cli("cognito-idp", "describe-user-pool", "--user-pool-id", fake_pool_id)
    fail = _assert_failure(res)
    assert fail.returncode in (1, 254)