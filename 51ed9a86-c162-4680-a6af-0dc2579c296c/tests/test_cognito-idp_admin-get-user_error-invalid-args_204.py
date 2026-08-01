def test_admin_get_user_missing_username_arg(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-missing-username"})
    pool_id = pool["UserPool"]["Id"]

    result = cli("cognito-idp", "admin-get-user", "--user-pool-id", pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "username" in result.stderr.lower()

    # pool still exists and has no users (command had no effect)
    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert users.get("Users", []) == []