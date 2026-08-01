def test_list_user_pool_clients_rejects_unknown_attribute_definitions(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-clients-invalid-args-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "existing-client",
        },
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        client["ClientId"] == client_id
        and client["ClientName"] == "existing-client"
        for client in clients
    )