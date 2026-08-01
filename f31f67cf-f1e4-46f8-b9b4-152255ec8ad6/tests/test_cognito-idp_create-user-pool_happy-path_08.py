def test_create_user_pool_happy_path(cli, cognito):
    import json

    pool_name = "string_v2"

    result = cli(
        "cognito-idp",
        "create-user-pool",
        "--pool-name",
        pool_name,
    )

    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    created_pool = output["UserPool"]
    pool_id = created_pool["Id"]

    assert created_pool["Name"] == pool_name
    assert pool_id
    assert pool_id != pool_name

    described_pool = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    assert described_pool["Id"] == pool_id
    assert described_pool["Name"] == pool_name

    listed_pools = cognito.rpc(
        "ListUserPools",
        {"MaxResults": 60},
    )["UserPools"]
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in listed_pools
    )