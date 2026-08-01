def test_get_user_pool_mfa_config_rejects_unknown_attribute_definitions(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "invalid-mfa-config-args"})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})

    result = cli(
        "cognito-idp",
        "get-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert after["MfaConfiguration"] == before["MfaConfiguration"]

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == "invalid-mfa-config-args"