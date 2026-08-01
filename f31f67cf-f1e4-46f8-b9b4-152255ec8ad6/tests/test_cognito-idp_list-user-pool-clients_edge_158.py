def test_list_user_pool_clients_with_next_token(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "pool-next-token"})
    pool_id = pool["UserPool"]["Id"]

    created = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "client-next-token"},
    )
    client_id = created["UserPoolClient"]["ClientId"]

    result = cli(
        "cognito-idp",
        "list-user-pool-clients",
        "--user-pool-id",
        pool_id,
        "--next-token",
        "x",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        client["ClientId"] == client_id
        and client["ClientName"] == "client-next-token"
        for client in output["UserPoolClients"]
    )

    state = cognito.rpc("ListUserPoolClients", {"UserPoolId": pool_id})
    assert any(
        client["ClientId"] == client_id
        and client["ClientName"] == "client-next-token"
        for client in state["UserPoolClients"]
    )