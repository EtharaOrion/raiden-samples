def test_list_users_accepts_maximum_limit(cli, cognito, tmp_path):
    import json
    import uuid

    pool_name = f"list-users-limit-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-users",
        "--user-pool-id",
        pool_id,
        "--limit",
        "60",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["Users"] == []

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == pool_name

    state = cognito.rpc("ListUsers", {"UserPoolId": pool_id, "Limit": 60})
    assert state["Users"] == []