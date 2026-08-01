def test_get_user_pool_mfa_config_happy_path(cli, cognito):
    import json

    created = cognito.rpc("CreateUserPool", {"PoolName": "mfa-config-test-pool"})
    user_pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["MfaConfiguration"] == "OFF"

    stored_config = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": user_pool_id},
    )
    assert stored_config["MfaConfiguration"] == "OFF"