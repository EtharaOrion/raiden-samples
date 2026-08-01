def test_admin_get_user_missing_user_errors(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-agu-missing"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", "nonexistent-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "UserNotFoundException" in result.stderr

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u["Username"] != "nonexistent-user" for u in users.get("Users", []))