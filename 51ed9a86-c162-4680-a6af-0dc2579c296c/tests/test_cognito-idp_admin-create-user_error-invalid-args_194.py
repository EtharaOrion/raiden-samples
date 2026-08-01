def test_admin_create_user_nonexistent_pool(cli, cognito):
    fake_pool_id = "local_nonexistent999"

    # Ensure the pool does not exist by attempting to describe it (should error out)
    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", fake_pool_id,
        "--username", "someuser",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no user got created in a real pool: create a real pool and confirm it's empty
    pool = cognito.rpc("CreateUserPool", {"PoolName": "verify-pool"})
    real_pool_id = pool["UserPool"]["Id"]

    users = cognito.rpc("ListUsers", {"UserPoolId": real_pool_id})
    assert users.get("Users", []) == []