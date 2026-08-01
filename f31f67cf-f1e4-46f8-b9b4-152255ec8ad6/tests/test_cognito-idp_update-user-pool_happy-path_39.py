def test_update_user_pool_with_only_id_succeeds(cli, cognito):
    pool_name = "update-user-pool-happy-path"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "update-user-pool",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0, result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name