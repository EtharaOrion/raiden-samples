def test_set_user_pool_mfa_config_requires_user_pool_id(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "mfa-config-invalid-args-pool"},
    )
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )

    result = cli("cognito-idp", "set-user-pool-mfa-config")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    after = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert after == before
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == "mfa-config-invalid-args-pool"