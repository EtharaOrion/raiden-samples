def test_create_user_pool_happy_path(cli, cognito):
    import json

    pool_name = "string_v5"
    before = cognito.rpc("ListUserPools", {"MaxResults": 60})
    existing_pool_ids = {pool["Id"] for pool in before.get("UserPools", [])}

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
    assert pool_id not in existing_pool_ids

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name