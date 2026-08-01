def test_get_user_pool_mfa_config_valid_pool(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "mfa-config-edge-pool"})["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": pool_id,
            "MfaConfiguration": "OFF",
        },
    )

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["MfaConfiguration"] == "OFF"

    actual = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert actual["MfaConfiguration"] == "OFF"