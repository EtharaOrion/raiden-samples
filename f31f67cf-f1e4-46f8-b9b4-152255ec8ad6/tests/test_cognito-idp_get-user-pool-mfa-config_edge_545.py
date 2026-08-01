def test_get_user_pool_mfa_config_returns_existing_pool_configuration(cli, cognito):
    import json

    created = cognito.rpc("CreateUserPool", {"PoolName": "mfa-config-edge-pool"})
    user_pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": user_pool_id,
            "MfaConfiguration": "OPTIONAL",
        },
    )

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["MfaConfiguration"] == "OPTIONAL"

    stored = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": user_pool_id},
    )
    assert stored["MfaConfiguration"] == "OPTIONAL"
    assert output["MfaConfiguration"] == stored["MfaConfiguration"]