def test_describe_user_pool_rejects_unknown_flag(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "describe-user-pool-invalid-args"},
    )
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "describe-user-pool",
        "--user-pool-id",
        pool_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "describe-user-pool-invalid-args"