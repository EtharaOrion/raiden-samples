def test_delete_user_pool_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-invalid-flag-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "delete-user-pool",
        "--user-pool-id", pool_id,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown" in result.stderr or "usage" in result.stderr.lower()

    # Pool must still exist because the command was rejected before execution
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id