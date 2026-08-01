def test_get_user_pool_mfa_config_happy_path(cli, cognito):
    import json

    pool_name = "mfa-config-happy-path"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    user_pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)

    actual_config = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": user_pool_id},
    )
    described = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": user_pool_id},
    )

    assert described["UserPool"]["Name"] == pool_name
    assert actual_config["MfaConfiguration"] == "OFF"
    assert output["MfaConfiguration"] == actual_config["MfaConfiguration"]