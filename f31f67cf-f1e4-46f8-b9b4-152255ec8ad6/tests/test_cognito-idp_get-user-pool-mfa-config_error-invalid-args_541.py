def test_get_user_pool_mfa_config_missing_user_pool_id(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "mfa-invalid-args-pool"})
    pool_id = created["UserPool"]["Id"]
    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})

    result = cli("cognito-idp", "get-user-pool-mfa-config")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "mfa-invalid-args-pool"

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert after["MfaConfiguration"] == before["MfaConfiguration"]