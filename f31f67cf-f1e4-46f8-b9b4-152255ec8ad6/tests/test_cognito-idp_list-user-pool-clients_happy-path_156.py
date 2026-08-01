def test_list_user_pool_clients_returns_existing_clients(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"list-clients-pool-{suffix}"},
    )["UserPool"]
    pool_id = pool["Id"]

    expected_clients = {}
    for name in (f"web-client-{suffix}", f"mobile-client-{suffix}"):
        client = cognito.rpc(
            "CreateUserPoolClient",
            {"UserPoolId": pool_id, "ClientName": name},
        )["UserPoolClient"]
        expected_clients[client["ClientId"]] = name

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    listed_clients = {
        client["ClientId"]: client["ClientName"]
        for client in output["UserPoolClients"]
    }
    assert listed_clients == expected_clients

    persisted = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id},
    )["UserPoolClients"]
    persisted_clients = {
        client["ClientId"]: client["ClientName"]
        for client in persisted
    }
    assert persisted_clients == expected_clients