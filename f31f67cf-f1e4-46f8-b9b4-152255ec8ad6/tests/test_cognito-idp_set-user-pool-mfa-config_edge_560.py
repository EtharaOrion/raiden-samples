def test_set_user_pool_mfa_config_turns_mfa_off(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "set-mfa-config-off-test"},
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
    before = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert before["MfaConfiguration"] == "OPTIONAL"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--mfa-configuration",
        "OFF",
    )

    assert result.returncode == 0
    after = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert after["MfaConfiguration"] == "OFF"