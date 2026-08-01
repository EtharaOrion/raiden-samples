def test_set_user_pool_mfa_config_with_existing_configuration(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "mfa-config-pool"})
    pool_id = pool["UserPool"]["Id"]

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
    output = json.loads(result.stdout)
    assert output["MfaConfiguration"] == "OPTIONAL"

    resulting_config = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert resulting_config["MfaConfiguration"] == "OPTIONAL"
    assert resulting_config["SoftwareTokenMfaConfiguration"]["Enabled"] is True