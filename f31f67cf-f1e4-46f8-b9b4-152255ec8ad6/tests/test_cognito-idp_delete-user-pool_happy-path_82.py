def test_delete_user_pool_happy_path(cli, cognito, tmp_path):
    pool_name = "delete-" + tmp_path.name
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert before["UserPool"]["Name"] == pool_name

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        pool_id,
    )
    assert result.returncode == 0

    remaining = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(pool["Id"] != pool_id for pool in remaining["UserPools"])