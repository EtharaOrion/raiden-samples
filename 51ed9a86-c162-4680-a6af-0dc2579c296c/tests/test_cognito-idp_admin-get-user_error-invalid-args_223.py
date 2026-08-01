def test_admin_get_user_missing_user_error(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-agu-err"})
    pool_id = pool["UserPool"]["Id"]

    # Sanity: the pool has no users yet
    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert users.get("Users", []) == []

    result = cli(
        "cognito-idp",
        "admin-get-user",
        "--user-pool-id",
        pool_id,
        "--username",
        "nonexistent-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "UserNotFoundException" in result.stderr

    # Confirm the user still does not exist in state
    users_after = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u.get("Username") != "nonexistent-user" for u in users_after.get("Users", []))