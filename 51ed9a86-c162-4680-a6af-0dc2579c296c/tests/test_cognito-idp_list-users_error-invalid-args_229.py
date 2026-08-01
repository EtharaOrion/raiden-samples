def test_list_users_missing_required_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli("cognito-idp", "list-users")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "user-pool-id" in result.stderr.lower()

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert users.get("Users", []) == []