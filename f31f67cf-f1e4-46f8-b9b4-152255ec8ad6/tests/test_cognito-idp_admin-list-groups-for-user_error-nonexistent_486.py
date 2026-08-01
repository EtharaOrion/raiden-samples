def test_admin_list_groups_for_user_nonexistent_pool(cli, cognito):
    deleted_pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-list-groups-for-user-deleted"},
    )["UserPool"]
    deleted_pool_id = deleted_pool["Id"]

    sentinel_pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "admin-list-groups-for-user-sentinel"},
    )["UserPool"]
    sentinel_pool_id = sentinel_pool["Id"]

    cognito.rpc("DeleteUserPool", {"UserPoolId": deleted_pool_id})

    result = cli(
        "cognito-idp",
        "admin-list-groups-for-user",
        "--username",
        "nonexistent-user",
        "--user-pool-id",
        deleted_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    pools_by_id = {pool["Id"]: pool for pool in pools}
    assert deleted_pool_id not in pools_by_id
    assert pools_by_id[sentinel_pool_id]["Name"] == "admin-list-groups-for-user-sentinel"