def test_list_user_pool_clients_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "invalid-args-pool"})["UserPool"]
    pool_id = pool["Id"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "existing-client"},
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        item["ClientId"] == client["ClientId"]
        and item["ClientName"] == "existing-client"
        for item in clients
    )