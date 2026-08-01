def test_set_user_pool_mfa_config_with_existing_pool(cli, cognito, tmp_path):
    import json

    pool_name = "mfa-config-" + tmp_path.name[-40:]
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    baseline = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert baseline["MfaConfiguration"] == "OFF"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["MfaConfiguration"] == "OFF"

    resulting = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert resulting["MfaConfiguration"] == "OFF"

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name