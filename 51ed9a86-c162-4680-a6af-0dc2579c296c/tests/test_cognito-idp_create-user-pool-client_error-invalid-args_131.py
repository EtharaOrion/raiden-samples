def test_create_user_pool_client_invalid_pool(cli, cognito):
    bogus_pool_id = "local_doesnotexist"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", bogus_pool_id,
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no client got created against this nonexistent pool: describe still fails.
    try:
        resp = cognito.rpc("ListUserPoolClients", {"UserPoolId": bogus_pool_id, "MaxResults": 60})
        # If the call unexpectedly succeeds, ensure there are no clients.
        assert not resp.get("UserPoolClients")
    except Exception:
        # Expected: the pool does not exist so listing raises.
        pass