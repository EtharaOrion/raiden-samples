def test_create_user_pool_with_mfa_on(cli, cognito, tmp_path):
    import json

    pool_name = f"pytest-mfa-on-{tmp_path.name}"[:128]

    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        pool_name,
        "--mfa-configuration",
        "ON",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    created_pool = output["UserPool"]
    pool_id = created_pool["Id"]
    assert created_pool["Name"] == pool_name
    assert isinstance(pool_id, str) and pool_id
    assert pool_id != pool_name

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name
    assert described["UserPool"]["MfaConfiguration"] == "ON"

    mfa_config = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": pool_id})
    assert mfa_config["MfaConfiguration"] == "ON"