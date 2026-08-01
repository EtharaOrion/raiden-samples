def test_set_user_pool_mfa_config_optional(cli, cognito, tmp_path):
    pool_name = f"mfa-edge-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": pool_id,
            "MfaConfiguration": "OFF",
            "SoftwareTokenMfaConfiguration": {"Enabled": True},
        },
    )
    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert before["MfaConfiguration"] == "OFF"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--mfa-configuration",
        "OPTIONAL",
    )
    assert result.returncode == 0

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert after["MfaConfiguration"] == "OPTIONAL"