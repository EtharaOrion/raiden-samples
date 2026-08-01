def test_delete_user_pool_missing_required_arg(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli("cognito-idp", "delete-user-pool")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "user-pool-id" in result.stderr.lower()

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id