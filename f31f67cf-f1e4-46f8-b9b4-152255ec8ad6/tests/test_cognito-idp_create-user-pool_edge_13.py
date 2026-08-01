def test_create_user_pool_with_optional_mfa(cli, cognito, tmp_path):
    import json
    import uuid

    pool_name = f"edge-optional-mfa-{uuid.uuid4().hex}"

    before = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(pool.get("Name") != pool_name for pool in before.get("UserPools", []))

    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        pool_name,
        "--mfa-configuration",
        "OPTIONAL",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    user_pool_id = output["UserPool"]["Id"]
    assert output["UserPool"]["Name"] == pool_name

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": user_pool_id})
    assert described["UserPool"]["Id"] == user_pool_id
    assert described["UserPool"]["Name"] == pool_name

    mfa_config = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": user_pool_id})
    assert mfa_config["MfaConfiguration"] == "OPTIONAL"