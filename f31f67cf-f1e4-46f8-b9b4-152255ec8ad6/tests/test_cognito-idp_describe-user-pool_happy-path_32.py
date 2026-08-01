def test_describe_user_pool_happy_path(cli, cognito, tmp_path):
    import json

    pool_name = f"describe-pool-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "describe-user-pool",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPool"]["Id"] == pool_id
    assert output["UserPool"]["Name"] == pool_name

    persisted = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert persisted["UserPool"]["Id"] == pool_id
    assert persisted["UserPool"]["Name"] == pool_name