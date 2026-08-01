def test_list_users_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "list-users",
        "--user-pool-id", pool_id,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # Pool still exists and is unaffected by the rejected command
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "invalid-args-pool"