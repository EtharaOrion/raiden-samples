def test_set_user_pool_mfa_config_nonexistent(cli, cognito, tmp_path):
    pool_name = "mfa-error-" + tmp_path.name
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    existing_pool_id = created["UserPool"]["Id"]

    region_prefix = existing_pool_id.split("_", 1)[0]
    nonexistent_pool_id = region_prefix + "_0000000000000000000000000"

    result = cli(
        "cognito-idp",
        "set-user-pool-mfa-config",
        "--user-pool-id",
        nonexistent_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": existing_pool_id},
    )
    assert described["UserPool"]["Id"] == existing_pool_id
    assert described["UserPool"]["Name"] == pool_name

    mfa_config = cognito.rpc(
        "GetUserPoolMfaConfig",
        {"UserPoolId": existing_pool_id},
    )
    assert mfa_config["MfaConfiguration"] == "OFF"