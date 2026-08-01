def test_admin_get_user_nonexistent_user_error(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-getuser"})
    pool_id = pool["UserPool"]["Id"]

    missing_username = "x" * 123

    # ensure the user does not exist in the pool
    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id}).get("Users", [])
    assert all(u.get("Username") != missing_username for u in users)

    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", missing_username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "UserNotFoundException" in result.stderr or "NotFound" in result.stderr

    # confirm state unchanged: user still not present
    users_after = cognito.rpc("ListUsers", {"UserPoolId": pool_id}).get("Users", [])
    assert all(u.get("Username") != missing_username for u in users_after)