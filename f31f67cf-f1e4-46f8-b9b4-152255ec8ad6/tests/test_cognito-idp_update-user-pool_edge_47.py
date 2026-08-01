def test_update_user_pool_sets_mfa_configuration_on(cli, cognito, tmp_path):
    pool_name = "update-mfa-" + tmp_path.name
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    before = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert before["Name"] == pool_name
    assert before.get("MfaConfiguration") != "ON"

    result = cli(
        "cognito-idp",
        "update-user-pool",
        "--user-pool-id",
        pool_id,
        "--mfa-configuration",
        "ON",
    )
    assert result.returncode == 0

    updated = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})["UserPool"]
    assert updated["Id"] == pool_id
    assert updated["Name"] == pool_name
    assert updated["MfaConfiguration"] == "ON"