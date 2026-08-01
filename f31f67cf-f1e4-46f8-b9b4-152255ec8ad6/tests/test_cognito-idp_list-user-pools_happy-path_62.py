def test_list_user_pools_happy_path(cli, cognito):
    import json
    import uuid

    pool_name = f"list-pools-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "60",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in output["UserPools"]
    )

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name