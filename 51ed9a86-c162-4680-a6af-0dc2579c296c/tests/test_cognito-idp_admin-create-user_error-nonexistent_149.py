def test_admin_create_user_nonexistent_pool(cli, cognito):
    fake_pool_id = "local_nonexistent123"
    username = "testuser"

    # Ensure the fake pool truly does not exist by checking DescribeUserPool errors
    # (not strictly necessary, but the id is clearly a non-created one)

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", fake_pool_id,
        "--username", username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no user got created in a real (existing) pool as a sanity cross-check:
    # create a real pool and confirm it has no such user (state isolation).
    pool = cognito.rpc("CreateUserPool", {"PoolName": "assert-pool"})
    real_pool_id = pool["UserPool"]["Id"]
    listed = cognito.rpc("ListUsers", {"UserPoolId": real_pool_id})
    assert all(u.get("Username") != username for u in listed.get("Users", []))