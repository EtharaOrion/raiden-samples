def test_list_user_pool_clients_existing_pool(cli, cognito):
    import json

    pool_name = "list-clients-edge-pool"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    client_name = "list-clients-edge-client"
    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": client_name},
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    listed_output = {
        (item["ClientId"], item["ClientName"])
        for item in output["UserPoolClients"]
    }
    assert (client_id, client_name) in listed_output

    state = cognito.rpc("ListUserPoolClients", {"UserPoolId": pool_id})
    listed_state = {
        (item["ClientId"], item["ClientName"])
        for item in state["UserPoolClients"]
    }
    assert (client_id, client_name) in listed_state