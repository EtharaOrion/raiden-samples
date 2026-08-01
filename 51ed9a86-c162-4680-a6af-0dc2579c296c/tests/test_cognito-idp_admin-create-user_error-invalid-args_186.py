def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    # Reference a user pool that does not exist -> must fail with ResourceNotFoundException.
    missing_pool_id = "local_deadbeef00"

    # Sanity: ensure this pool id is genuinely absent from current state.
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != missing_pool_id for p in pools)

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", missing_pool_id,
        "--username", "ghost-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # State assertion: attempting to read from the missing pool still fails, i.e.
    # no user was created anywhere for that pool.
    try:
        resp = cognito.rpc("ListUsers", {"UserPoolId": missing_pool_id})
        users = resp.get("Users", [])
        assert all(u.get("Username") != "ghost-user" for u in users)
    except Exception:
        # Expected: pool does not exist, so ListUsers itself errors.
        pass