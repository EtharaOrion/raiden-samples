def test_list_user_pool_clients_lists_existing_clients(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-client-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    first_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "first-list-client",
        },
    )["UserPoolClient"]
    second_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "second-list-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    listed_by_cli = {
        (client["ClientId"], client["ClientName"])
        for client in output["UserPoolClients"]
    }
    expected_clients = {
        (first_client["ClientId"], first_client["ClientName"]),
        (second_client["ClientId"], second_client["ClientName"]),
    }
    assert expected_clients <= listed_by_cli

    state = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    listed_in_state = {
        (client["ClientId"], client["ClientName"])
        for client in state["UserPoolClients"]
    }
    assert expected_clients <= listed_in_state