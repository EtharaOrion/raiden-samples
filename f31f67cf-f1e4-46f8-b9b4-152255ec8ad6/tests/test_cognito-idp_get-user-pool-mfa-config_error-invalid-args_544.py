def test_get_user_pool_mfa_config_rejects_unknown_flag(cli, cognito):
    created = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "mfa-config-invalid-args-pool"},
    )
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    config = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert config["MfaConfiguration"] == "OFF"