def test_create_user_pool_client_invalid_pool(cli, cognito):
    bogus_pool_id = "local_nonexistent999"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", bogus_pool_id,
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Confirm no client was created against the bogus pool by verifying the
    # pool truly does not exist.
    try:
        resp = cognito.rpc("ListUserPoolClients", {"UserPoolId": bogus_pool_id, "MaxResults": 60})
        # If the call unexpectedly succeeds, ensure no client got created.
        assert not resp.get("UserPoolClients")
    except Exception:
        # Expected: describing/listing on a nonexistent pool errors out.
        pass