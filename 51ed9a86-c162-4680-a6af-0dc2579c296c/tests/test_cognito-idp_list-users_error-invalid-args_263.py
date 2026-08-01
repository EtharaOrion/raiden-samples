def test_list_users_invalid_filter(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "filter-test-pool"})
    pool_id = pool["UserPool"]["Id"]

    bad_filter = "x" * 400
    result = cli(
        "cognito-idp", "list-users",
        "--user-pool-id", pool_id,
        "--filter", bad_filter,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidParameterException" in result.stderr

    # Pool still exists and is queryable normally
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert users.get("Users", []) == []