def test_update_user_pool_missing_required_user_pool_id(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-user-pool-invalid-args"},
    )
    pool_id = created["UserPool"]["Id"]

    result = cli("cognito-idp", "update-user-pool")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "update-user-pool-invalid-args"