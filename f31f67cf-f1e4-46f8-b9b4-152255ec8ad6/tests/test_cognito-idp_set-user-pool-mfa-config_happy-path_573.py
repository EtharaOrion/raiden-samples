def test_set_user_pool_mfa_config_with_only_pool_id_preserves_configuration(cli, cognito):
    import json

    created = cognito.rpc("CreateUserPool", {"PoolName": "mfa-config-preservation-pool"})
    pool_id = created["UserPool"]["Id"]

    cognito.rpc(
        "SetUserPoolMfaConfig",
        {
            "UserPoolId": pool_id,
            "MfaConfiguration": "OPTIONAL",
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