def test_get_user_pool_mfa_config_rejects_empty_user_pool_id(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "mfa-config-empty-id-validation"},
    )
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "mfa-config-empty-id-validation"