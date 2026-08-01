def test_list_users_empty_user_pool(cli, cognito, tmp_path):
    import json

    pool_name = f"list-users-empty-{tmp_path.name}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-users",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output.get("Users") == []

    listed = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert listed.get("Users") == []

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name