def test_delete_user_pool_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "attribute-definitions" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id