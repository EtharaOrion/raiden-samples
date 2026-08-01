def test_create_user_pool_client_invalid_pool(cli, cognito):
    bogus_pool_id = "local_nonexistent123"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", bogus_pool_id,
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Verify no such pool exists so no client could have been created
    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    assert all(p.get("Id") != bogus_pool_id for p in pools.get("UserPools", []))