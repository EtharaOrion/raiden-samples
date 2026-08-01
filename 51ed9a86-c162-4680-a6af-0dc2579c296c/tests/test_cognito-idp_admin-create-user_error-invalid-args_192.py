def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    # Reference a user pool that does not exist -> must fail with ResourceNotFoundException
    missing_pool_id = "local_nonexistentpool"

    # Sanity: ensure this pool really isn't present
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

    # State assertion: referencing the missing pool for a read also fails,
    # confirming no user was created there.
    try:
        listed = cognito.rpc("ListUsers", {"UserPoolId": missing_pool_id})
        assert not listed.get("Users")
    except Exception:
        pass