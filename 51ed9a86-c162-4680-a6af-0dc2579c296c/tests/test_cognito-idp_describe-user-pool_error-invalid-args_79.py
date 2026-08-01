def test_describe_user_pool_invalid_flag(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-invalid-flag-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "describe-user-pool",
        "--user-pool-id", pool_id,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # The pool should still exist and be describable via the wire client.
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "describe-invalid-flag-pool"