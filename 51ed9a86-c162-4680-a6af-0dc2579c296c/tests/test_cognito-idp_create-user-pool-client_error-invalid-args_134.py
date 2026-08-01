def test_create_user_pool_client_invalid_user_pool(cli, cognito):
    # Use a well-formed-looking but nonexistent user pool id
    bogus_pool_id = "local_doesnotexist"

    # Sanity: ensure this pool truly doesn't exist by listing pools
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    existing_ids = {p["Id"] for p in listed.get("UserPools", [])}
    assert bogus_pool_id not in existing_ids

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", bogus_pool_id,
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no client got created against this bogus pool (still nonexistent).
    listed_after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids_after = {p["Id"] for p in listed_after.get("UserPools", [])}
    assert bogus_pool_id not in ids_after