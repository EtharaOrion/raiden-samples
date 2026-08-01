def test_set_user_pool_mfa_config_with_only_pool_id_preserves_configuration(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "mfa-config-edge-pool"},
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

    resulting_config = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert resulting_config["MfaConfiguration"] == "OPTIONAL"
    assert resulting_config["SoftwareTokenMfaConfiguration"]["Enabled"] is True