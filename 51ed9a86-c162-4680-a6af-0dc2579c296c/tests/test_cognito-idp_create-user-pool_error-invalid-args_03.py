def test_create_user_pool_invalid_args(cli, cognito):
    pool_name = "invalid-flag-pool-xyz"

    result = cli(
        "cognito-idp", "create-user-pool",
        "--pool-name", pool_name,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    # Ensure the pool was NOT created due to the invalid invocation.
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Name") != pool_name for p in pools)