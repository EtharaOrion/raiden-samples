def test_get_user_pool_mfa_config_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"mfa-config-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

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
        "get-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["MfaConfiguration"] == "OPTIONAL"
    assert output["SoftwareTokenMfaConfiguration"]["Enabled"] is True

    persisted = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": pool_id},
    )
    assert persisted["MfaConfiguration"] == "OPTIONAL"
    assert persisted["SoftwareTokenMfaConfiguration"]["Enabled"] is True