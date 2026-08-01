def test_admin_get_user_missing_user_error(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "err-pool"})
    pool_id = pool["UserPool"]["Id"]

    # The user does not exist in this freshly created pool.
    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", "nonexistent-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "UserNotFoundException" in result.stderr

    # Confirm via state that the user really is absent.
    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u["Username"] != "nonexistent-user" for u in users.get("Users", []))