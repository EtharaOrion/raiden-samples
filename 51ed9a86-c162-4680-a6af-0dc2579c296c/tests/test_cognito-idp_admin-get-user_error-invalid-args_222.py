def test_admin_get_user_nonexistent_user_errors(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-agu"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", pool_id,
        "--username", "no-such-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "Exception" in result.stderr

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u["Username"] != "no-such-user" for u in users.get("Users", []))