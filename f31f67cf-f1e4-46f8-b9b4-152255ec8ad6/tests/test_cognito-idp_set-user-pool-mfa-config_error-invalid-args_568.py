def test_set_user_pool_mfa_config_rejects_unknown_malformed_argument(cli, cognito):
    pool_name = "mfa-invalid-args-pool"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert after == before
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == pool_name