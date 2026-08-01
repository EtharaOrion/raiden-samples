def test_create_user_pool_explicit_mfa_off(cli, cognito):
    import json
    import uuid

    pool_name = f"edge-mfa-off-{uuid.uuid4().hex}"

    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        pool_name,
        "--mfa-configuration",
        "OFF",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    user_pool_id = output["UserPool"]["Id"]
    assert output["UserPool"]["Name"] == pool_name

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": user_pool_id})
    assert described["UserPool"]["Id"] == user_pool_id
    assert described["UserPool"]["Name"] == pool_name

    mfa_config = cognito.rpc("GetUserPoolMfaConfig", {"UserPoolId": user_pool_id})
    assert mfa_config["MfaConfiguration"] == "OFF"

    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(
        pool["Id"] == user_pool_id and pool["Name"] == pool_name
        for pool in listed["UserPools"]
    )