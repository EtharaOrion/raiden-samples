def test_create_group_nonexistent_user_pool(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "create-group-missing-pool"})
    user_pool_id = created["UserPool"]["Id"]

    cognito.rpc("DeleteUserPool", {"UserPoolId": user_pool_id})

    result = cli(
        "cognito-idp",
        "create-group",
        "--group-name",
        "ghost-group",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})["UserPools"]
    assert all(pool["Id"] != user_pool_id for pool in pools)