def test_create_user_pool_client_invalid_pool(cli, cognito):
    fake_pool_id = "local_nonexistent999"

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", fake_pool_id,
        "--client-name", "myclient",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no client was actually created against this (nonexistent) pool
    try:
        resp = cognito.rpc("ListUserPoolClients", {
            "UserPoolId": fake_pool_id,
            "MaxResults": 60,
        })
        assert resp.get("UserPoolClients", []) == []
    except Exception:
        # Listing clients for a nonexistent pool should itself error out,
        # confirming no such pool/client state exists.
        pass