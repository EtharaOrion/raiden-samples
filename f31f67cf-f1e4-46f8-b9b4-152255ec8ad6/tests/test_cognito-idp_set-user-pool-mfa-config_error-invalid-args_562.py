def test_set_user_pool_mfa_config_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-mfa-args-pool"})["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert after["MfaConfiguration"] == before["MfaConfiguration"]