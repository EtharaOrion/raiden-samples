def test_admin_create_user_nonexistent_pool_errors(cli, cognito):
    # Reference a user pool that does not exist -> ResourceNotFoundException
    missing_pool_id = "local_nonexistent999"

    # Sanity: ensure this pool id is not present
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != missing_pool_id for p in pools)

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", missing_pool_id,
        "--username", "someuser",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no user got created anywhere referencing that pool (pool truly absent)
    try:
        cognito.rpc("ListUsers", {"UserPoolId": missing_pool_id})
        listed_ok = True
    except Exception:
        listed_ok = False
    assert not listed_ok