def test_delete_user_pool_removes_existing_pool(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-user-pool-edge-" + ("x" * 55)},
    )
    user_pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(pool["Id"] != user_pool_id for pool in listed["UserPools"])