def test_admin_create_user_invalid_flag_rejected(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-invalid-flag-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", pool_id,
        "--username", "alice",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})
    assert all(u["Username"] != "alice" for u in users.get("Users", []))