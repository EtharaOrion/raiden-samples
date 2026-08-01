def test_create_user_pool_client_invalid_user_pool_id(cli, cognito):
    # The user-pool-id is malformed/nonexistent; the create must fail.
    bogus_pool_id = "x" * 400
    client_name = "my-app-client"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", bogus_pool_id,
        "--client-name", client_name,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "InvalidParameterException" in stderr
        or "ResourceNotFoundException" in stderr
        or "ValidationException" in stderr
    )

    # Assert no such pool exists / no client was created against the bogus id.
    # ListUserPools must not contain a pool with the bogus id.
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    pool_ids = [p.get("Id") for p in listed.get("UserPools", [])]
    assert bogus_pool_id not in pool_ids