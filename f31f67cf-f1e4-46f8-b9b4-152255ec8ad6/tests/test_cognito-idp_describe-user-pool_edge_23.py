def test_describe_user_pool_existing_pool(cli, cognito, tmp_path):
    import json

    pool_name = f"describe-edge-{tmp_path.name}"
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

    observed = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert observed["UserPool"]["Id"] == pool_id
    assert observed["UserPool"]["Name"] == pool_name