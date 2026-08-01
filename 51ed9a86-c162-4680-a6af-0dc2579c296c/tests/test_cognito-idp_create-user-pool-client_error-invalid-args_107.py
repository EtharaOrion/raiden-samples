def test_create_user_pool_client_invalid_args(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", pool_id,
        "--client-name", "my-client",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # Assert the client was NOT created due to the invalid arg
    listing = cognito.rpc("ListUserPoolClients", {"UserPoolId": pool_id, "MaxResults": 60})
    names = [c.get("ClientName") for c in listing.get("UserPoolClients", [])]
    assert "my-client" not in names