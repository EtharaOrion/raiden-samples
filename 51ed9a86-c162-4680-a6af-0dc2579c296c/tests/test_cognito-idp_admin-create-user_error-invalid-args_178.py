def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    # Use a well-formed but non-existent pool id so the operation fails.
    missing_pool_id = "local_deadbeef99"

    # Sanity: ensure this pool truly does not exist.
    try:
        cognito.rpc("DescribeUserPool", {"UserPoolId": missing_pool_id})
        pool_exists = True
    except Exception:
        pool_exists = False
    assert not pool_exists

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", missing_pool_id,
        "--username", "someuser",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no user was created anywhere referencing this pool (pool doesn't exist).
    try:
        cognito.rpc("AdminGetUser", {"UserPoolId": missing_pool_id, "Username": "someuser"})
        got_user = True
    except Exception:
        got_user = False
    assert not got_user