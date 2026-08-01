def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    real_pool_id = pool["UserPool"]["Id"]

    missing_pool_id = "local_deadbeef00"

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", missing_pool_id,
        "--username", "ghostuser",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no such user leaked into the real (seed) pool
    users = cognito.rpc("ListUsers", {"UserPoolId": real_pool_id})
    assert all(u.get("Username") != "ghostuser" for u in users.get("Users", []))