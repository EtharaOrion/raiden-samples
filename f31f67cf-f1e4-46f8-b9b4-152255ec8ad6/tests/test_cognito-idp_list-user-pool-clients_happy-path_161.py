def test_list_user_pool_clients_happy_path(cli, cognito, tmp_path):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"list-clients-{suffix}"},
    )["UserPool"]
    pool_id = pool["Id"]

    expected_clients = {}
    for name in (f"web-{suffix}", f"mobile-{suffix}"):
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

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    listed_by_cli = {
        client["ClientId"]: client["ClientName"]
        for client in output["UserPoolClients"]
    }
    assert listed_by_cli == expected_clients

    service_state = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    listed_by_service = {
        client["ClientId"]: client["ClientName"]
        for client in service_state["UserPoolClients"]
    }
    assert listed_by_service == expected_clients