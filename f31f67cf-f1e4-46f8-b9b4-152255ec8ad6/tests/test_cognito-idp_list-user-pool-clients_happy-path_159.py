def test_list_user_pool_clients_happy_path(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-clients-test-pool"})["UserPool"]
    pool_id = pool["Id"]

    first_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "list-test-client-one"},
    )["UserPoolClient"]
    second_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "list-test-client-two"},
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    listed_by_id = {
        client["ClientId"]: client["ClientName"]
        for client in output["UserPoolClients"]
    }
    assert listed_by_id[first_client["ClientId"]] == first_client["ClientName"]
    assert listed_by_id[second_client["ClientId"]] == second_client["ClientName"]

    state = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    state_by_id = {
        client["ClientId"]: client["ClientName"]
        for client in state["UserPoolClients"]
    }
    assert state_by_id[first_client["ClientId"]] == "list-test-client-one"
    assert state_by_id[second_client["ClientId"]] == "list-test-client-two"
    assert listed_by_id == state_by_id