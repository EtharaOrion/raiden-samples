def test_delete_user_pool_removes_existing_pool(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "delete-user-pool-edge"})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert all(pool["Id"] != pool_id for pool in pools)