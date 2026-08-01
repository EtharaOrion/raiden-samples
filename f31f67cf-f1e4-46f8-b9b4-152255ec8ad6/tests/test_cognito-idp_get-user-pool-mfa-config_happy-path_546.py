def test_get_user_pool_mfa_config_happy_path(cli, cognito):
    import json

    pool_name = "get-mfa-config-happy-path"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
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
    assert output["MfaConfiguration"] == "OFF"

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name

    stored_config = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert stored_config["MfaConfiguration"] == "OFF"
    assert output["MfaConfiguration"] == stored_config["MfaConfiguration"]