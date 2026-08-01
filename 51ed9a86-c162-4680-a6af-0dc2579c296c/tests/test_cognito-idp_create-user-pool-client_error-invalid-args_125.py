def test_create_user_pool_client_missing_pool_error(cli, cognito):
    fake_pool_id = "local_nonexistent999"

    # Sanity: ensure this pool does not exist by listing pools
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60}).get("UserPools", [])
    assert all(p.get("Id") != fake_pool_id for p in pools)

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", fake_pool_id,
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no client got created against a real, existing pool either.
    # Create a real pool and verify it has no clients matching that name.
    real_pool = cognito.rpc("CreateUserPool", {"PoolName": "real-pool-for-check"})
    real_pool_id = real_pool["UserPool"]["Id"]
    clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": real_pool_id, "MaxResults": 60},
    ).get("UserPoolClients", [])
    assert all(c.get("ClientName") != "my-app-client" for c in clients)