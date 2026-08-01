def test_list_users_zero_limit_succeeds(cli, cognito):
    import json

    pool_name = "list-users-zero-limit-pool"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-users",
        "--user-pool-id",
        pool_id,
        "--limit",
        "0",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Users"] == []

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert users["Users"] == []