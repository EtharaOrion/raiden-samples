def test_list_user_pool_clients_missing_required_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-clients-invalid-args-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "existing-client",
        },
    )["UserPoolClient"]

    result = cli("cognito-idp", "list-user-pool-clients")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool["Id"], "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        item["ClientId"] == client["ClientId"]
        and item["ClientName"] == "existing-client"
        for item in clients
    )