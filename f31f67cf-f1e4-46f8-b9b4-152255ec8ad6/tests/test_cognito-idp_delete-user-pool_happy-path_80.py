def test_delete_user_pool_happy_path(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-user-pool-happy-path"},
    )
    pool_id = created["UserPool"]["Id"]

    existing = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert existing["UserPool"]["Name"] == "delete-user-pool-happy-path"

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        pool_id,
    )
    assert result.returncode == 0

    remaining = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert pool_id not in {pool["Id"] for pool in remaining["UserPools"]}