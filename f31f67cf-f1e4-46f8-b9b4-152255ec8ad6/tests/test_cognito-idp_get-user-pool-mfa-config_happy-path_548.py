def test_get_user_pool_mfa_config_happy_path(cli, cognito):
    import json

    created = cognito.rpc("CreateUserPool", {"PoolName": "mfa-config-read-test"})
    pool_id = created["UserPool"]["Id"]

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

    actual = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert actual["MfaConfiguration"] == "OFF"
    assert output["MfaConfiguration"] == actual["MfaConfiguration"]