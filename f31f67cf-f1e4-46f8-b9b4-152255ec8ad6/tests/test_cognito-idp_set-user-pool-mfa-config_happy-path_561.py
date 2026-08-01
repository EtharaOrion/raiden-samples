def test_set_user_pool_mfa_config_with_only_pool_id_succeeds(cli, cognito, tmp_path):
    pool_name = f"mfa-config-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert before["MfaConfiguration"] == "OFF"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert after["MfaConfiguration"] == "OFF"

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name