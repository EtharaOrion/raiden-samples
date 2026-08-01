def test_delete_user_pool_happy_path(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-user-pool-happy-path"},
    )
    user_pool_id = created["UserPool"]["Id"]

    existing = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": user_pool_id},
    )
    assert existing["UserPool"]["Name"] == "delete-user-pool-happy-path"

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        user_pool_id,
    )
    assert result.returncode == 0

    remaining = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(
        pool["Id"] != user_pool_id
        for pool in remaining.get("UserPools", [])
    )