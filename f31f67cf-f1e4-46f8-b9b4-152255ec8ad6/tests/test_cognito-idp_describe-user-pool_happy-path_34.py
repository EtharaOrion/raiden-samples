def test_describe_user_pool_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"describe-pool-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    user_pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "describe-user-pool",
        "--user-pool-id",
        user_pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPool"]["Id"] == user_pool_id
    assert output["UserPool"]["Name"] == pool_name

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": user_pool_id})
    assert described["UserPool"]["Id"] == user_pool_id
    assert described["UserPool"]["Name"] == pool_name