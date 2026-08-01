def test_list_user_pool_clients_max_results_edge(cli, cognito, tmp_path):
    import json

    suffix = "".join(character for character in tmp_path.name if character.isalnum())[-24:]
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"list-clients-edge-{suffix}"},
    )["UserPool"]
    pool_id = pool["Id"]

    first_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "edgeclientone"},
    )["UserPoolClient"]
    second_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "edgeclienttwo"},
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
        "--max-results",
        "60",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    expected_clients = {
        (first_client["ClientId"], "edgeclientone"),
        (second_client["ClientId"], "edgeclienttwo"),
    }
    output_clients = {
        (client["ClientId"], client["ClientName"])
        for client in output["UserPoolClients"]
    }
    assert expected_clients <= output_clients

    service_clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    service_client_pairs = {
        (client["ClientId"], client["ClientName"])
        for client in service_clients
    }
    assert expected_clients <= service_client_pairs

    for client_id, client_name in expected_clients:
        described = cognito.rpc(
            "DescribeUserPoolClient",
            {"UserPoolId": pool_id, "ClientId": client_id},
        )["UserPoolClient"]
        assert described["UserPoolId"] == pool_id
        assert described["ClientId"] == client_id
        assert described["ClientName"] == client_name