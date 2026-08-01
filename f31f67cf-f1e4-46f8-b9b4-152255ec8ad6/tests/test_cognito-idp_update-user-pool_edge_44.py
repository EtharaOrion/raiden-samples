def test_update_user_pool_turns_mfa_off(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "update-user-pool-mfa-edge"})
    user_pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": user_pool_id,
            "MfaConfiguration": "OPTIONAL",
            "SoftwareTokenMfaConfiguration": {"Enabled": True},
        },
    )
    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": user_pool_id})
    assert before["MfaConfiguration"] == "OPTIONAL"

    result = cli(
        "cognito-idp",
        "update-user-pool",
        "--user-pool-id",
        user_pool_id,
        "--mfa-configuration",
        "OFF",
    )

    assert result.returncode == 0
    after = cognito.rpc("DescribeUserPool", {"UserPoolId": user_pool_id})
    assert after["UserPool"]["Id"] == user_pool_id
    assert after["UserPool"]["MfaConfiguration"] == "OFF"