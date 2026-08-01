def test_create_user_pool_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"pytest-create-{uuid.uuid4().hex[:12]}"

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

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name

    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in listed["UserPools"]
    )