def test_create_user_pool_client_invalid_user_pool_id(cli, cognito):
    # Attempt to create an app client against a non-existent / malformed pool id.
    bogus_pool_id = "x" * 54

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", bogus_pool_id,
        "--client-name", "my-app-client",
    )

    # Must fail.
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    # Error category substring (either malformed param or missing resource).
    assert (
        "Exception" in result.stderr
        or "NotFound" in result.stderr
    )

    # Assert no such pool exists in state (nothing was created under the bogus id).
    listing = cognito.rpc("ListUserPools", {"MaxResults": 60})
    pool_ids = [p.get("Id") for p in listing.get("UserPools", [])]
    assert bogus_pool_id not in pool_ids