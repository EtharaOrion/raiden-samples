def test_list_user_pool_clients_happy_path(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-clients-pool"})
    pool_id = pool["UserPool"]["Id"]

    first_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "first-app-client"},
    )["UserPoolClient"]
    second_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "second-app-client"},
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
        (first_client["ClientId"], "first-app-client"),
        (second_client["ClientId"], "second-app-client"),
    }
    assert expected_clients <= listed_by_cli

    stored = cognito.rpc("ListUserPoolClients", {"UserPoolId": pool_id})
    stored_clients = {
        (client["ClientId"], client["ClientName"])
        for client in stored["UserPoolClients"]
    }
    assert expected_clients <= stored_clients