def test_set_user_pool_mfa_config_preserves_existing_configuration(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "set-mfa-config-happy-path"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": pool_id,
            "MfaConfiguration": "OPTIONAL",
            "SoftwareTokenMfaConfiguration": {"Enabled": True},
        },
    )

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0

    configuration = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert configuration["MfaConfiguration"] == "OPTIONAL"
    assert configuration["SoftwareTokenMfaConfiguration"]["Enabled"] is True