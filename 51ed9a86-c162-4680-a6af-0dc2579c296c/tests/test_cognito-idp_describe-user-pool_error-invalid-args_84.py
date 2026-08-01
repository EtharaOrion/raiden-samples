def test_describe_user_pool_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "describe-user-pool",
        "--user-pool-id", pool_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown" in result.stderr or "Error" in result.stderr or "argument" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "invalid-args-pool"