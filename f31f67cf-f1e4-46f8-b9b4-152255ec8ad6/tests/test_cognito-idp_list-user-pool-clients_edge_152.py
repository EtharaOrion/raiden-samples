def test_list_user_pool_clients_max_results_one(cli, cognito, tmp_path):
    import json

    pool_name = f"pool-{tmp_path.name}"
    client_name = f"client-{tmp_path.name}"

    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": client_name},
    )["UserPoolClient"]
    client_id = client["ClientId"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
        "--max-results",
        "1",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        item["ClientId"] == client_id and item["ClientName"] == client_name
        for item in output["UserPoolClients"]
    )

    persisted_clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        item["ClientId"] == client_id and item["ClientName"] == client_name
        for item in persisted_clients
    )