def test_admin_get_user_error_nonexistent(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-error"})
    pool_id = pool["UserPool"]["Id"]

    # Verify pool exists but user does not
    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u.get("Username") != "ghost-user" for u in users.get("Users", []))

    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", "ghost-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "UserNotFoundException" in result.stderr

    # Confirm the user still does not exist after the failed call
    users_after = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u.get("Username") != "ghost-user" for u in users_after.get("Users", []))