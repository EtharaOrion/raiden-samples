def test_list_user_pool_clients_without_optional_limit(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-clients-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    first_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "list-clients-first",
        },
    )["UserPoolClient"]
    second_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "list-clients-second",
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
    listed_by_id = {
        client["ClientId"]: client for client in output["UserPoolClients"]
    }
    assert set(listed_by_id) == {
        first_client["ClientId"],
        second_client["ClientId"],
    }
    assert listed_by_id[first_client["ClientId"]]["ClientName"] == "list-clients-first"
    assert listed_by_id[second_client["ClientId"]]["ClientName"] == "list-clients-second"

    persisted = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert {
        (client["ClientId"], client["ClientName"]) for client in persisted
    } == {
        (first_client["ClientId"], "list-clients-first"),
        (second_client["ClientId"], "list-clients-second"),
    }