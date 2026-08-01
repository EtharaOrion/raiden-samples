def test_set_user_pool_mfa_config_rejects_empty_user_pool_id(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "mfa-empty-id-validation-pool"},
    )
    user_pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": user_pool_id,
            "MfaConfiguration": "OFF",
        },
    )

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    mfa_config = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": user_pool_id},
    )
    assert mfa_config["MfaConfiguration"] == "OFF"