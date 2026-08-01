def test_set_user_pool_mfa_config_enables_mfa(cli, cognito, tmp_path):
    pool_name = f"mfa-config-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {"UserPoolId": pool_id, "MfaConfiguration": "OFF"},
    )
    baseline = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert baseline["MfaConfiguration"] == "OFF"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--mfa-configuration",
        "ON",
    )

    assert result.returncode == 0
    current = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert current["MfaConfiguration"] == "ON"