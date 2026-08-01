def test_list_user_pools_unknown_flag_rejected(cli, cognito):
    # Seed a pool so ListUserPools would have real state to return on success.
    created = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    pool_id = created["UserPool"]["Id"]

    # Invoke with an unknown flag -> must be rejected by argument parsing.
    result = cli(
        "cognito-idp", "list-user-pools",
        "--max-results", "10",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown option" in result.stderr

    # State unaffected: the seeded pool still exists.
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert any(p["Id"] == pool_id for p in listed.get("UserPools", []))