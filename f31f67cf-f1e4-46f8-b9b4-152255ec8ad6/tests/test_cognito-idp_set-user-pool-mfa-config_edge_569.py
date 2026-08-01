def test_set_user_pool_mfa_config_with_only_pool_id_preserves_configuration(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "minimal-mfa-config-pool"})
    user_pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": user_pool_id,
            "MfaConfiguration": "OPTIONAL",
            "SoftwareTokenMfaConfiguration": {"Enabled": True},
        },
    )
    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": user_pool_id})
    assert before["MfaConfiguration"] == "OPTIONAL"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        user_pool_id,
    )
    assert result.returncode == 0

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": user_pool_id})
    assert after["MfaConfiguration"] == "OPTIONAL"