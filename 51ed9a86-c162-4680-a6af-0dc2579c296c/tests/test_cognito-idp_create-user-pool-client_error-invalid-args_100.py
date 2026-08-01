def test_create_user_pool_client_missing_user_pool_id(cli, cognito):
    # Seed a valid pool so the only problem is the missing required --user-pool-id
    pool = cognito.rpc("CreateUserPool", {"PoolName": "seed-pool"})
    pool_id = pool["UserPool"]["Id"]

    # Invoke create-user-pool-client WITHOUT the required --user-pool-id
    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--client-name", "my-app-client",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "user-pool-id" in result.stderr.lower() or "UserPoolId" in result.stderr

    # Assert no client was created in the seeded pool
    clients = cognito.rpc("ListUserPoolClients", {"UserPoolId": pool_id, "MaxResults": 60})
    names = [c.get("ClientName") for c in clients.get("UserPoolClients", [])]
    assert "my-app-client" not in names