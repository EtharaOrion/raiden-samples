def test_create_user_pool_client_invalid_user_pool(cli, cognito):
    # Use a non-existent user pool id to trigger an error
    missing_pool_id = "local_nonexistent999"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", missing_pool_id,
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "ResourceNotFoundException" in result.stderr

    # Verify no client was created / pool truly doesn't exist by listing clients
    # ListUserPoolClients on missing pool should fail; assert pool absent via ListUserPools
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    pool_ids = [p["Id"] for p in pools.get("UserPools", [])]
    assert missing_pool_id not in pool_ids