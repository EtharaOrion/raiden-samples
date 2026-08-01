def test_admin_create_user_missing_username(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-missing-username"})
    pool_id = pool["UserPool"]["Id"]

    result = cli("cognito-idp", "admin-create-user", "--user-pool-id", pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "username" in result.stderr.lower()

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert users.get("Users", []) == []