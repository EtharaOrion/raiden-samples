def test_create_user_pool_client_nonexistent_pool(cli, cognito):
    # Use a syntactically plausible but nonexistent user pool id.
    fake_pool_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", fake_pool_id,
        "--client-name", "edge-client",
    )

    assert result.returncode != 0
    assert "NotFound" in result.stderr or "ResourceNotFoundException" in result.stderr

    # Assert no client got created against any real pool for this fake id
    # (the pool simply does not exist).
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(p["Id"] != fake_pool_id for p in pools.get("UserPools", []))