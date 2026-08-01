def test_admin_create_user_invalid_username_too_long(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-username-pool"})
    pool_id = pool["UserPool"]["Id"]

    long_username = "x" * 123

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", pool_id,
        "--username", long_username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u.get("Username") != long_username for u in users.get("Users", []))